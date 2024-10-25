# from marker.marker.convert import convert_single_pdf
from pathlib import Path
from collections import OrderedDict

default_out_dir = Path.cwd() / "output"
default_model_dir = Path.cwd() / "models"

import shutil
import io, os
import zipfile

from marker.convert import convert_single_pdf
from marker.output import save_markdown
from marker.settings import Settings as marker_Settings


marker_settings = marker_Settings(TORCH_DEVICE=os.getenv("TORCH_DEVICE", "cpu"))
# marker_settings.DEBUG=True
print(marker_settings)

from marker.models import load_all_models as marker_load_all_models

from surya.settings import settings as surya_settings
from texify.model.model import load_model as load_texify_model
from texify.model.processor import load_processor as load_texify_processor
from surya.model.detection.model import (
    load_model as load_detection_model,
    load_processor as load_detection_processor,
)

from surya.model.ordering.model import load_model as load_order_model
from surya.model.ordering.processor import load_processor as load_order_processor
from surya.model.recognition.model import load_model as load_recognition_model
from surya.model.recognition.processor import (
    load_processor as load_recognition_processor,
)
from surya.model.table_rec.model import load_model as load_table_model
from surya.model.table_rec.processor import load_processor as load_table_processor

from transformers import AutoModel


def load_all_models(marker_settings):
    model_lst = marker_load_all_models()
    return model_lst
    # models = OrderedDict()
    # models["textify"] = {"name": marker_settings.TEXIFY_MODEL_NAME}
    # models["layout"] = {"name": marker_settings.LAYOUT_MODEL_CHECKPOINT}
    # models["order"] = {"name": surya_settings.ORDER_MODEL_CHECKPOINT}
    # models["detection"] = {"name": surya_settings.DETECTOR_MODEL_CHECKPOINT}
    # models["ocr"] = {"name": surya_settings.RECOGNITION_MODEL_CHECKPOINT}
    # models["table_model"] = {"name": surya_settings.TABLE_REC_MODEL_CHECKPOINT}
    # for k, v in models.items():
    #     local_path = default_model_dir / v["name"]
    #     if local_path.is_dir():
    #         print(f"loading localy saved model at {local_path}")
    #         loc = local_path
    #     else:
    #         loc = v["name"]
    #     v["model"] = AutoModel.from_pretrained(loc)
    #     # if k == "textify":
    #     #     v["model"] = load_texify_model(loc)
    #     #     v["model"].pocessor = load_texify_processor()
    #     # elif k == "layout":
    #     #     v["model"] = load_detection_model(loc)
    #     #     v["model"].pocessor = load_detection_processor(loc)
    #     # elif k == "order":
    #     #     v["model"] = load_order_model(loc)
    #     #     v["model"].pocessor = load_order_processor(loc)
    #     # elif k == "detection":
    #     #     v["model"] = load_detection_model(loc)
    #     #     v["model"].pocessor = load_detection_processor()
    #     # elif k == "ocr":
    #     #     v["model"] = load_recognition_model(loc)
    #     #     v["model"].pocessor = load_recognition_processor()
    #     # elif k == "table_model":
    #     #     v["model"] = load_table_model(loc)
    #     #     v["model"].pocessor = load_table_processor()

    # return [v["model"] for k, v in models.items()]


# global_models = load_all_models(marker_settings)
# download model if necessary
def check_or_download_models(models_list):
    for model in models_list:
        if model:
            model_name = model.config.name_or_path.split("/")[
                -1
            ]  # extract the model name from its config
            if model_name in ["surya_rec2", "surya_tablerec"]:
                continue
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
        full_text, images, out_meta = convert_single_pdf(
            self.doc_path.as_posix(),
            self.model_lst,
            max_pages=None,
            metadata={},
        )

        if len(full_text.strip()) > 0:
            outname = self.outname + ".md"
            save_out_dir = save_markdown(
                self.out_dir, outname, full_text, images, out_meta
            )
            self.out_dir = Path(save_out_dir)
        # with open(self.out_file, "w+", encoding="utf-8") as f:
        #     f.write(full_text)
        # with open(self.out_dir / outname, "w+") as f:
        #     f.write(json.dumps(out_meta, indent=4))

    def zip_results(self, delete_files=True):
        zip_file_buffer = zip_folder(self.out_dir.as_posix())
        if delete_files:
            self.doc_path.unlink()
            shutil.rmtree(self.out_dir.as_posix())
        return zip_file_buffer


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
