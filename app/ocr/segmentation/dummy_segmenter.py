from pathlib import Path

from app.ocr.pipeline.result import TextLine


class DummySegmenter:
    name = "dummy"
    model_name = "dummy-full-page"

    def segment(self, image_path: Path) -> list[TextLine]:
        # MVP scaffold: one pseudo-line representing the full page.
        return [TextLine(index=0, bbox=(0, 0, 0, 0), crop_path=image_path)]
