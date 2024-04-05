#from marker.convert import convert_single_pdf
# from marker.marker.convert import convert_single_pdf
from marker.models import load_all_models
from pathlib import Path
default_out_dir=Path.cwd() / "output"

class PDFExtract():
    def __init__(self,doc_path: Path, output_dir: Path=default_out_dir, dimlimit: int = 10, relsize: float = 0.01, abssize: int = 10) -> None:
        self.dimlimit = dimlimit  # 100  # each image side must be greater than this
        self.relsize = relsize  # 0.05  # image : image size ratio must be larger than this (5%)
        self.abssize = abssize  # 2048  # absolute image size limit 2 KB: ignore if smaller
        self.output_dir = output_dir
        self.img_dir = output_dir / "images"  # found images are stored in this subfolder
        self.doc_path=doc_path
        self.image_list=list()
        load_all_models()
    
