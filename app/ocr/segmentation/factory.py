from app.core.config import get_settings
from app.ocr.segmentation.dummy_segmenter import DummySegmenter
from app.ocr.segmentation.kraken_segmenter import KrakenSegmenter
from app.ocr.segmentation.simple_line_segmenter import SimpleLineSegmenter


def create_segmenter():
    settings = get_settings()
    match settings.ocr_segmenter:
        case "dummy":
            return DummySegmenter()
        case "simple":
            return SimpleLineSegmenter()
        case "kraken":
            return KrakenSegmenter()
        case other:
            raise ValueError(f"Unsupported OCR_SEGMENTER={other!r}")
