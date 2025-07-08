import io
import os
import shutil
import time
import zipfile
import json
from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import save_output
from marker.settings import Settings as marker_Settings
from pathlib import Path
from cross_ref import build_full_record

default_out_dir = Path.cwd() / "output"
default_model_dir = Path.cwd() / "models"

# import diskcache as dc


TORCH_DEVICE = os.getenv("TORCH_DEVICE", "cpu")
settings = marker_Settings(TORCH_DEVICE=os.getenv("TORCH_DEVICE", TORCH_DEVICE))


def load_models():
    print(settings)
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
        json_files = list(self.out_folder.glob('*.json'))
        meta_data={}
        if len(json_files) == 1:
            with open(json_files[0], 'r') as json_file:
                data = json.load(json_file)
                # Extrahieren der Titel mit heading_level == null
                titles = []
                for item in data['table_of_contents']:
                    if item['heading_level'] is None:
                        if item['title'] and len(item['title'].split())<5:
                            continue
                        # Überprüfen, ob der Titel mit einer Zahl beginnt
                        if item['title'] and item['title'][0].isdigit():
                            break
                        titles.append(item['title'])
                        
                for title in titles:
                    meta_data=build_full_record(query=title,max_depth=0)
                    if meta_data:
                        data.update(meta_data)  # Füge meta_data auf der obersten Ebene in data ein
                        break
        # Speichern des aktualisierten data-Dictionaries in dieselbe JSON-Datei
        if meta_data:
            with open(json_files[0], 'w') as json_file:  # Überschreibe die ursprüngliche Datei
                json.dump(data, json_file, indent=4)
        print(f"Saved markdown to {self.out_folder }")
        print(f"Total time: {time.time() - start}")

    def zip_results(self, delete_files=True):
        zip_file_buffer = zip_folder(self.out_folder.as_posix())
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
