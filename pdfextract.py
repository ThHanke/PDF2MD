# from marker.marker.convert import convert_single_pdf
from pathlib import Path

default_out_dir = Path.cwd() / "output"
default_model_dir = Path.cwd() / "models"

import json
import shutil
import io, re
import zipfile

from marker.convert import convert_single_pdf
from marker.settings import Settings as marker_Settings
from marker.models import load_all_models as marker_load_all_models

settings = marker_Settings(TORCH_DEVICE="cpu")
# settings.ENABLE_EDITOR_MODEL = True
# marker_settings.DEBUG=True
# marker_settings.BAD_SPAN_TYPES = ["Caption", "Footnote", "Page-footer", "Page-header"]
print(settings)
model_name_keys = [
    key
    for key in settings.dict().keys()
    if any(map(key.__contains__, ["MODEL_NAME", "MODEL_CHECKPOINT"]))
]
print(model_name_keys)
texify_folder = default_model_dir / "texify"
layout_folder = default_model_dir / "surya_layout2"
order_folder = default_model_dir / "surya_order"
# editor_folder = default_model_dir / "pdf_postprocessor_t5"
detection_folder = default_model_dir / "surya_det2"
ocr_folder = default_model_dir / "surya_rec"
setattr(settings, "TEXIFY_MODEL_NAME", texify_folder.as_posix())
setattr(settings, "LAYOUT_MODEL_CHECKPOINT", layout_folder.as_posix())
# setattr(settings, "EDITOR_MODEL_NAME", editor_folder.as_posix())

from surya.model.detection import segformer
from surya.model.ordering.model import load_model as load_order_model
from surya.model.recognition.model import load_model as load_recognition_model
from surya.model.ordering.processor import load_processor as load_order_processor
from surya.model.recognition.processor import SuryaImageProcessor
from surya.model.recognition.tokenizer import Byt5LangTokenizer

from transformers import DonutProcessor, AutoImageProcessor
from texify.model.model import load_model as load_texify_model

from texify.model.processor import (
    VariableDonutProcessor,
    IMAGE_STD,
    IMAGE_MEAN,
    VariableDonutImageProcessor,
)
from texify.model.config import VariableDonutSwinConfig


class CustomSuryaProcessor(DonutProcessor):
    def __init__(self, checkpoint=None, tokenizer=None, train=False, **kwargs):
        if checkpoint is None:
            image_processor = SuryaImageProcessor.from_pretrained(
                settings.RECOGNITION_MODEL_CHECKPOINT
            )
        else:
            image_processor = SuryaImageProcessor.from_pretrained(checkpoint)
        if tokenizer is None:
            tokenizer = Byt5LangTokenizer()

        super().__init__(image_processor, tokenizer)
        self.current_processor = self.image_processor
        self._in_target_context_manager = False

    def __call__(self, *args, **kwargs):
        images = kwargs.pop("images", None)
        text = kwargs.pop("text", None)
        lang = kwargs.pop("lang", None)

        if len(args) > 0:
            images = args[0]
            args = args[1:]

        if images is None and text is None:
            raise ValueError(
                "You need to specify either an `images` or `text` input to process."
            )

        if images is not None:
            inputs = self.image_processor(images, *args, **kwargs)

        if text is not None:
            encodings = self.tokenizer(text, lang, **kwargs)

        if text is None:
            return inputs
        elif images is None:
            return encodings
        else:
            inputs["labels"] = encodings["input_ids"]
            inputs["langs"] = encodings["langs"]
            return inputs


