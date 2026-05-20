from app.core.config import get_settings
from app.ocr.recognition.dummy_recognizer import DummyRecognizer
from app.ocr.recognition.transformers_trocr_recognizer import TransformersTrOCRRecognizer


def create_recognizer():
    settings = get_settings()
    match settings.ocr_recognizer:
        case "dummy":
            return DummyRecognizer()
        case "transformers_trocr":
            return TransformersTrOCRRecognizer()
        case other:
            raise ValueError(f"Unsupported OCR_RECOGNIZER={other!r}")
