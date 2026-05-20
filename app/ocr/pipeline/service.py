from pathlib import Path

from app.core.config import get_settings
from app.ocr.pipeline.result import PipelineResult
from app.ocr.postprocessing.default_postprocessor import DefaultPostProcessor
from app.ocr.preprocessing.default_preprocessor import DefaultPreprocessor
from app.ocr.recognition.factory import create_recognizer
from app.ocr.segmentation.factory import create_segmenter


class OCRPipelineService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.preprocessor = DefaultPreprocessor()
        self.segmenter = create_segmenter()
        self.recognizer = create_recognizer()
        self.postprocessor = DefaultPostProcessor()

    def run(self, image_path: Path) -> PipelineResult:
        processed_path = self.preprocessor.process(image_path)
        lines = self.segmenter.segment(processed_path)
        recognized_lines = self.recognizer.recognize_lines(lines)

        raw_text = "\n".join(line.text for line in recognized_lines if line.text)
        normalized_text = self.postprocessor.process(raw_text)

        confidences = [line.confidence for line in recognized_lines if line.confidence is not None]
        confidence = sum(confidences) / len(confidences) if confidences else None

        line_json = [
            {
                "index": line.index,
                "text": line.text,
                "confidence": line.confidence,
                "bbox": list(line.bbox) if line.bbox else None,
                "crop_path": str(next((src.crop_path for src in lines if src.index == line.index), "")),
            }
            for line in recognized_lines
        ]

        segmentation_json = [
            {
                "index": line.index,
                "bbox": list(line.bbox),
                "crop_path": str(line.crop_path) if line.crop_path else None,
                "baseline": line.baseline,
                "polygon": line.polygon,
            }
            for line in lines
        ]

        return PipelineResult(
            raw_text=raw_text,
            normalized_text=normalized_text,
            body=normalized_text,
            confidence=confidence,
            segmenter=self.segmenter.name,
            segmentation_model=self.segmenter.model_name,
            recognizer=self.recognizer.name,
            recognition_model=self.recognizer.model_name,
            recognition_model_version=self.recognizer.model_version,
            preprocessing_config={
                "enabled": self.settings.ocr_preprocessing_enabled,
                "max_image_side": self.settings.ocr_max_image_side,
            },
            recognition_config={
                "pipeline": self.settings.ocr_pipeline,
                "segmenter": self.settings.ocr_segmenter,
                "recognizer": self.settings.ocr_recognizer,
            },
            result_json={
                "processed_image_path": str(processed_path),
                "segmentation": segmentation_json,
                "lines": line_json,
            },
        )
