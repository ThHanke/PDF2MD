# from marker.marker.convert import convert_single_pdf
from pathlib import Path

default_out_dir = Path.cwd() / "output"
default_model_dir = Path.cwd() / "models"

import json
import shutil, time
import io, os
import zipfile

import fitz
from ordered_set import OrderedSet
import cv2
import numpy as np

from marker.postprocessors.t5 import T5ForTokenClassification
from transformers import (
    LayoutLMv3ForSequenceClassification,
    LayoutLMv3ForTokenClassification,
)
from texify.model.model import load_model

from marker.convert import convert_single_pdf
from marker.settings import Settings as marker_Settings

marker_settings = marker_Settings(TORCH_DEVICE="cpu")
# marker_settings.ENABLE_EDITOR_MODEL=True
# marker_settings.DEBUG=True
# marker_settings.BAD_SPAN_TYPES = ["Caption", "Footnote", "Page-footer", "Page-header"]
print(marker_settings)


def load_all_models(marker_settings):
    local_edit_model = default_model_dir / "edit"
    local_order_model = default_model_dir / "column_detector"
    local_layout_model = default_model_dir / "layout_segmenter"
    local_equation_model = default_model_dir / "texify"
    if local_edit_model.is_dir():
        edit_model = local_edit_model
    else:
        edit_model = marker_settings.EDITOR_MODEL_NAME
    edit = T5ForTokenClassification.from_pretrained(
        edit_model,
        torch_dtype=marker_settings.MODEL_DTYPE,
    ).to(marker_settings.TORCH_DEVICE_MODEL)
    edit.eval()
    edit.config.label2id = {
        "equal": 0,
        "delete": 1,
        "newline-1": 2,
        "space-1": 3,
    }
    edit.config.id2label = {v: k for k, v in edit.config.label2id.items()}
    if local_order_model.is_dir():
        order_model = local_order_model
    else:
        order_model = marker_settings.ORDERER_MODEL_NAME
    order = LayoutLMv3ForSequenceClassification.from_pretrained(
        order_model,
        torch_dtype=marker_settings.MODEL_DTYPE,
    ).to(marker_settings.TORCH_DEVICE_MODEL)
    order.eval()
    if local_layout_model.is_dir():
        layout_model = local_layout_model
    else:
        layout_model = marker_settings.LAYOUT_MODEL_NAME
    layout = LayoutLMv3ForTokenClassification.from_pretrained(
        layout_model,
        torch_dtype=marker_settings.MODEL_DTYPE,
    ).to(marker_settings.TORCH_DEVICE_MODEL)
    layout.config.id2label = {
        0: "Caption",
        1: "Footnote",
        2: "Formula",
        3: "List-item",
        4: "Page-footer",
        5: "Page-header",
        6: "Picture",
        7: "Section-header",
        8: "Table",
        9: "Text",
        10: "Title",
    }
    layout.config.label2id = {v: k for k, v in layout.config.id2label.items()}
    local_equation_model
    if local_equation_model.is_dir():
        equation_model = local_equation_model
    else:
        equation_model = marker_settings.TEXIFY_MODEL_NAME
    equation = load_model(
        checkpoint=equation_model,
        device=marker_settings.TORCH_DEVICE_MODEL,
        dtype=marker_settings.TEXIFY_DTYPE,
    )
    return [equation, layout, order, edit]


# global_models = load_all_models(marker_settings)
# download model if necessary
def check_or_download_models(models_list):
    for model in models_list:
        if model:
            model_name = model.config.name_or_path.split("/")[
                -1
            ]  # extract the model name from its config
            model_path = default_model_dir / model_name
            if not model_path.is_dir():
                print("saving model {} to {}".format(model_name, model_path))
                # needed because of https://github.com/huggingface/transformers/issues/27293
                model.save_pretrained(model_path.as_posix(), safe_serialization=False)
                # model.save_pretrained(model_path.as_posix())