def load_all_models(settings):
    print("try to load all models")
    detection = segformer.load_model(
        checkpoint=detection_folder.as_posix(),
        device=settings.TORCH_DEVICE,
        dtype=settings.MODEL_DTYPE,
    )
    detection.processor = segformer.load_processor(
        checkpoint=(detection_folder).as_posix()
    )
    layout = segformer.load_model(
        checkpoint=layout_folder.as_posix(),
        device=settings.TORCH_DEVICE,
        dtype=settings.MODEL_DTYPE,
    )
    layout.processor = segformer.load_processor(checkpoint=(layout_folder).as_posix())
    order = load_order_model(checkpoint=order_folder.as_posix())
    order.processor = load_order_processor(checkpoint=(order_folder).as_posix())
    ocr = load_recognition_model(checkpoint=ocr_folder.as_posix())
    processor = CustomSuryaProcessor(checkpoint=ocr_folder.as_posix())
    processor.image_processor.train = False
    processor.image_processor.max_size = {"height": 196, "width": 896}
    processor.tokenizer.model_max_length = 175
    ocr.processor = processor
    edit = None
    # texify = AutoModel.from_pretrained(texify_folder.as_posix())
    texify = load_texify_model(checkpoint=texify_folder.as_posix())
    # texify.processor = load_texify_processor(checkpoint=(texify_folder).as_posix())
    # tokenizer = AutoTokenizer.from_pretrained(texify_folder.as_posix())
    # image_processor=
    AutoImageProcessor.register(VariableDonutSwinConfig, VariableDonutImageProcessor)
    # processor = VariableDonutProcessor(texify_folder.as_posix(), tokenizer=tokenizer)
    processor = VariableDonutProcessor.from_pretrained(texify_folder.as_posix())
    processor.image_processor.max_size = {"height": 420, "width": 420}
    processor.image_processor.size = [420, 420]
    processor.image_processor.image_mean = IMAGE_MEAN
    processor.image_processor.image_std = IMAGE_STD
    texify.processor = processor

    model_lst = [texify, layout, order, edit, detection, ocr]
    # local_edit_model = default_model_dir / "edit"
    # if local_edit_model.is_dir():
    #     edit_model = local_edit_model
    # else:
    #     edit_model = marker_settings.EDITOR_MODEL_NAME
    # edit = T5ForTokenClassification.from_pretrained(
    #     edit_model,
    #     torch_dtype=marker_settings.MODEL_DTYPE,
    # ).to(marker_settings.TORCH_DEVICE_MODEL)
    # edit.eval()
    # edit.config.label2id = {
    #     "equal": 0,
    #     "delete": 1,
    #     "newline-1": 2,
    #     "space-1": 3,
    # }
    # edit.config.id2label = {v: k for k, v in edit.config.label2id.items()}
    return model_lst


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
                try:
                    # processorpath = model_path / "processor"
                    processorpath = model_path
                    model.processor.save_pretrained(
                        processorpath.as_posix(), safe_serialization=False
                    )
                except e:
                    print(e)
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
        # self.model_lst = marker_load_all_models(settings)
        self.model_lst = load_all_models(settings)
        check_or_download_models(self.model_lst)
        self.page_count = None

    def extract(self):
        full_text, doc_images, out_meta = convert_single_pdf(
            self.doc_path.as_posix(),
            self.model_lst,
            max_pages=None,
            langs=["English", "German"],
            metadata={},
        )
        with open(self.out_file, "w+", encoding="utf-8") as f:
            f.write(full_text)
        outname = self.outname + "_meta.json"
        with open(self.out_dir / outname, "w+") as f:
            f.write(json.dumps(out_meta, indent=4))
        for filename, image in doc_images.items():
            image.save(self.img_dir / filename)
        self.image_dict = doc_images

    def zip_results(self, delete_files=True):
        zip_file_buffer = zip_folder(self.out_dir.as_posix())
        if delete_files:
            self.doc_path.unlink()
            shutil.rmtree(self.out_dir.as_posix())
        return zip_file_buffer

    def fix_links_in_md(self):
        md_file = self.out_file
        with open(md_file, "r") as f:
            file_content = f.read()
        for image_key in self.image_dict.keys():
            file_content = re.sub(
                "{}".format(image_key), "images/{}".format(image_key), file_content
            )
        with open(md_file, "w") as f:
            f.write(file_content)


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
