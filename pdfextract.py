from pathlib import Path

default_out_dir = Path.cwd() / "output"
default_model_dir = Path.cwd() / "models"

import shutil
import io, os
import zipfile
import time

# import diskcache as dc

from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import save_output

from marker.settings import Settings as marker_Settings

marker_settings = marker_Settings(TORCH_DEVICE=os.getenv("TORCH_DEVICE", "cpu"))


def load_models():
    return create_model_dict()


class PDFExtract:
    def __init__(
        self,
        doc_path: Path = None,
        output_dir: Path = default_out_dir,
        models: dict = {},
        dimlimit: int = 10,
        relsize: float = 0.01,
        abssize: int = 10,
    ) -> None:
        self.models = models
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
        self.doc_path = doc_path
        self.image_list = list()
        self.page_count = None

    def extract_text(self):
        if not self.models:
            models = load_models()
        else:
            models = self.models
        start = time.time()
        config_parser = ConfigParser(
            cli_options={
                "output_dir": self.out_dir.as_posix(),
                "output_format": "markdown",
            }
        )
        converter = PdfConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=models,
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer(),
        )
        rendered = converter(self.doc_path.as_posix())
        out_folder = config_parser.get_output_folder(self.doc_path.as_posix())
        self.out_folder = Path(out_folder)
        save_output(
            rendered,
            self.out_folder,
            config_parser.get_base_filename(self.doc_path.as_posix()),
        )

        print(f"Saved markdown to {self.out_folder }")
        print(f"Total time: {time.time() - start}")

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