class PDFExtract:
    def __init__(
        self,
        doc_path: Path,
        output_dir: Path = default_out_dir,
        dimlimit: int = 10,
        relsize: float = 0.01,
        abssize: int = 10,
    ) -> None:
        self.dimlimit = dimlimit  # 100  # each image side must be greater than this
        self.relsize = (
            relsize  # 0.05  # image : image size ratio must be larger than this (5%)
        )
        self.abssize = (
            abssize  # 2048  # absolute image size limit 2 KB: ignore if smaller
        )
        self.outname = doc_path.stem
        # shorten th name if necessarry
        self.outname = (self.outname[:50]) if len(self.outname) > 50 else self.outname
        self.out_dir = output_dir / self.outname
        filename = self.outname + ".md"
        self.out_file = self.out_dir / filename
        self.img_dir = (
            self.out_dir / "images"
        )  # found images are stored in this subfolder
        self.img_dir.mkdir(parents=True, exist_ok=True)
        self.doc_path = doc_path
        self.image_list = list()
        self.model_lst = load_all_models(marker_settings)
        check_or_download_models(self.model_lst)
        self.page_count = None

    def extract_text(self):
        full_text, out_meta = convert_single_pdf(
            self.doc_path.as_posix(),
            self.model_lst,
            max_pages=None,
            parallel_factor=2,
            metadata={},
        )
        with open(self.out_file, "w+", encoding="utf-8") as f:
            f.write(full_text)
        outname = self.outname + "_meta.json"
        with open(self.out_dir / outname, "w+") as f:
            f.write(json.dumps(out_meta, indent=4))

    def zip_results(self, delete_files=True):
        zip_file_buffer = zip_folder(self.out_dir.as_posix())
        if delete_files:
            self.doc_path.unlink()
            shutil.rmtree(self.out_dir.as_posix())
        return zip_file_buffer

    def extract_images(self):
        t0 = time.time()
        doc = fitz.open(self.doc_path)
        self.page_count = doc.page_count  # number of pages
        xreflist = []
        imglist = []
        for pno in range(self.page_count):
            # pno=6
            page = doc.load_page(pno)
            page.clean_contents()
            # Get the page size
            page_width, page_height = page.mediabox_size
            image_infos = page.get_image_info()
            page_images = []
            il = doc.get_page_images(pno)
            # imglist.extend([x[0] for x in il])
            for k, img in enumerate(il):
                # get p1 of bounding box - should be most left and top point
                xref = img[0]
                if xref in xreflist:
                    continue

                rect = page.get_image_rects(xref)[0]
                x1, y1, width, height = rect.x0, rect.y0, rect.width, rect.height
                # test if we have an image with the same bounding box already
                if any([(x1, y1, width, height) == entry[:4] for entry in page_images]):
                    continue
                # print(k,xref,x1,y1)
                if min(width, height) <= self.dimlimit:
                    continue
                image = self.recoverpix(doc, img)
                n = image["colorspace"]
                imgdata = image["image"]

                if len(imgdata) <= self.abssize:
                    continue
                if len(imgdata) / (width * height * n) <= self.relsize:
                    continue

                # Calculate the relative position
                rel_x = float(x1) / page_width
                rel_y = float(y1) / page_height

                # Calculate the overall relative position
                overall_rel_x = (pno + rel_x) / self.page_count
                overall_rel_y = (pno + rel_y) / self.page_count
                # print(pno,rel_y,page_height,overall_rel_y)

                xreflist.append(xref)
                page_images.append(
                    (
                        x1,
                        y1,
                        width,
                        height,
                        xref,
                        pno,
                        overall_rel_x,
                        overall_rel_y,
                        image["ext"],
                        imgdata,
                    )
                )
            sorted_list = sorted(page_images)
            # [print(entry[:-1]) for entry in sorted_list]
            imglist.extend(sorted_list)
            # break
        # save images to file
        for i, image in enumerate(imglist):
            xref = image[4]
            pno = image[5]
            ext = image[-2]
            x1 = image[0]
            y1 = image[1]
            orel_x = image[-4]
            orel_y = image[-3]
            imgdata = image[-1]
            image_name = "img%05ipage%iref%ix%iy%i.%s" % (i, pno, xref, x1, y1, ext)
            imgfile = self.img_dir / image_name
            fout = open(imgfile, "wb")
            fout.write(imgdata)
            fout.close()
            self.image_list.append(
                (x1, y1, image[2], image[3], xref, pno, orel_x, orel_y, ext, imgfile)
            )

        t1 = time.time()
        print(len(set(self.image_list)), "images in total")
        print(len(xreflist), "images extracted")
        print("total time %g sec" % (t1 - t0))
        # images might be slices of the original so merge them dependent on bounding rect intersections
        self.merge_images()

    def recoverpix(self, doc, item):
        xref = item[0]  # xref of PDF image
        smask = item[1]  # xref of its /SMask

        # special case: /SMask or /Mask exists
        if smask > 0:
            pix0 = fitz.Pixmap(doc.extract_image(xref)["image"])
            if pix0.alpha:  # catch irregular situation
                pix0 = fitz.Pixmap(pix0, 0)  # remove alpha channel
            mask = fitz.Pixmap(doc.extract_image(smask)["image"])

            try:
                pix = fitz.Pixmap(pix0, mask)
            except:  # fallback to original base image in case of problems
                pix = fitz.Pixmap(doc.extract_image(xref)["image"])

            if pix0.n > 3:
                ext = "pam"
            else:
                ext = "png"

            return {  # create dictionary expected by caller
                "ext": ext,
                "colorspace": pix.colorspace.n,
                "image": pix.tobytes(ext),
            }

        # special case: /ColorSpace definition exists
        # to be sure, we convert these cases to RGB PNG images
        if "/ColorSpace" in doc.xref_object(xref, compressed=True):
            pix = fitz.Pixmap(doc, xref)
            pix = fitz.Pixmap(fitz.csRGB, pix)
            return {  # create dictionary expected by caller
                "ext": "png",
                "colorspace": 3,
                "image": pix.tobytes("png"),
            }
        return doc.extract_image(xref)

    def merge_images(self):
        rects = [image_stats[:4] for image_stats in self.image_list]
        to_merge = None
        image_list = self.image_list.copy()
        for i, image_stats in enumerate(self.image_list):
            # print(i,image_stats[-1].name)
            overlapping = [
                i
                for i, rect in enumerate(rects)
                if overlapping_edge(
                    image_stats[:4], rect, tolerance=0.01, same_width=True
                )
            ]
            if not to_merge or i not in to_merge:
                if to_merge and len(to_merge) > 1:
                    # probably stack complete lets stitch together
                    merge_images_paths = [self.image_list[hit][-1] for hit in to_merge]
                    if stitch(
                        [hit.as_posix() for hit in merge_images_paths], delete=True
                    ):
                        print(
                            "merged: {}".format(
                                [self.image_list[hit][-1].name for hit in to_merge]
                            )
                        )
                        # remove images for images_list
                        image_list = [
                            entry
                            for entry in image_list
                            if entry[-1] not in merge_images_paths[1:]
                        ]
                to_merge = OrderedSet(
                    [
                        i,
                    ]
                )
            if overlapping:
                to_merge.update(overlapping)
        # update image_list
        self.image_list = image_list

    def paste_img_links_to_md(self):
        md_file = self.out_file
        with open(md_file, "r") as f:
            file_content = f.read()

            # Split the file content into blocks
            blocks = list(filter(bool, file_content.split("\n\n")))
            # Calculate the cumulative block lengths
            block_lengths = [len(block) for block in blocks]
            cumulative_lengths = [
                sum(block_lengths[: i + 1]) for i in range(len(block_lengths))
            ]
            # print([(i,block_lengths[i],cumulative_lengths[i],blocks[i][-50:]) for i in range(len(block_lengths))])
        for image_stats in self.image_list[::1]:
            imgfile = image_stats[-1]

            relative_pos = image_stats[-3]
            cumulative_pos = int(sum(block_lengths) * relative_pos)

            # Find the block where the cumulative length is just over the relative position
            insert_pos = next(
                (
                    i
                    for i, cumulative_length in enumerate(cumulative_lengths)
                    if cumulative_length > cumulative_pos
                ),
                len(blocks),
            )
            image_link = f"![{imgfile.name}]({Path(os.path.relpath(imgfile, start=md_file.parent))})\n"
            # Insert the image link at the appropriate position
            # print(relative_pos,insert_pos,image_link)
            blocks.insert(insert_pos, image_link)
        # Join the blocks back together
        new_content = "\n\n".join(blocks)
        with open(self.out_file, "w") as f:
            f.write(new_content)


