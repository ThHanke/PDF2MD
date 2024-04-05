from marker.convert import convert_single_pdf
# from marker.marker.convert import convert_single_pdf
from marker.models import load_all_models
from pathlib import Path
default_out_dir=Path.cwd() / "output"
import json
import shutil,time
import io, os
import zipfile

import fitz
from ordered_set import OrderedSet
import cv2
import numpy as np


class PDFExtract():
    def __init__(self, doc_path: Path, output_dir: Path=default_out_dir, dimlimit: int = 10, relsize: float = 0.01, abssize: int = 10) -> None:
        self.dimlimit = dimlimit  # 100  # each image side must be greater than this
        self.relsize = relsize  # 0.05  # image : image size ratio must be larger than this (5%)
        self.abssize = abssize  # 2048  # absolute image size limit 2 KB: ignore if smaller
        self.outname=doc_path.stem
        #shorten th name if necessarry
        self.outname = (self.outname[:50]) if len(self.outname) > 50 else self.outname
        self.out_dir=output_dir / self.outname
        self.img_dir = self.out_dir / "images"  # found images are stored in this subfolder
        self.img_dir.mkdir(parents=True, exist_ok=True)
        self.doc_path=doc_path
        self.image_list=list()
        self.model_lst = load_all_models()

    def extract_text(self):
        full_text, out_meta = convert_single_pdf(self.doc_path.as_posix(), self.model_lst, max_pages=None, parallel_factor=2,metadata={})
        outname=self.outname+".md"
        with open(self.out_dir / outname, "w+", encoding='utf-8') as f:
            f.write(full_text)
        outname=self.outname+"_meta.json"
        with open(self.out_dir / outname, "w+") as f:
            f.write(json.dumps(out_meta, indent=4))
    def zip_results(self):
        zip_file_buffer = zip_folder(self.out_dir.as_posix())
        self.doc_path.unlink()
        shutil.rmtree(self.out_dir.as_posix())
        return zip_file_buffer
    def extract_images(self):
        t0 = time.time()
        doc=fitz.open(self.doc_path)
        page_count = doc.page_count  # number of pages
        xreflist = []
        imglist = []
        for pno in range(page_count):
            #pno=6
            page = doc.load_page(pno)
            page.clean_contents()
            image_infos=page.get_image_info()
            page_images=[]
            il = doc.get_page_images(pno)
            #imglist.extend([x[0] for x in il])
            for k, img in enumerate(il):
                #get p1 of bounding box - should be most left and top point
                xref = img[0]
                if xref in xreflist:
                    continue
                
                rect=page.get_image_rects(xref)[0]
                x1,y1,width,height=rect.x0,rect.y0,rect.width,rect.height
                #test if we have an image with the same bounding box already
                if any([(x1,y1,width,height)==entry[:4] for entry in page_images]):
                    continue
                #print(k,xref,x1,y1)
                if min(width, height) <= self.dimlimit:
                    continue
                image = self.recoverpix(doc, img)
                n = image["colorspace"]
                imgdata = image["image"]

                if len(imgdata) <= self.abssize:
                    continue
                if len(imgdata) / (width * height * n) <= self.relsize:
                    continue
                
                xreflist.append(xref)
                page_images.append((x1,y1,width,height,xref,pno,image["ext"],imgdata))
            sorted_list = sorted(page_images)
            #[print(entry[:-1]) for entry in sorted_list]
            imglist.extend(sorted_list)
            #break
        #save images to file
        for i,image in enumerate(imglist):
            xref=image[4]
            pno=image[5]
            ext=image[6]
            x1=image[0]
            y1=image[1]
            imgdata=image[-1]
            image_name="img%05ipage%iref%ix%iy%i.%s" % (i, pno, xref, x1, y1,ext)
            imgfile = self.img_dir / image_name
            fout = open(imgfile, "wb")
            fout.write(imgdata)
            fout.close()
            self.image_list.append((x1,y1,image[2],image[3],xref,pno,ext,imgfile))
                
        t1 = time.time()
        print(len(set(self.image_list)), "images in total")
        print(len(xreflist), "images extracted")
        print("total time %g sec" % (t1 - t0))
        #images might be slices of the original so merge them dependent on bounding rect intersections
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
        rects=[image_stats[:4] for image_stats in self.image_list]
        to_merge=None
        for i, image_stats in enumerate(self.image_list):
            #print(i,image_stats[-1].name)
            overlapping=[i for i, rect in enumerate(rects) if overlapping_edge(image_stats[:4],rect,tolerance=0.01,same_width=True)]
            if not to_merge or i not in to_merge:
                if to_merge and len(to_merge)>1:
                    #probably stack complete lets stitch together
                    #print([self.image_list[hit][-1].name for hit in to_merge])
                    if stitch([self.image_list[hit][-1].as_posix() for hit in to_merge],delete=True):
                        print("merged: {}".format([self.image_list[hit][-1].name for hit in to_merge]))
                to_merge=OrderedSet([i,])
            if overlapping:
                to_merge.update(overlapping)

def zip_folder(folder_path: str):
    # Create an in-memory byte stream
    zip_buffer = io.BytesIO()

    # Create a ZipFile object with the in-memory byte stream
    with zipfile.ZipFile(zip_buffer, mode='w') as zip_file:
        # Loop through all files in the folder
        for filename in os.listdir(folder_path):
            # Get the full file path
            file_path = os.path.join(folder_path, filename)
            # Add the file to the zip archive
            zip_file.write(file_path, arcname=filename)

    # Reset the in-memory byte stream to the beginning
    zip_buffer.seek(0)
    return zip_buffer

def overlapping_edge(rect1, rect2, tolerance=1.0, same_width=False):  # you can adjust the tolerance as needed
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2

    # Calculate the coordinates of the bottom and right edges
    x1_right = x1 + w1
    y1_bottom = y1 + h1
    x2_right = x2 + w2
    y2_bottom = y2 + h2

    #check if have same width
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

def stitch(images,delete=True):
    for i, image in enumerate(images):
        img = cv2.imread(image)
        if i==0:
            stitched = img
            img_name=images[0]
            continue
        if stitched.shape[1] == img.shape[1]:
            stitched = np.vstack((stitched, img))
            #delete stacked image
            if delete:
                Path(image).unlink()
        elif stitched.shape[0] == img.shape[0]:
            stitched = np.hstack((stitched, img))
            #delete stacked image
            if delete:
                Path(image).unlink()
        else:
            print("unstackable - {} width or height not the same".format(image))
            return False
    result = cv2.imwrite(img_name,stitched)
    return result
