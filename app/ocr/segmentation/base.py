from pathlib import Path
from typing import Protocol

from app.ocr.pipeline.result import TextLine


class Segmenter(Protocol):
    name: str
    model_name: str

    def segment(self, image_path: Path) -> list[TextLine]:
        ...