def zip_folder(folder_path: str):
    # Create an in-memory byte stream
    zip_buffer = io.BytesIO()
    folder_path = Path(folder_path)
    # Create a ZipFile object with the in-memory byte stream
    with zipfile.ZipFile(zip_buffer, mode="w") as zip_file:
        # Loop through all files in the folder
        for file in folder_path.rglob("*"):
            if file.is_file():
                # Get the relative path for the file which is needed for writing into the zipfile
                relative_path = file.relative_to(folder_path)
                # Add the file to the zip archive
                zip_file.write(file, arcname=str(relative_path))
    # Reset the in-memory byte stream to the beginning
    zip_buffer.seek(0)
    return zip_buffer


def overlapping_edge(
    rect1, rect2, tolerance=1.0, same_width=False
):  # you can adjust the tolerance as needed
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2

    # Calculate the coordinates of the bottom and right edges
    x1_right = x1 + w1
    y1_bottom = y1 + h1
    x2_right = x2 + w2
    y2_bottom = y2 + h2

    # check if have same width
    if same_width:
        if abs(w1 - w2) > tolerance:
            return None
    # Check for overlapping edges
    if abs(x1_right - x2) <= tolerance and (max(y1, y2) < min(y1_bottom, y2_bottom)):
        return "right of rect1 and left of rect2"
    elif abs(x1 - x2_right) <= tolerance and (max(y1, y2) < min(y1_bottom, y2_bottom)):
        return "left of rect1 and right of rect2"
    elif abs(y1_bottom - y2) <= tolerance and (max(x1, x2) < min(x1_right, x2_right)):
        return "bottom of rect1 and top of rect2"
    elif abs(y1 - y2_bottom) <= tolerance and (max(x1, x2) < min(x1_right, x2_right)):
        return "top of rect1 and bottom of rect2"

    return None


def stitch(images, delete=True):
    stitch = None
    for i, image in enumerate(images):
        img = cv2.imread(image)

        if i == 0:
            stitched = img
            img_name = images[0]
            continue
        if img is None or stitch is None:
            continue
        if stitched.shape[1] == img.shape[1]:
            stitched = np.vstack((stitched, img))
            # delete stacked image
            if delete:
                Path(image).unlink()
        elif stitched.shape[0] == img.shape[0]:
            stitched = np.hstack((stitched, img))
            # delete stacked image
            if delete:
                Path(image).unlink()
        else:
            print("unstackable - {} width or height not the same".format(image))
            return False
    result = cv2.imwrite(img_name, stitched)
    return result
