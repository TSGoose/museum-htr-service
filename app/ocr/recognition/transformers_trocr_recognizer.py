from pathlib import Path

from PIL import Image

from app.core.config import get_settings
from app.ocr.pipeline.result import RecognizedLine, TextLine


class TransformersTrOCRRecognizer:
    name = "transformers_trocr"
    model_version = None

    def __init__(self) -> None:
        self.settings = get_settings()
        self.model_name = self.settings.ocr_trocr_model_name
        self.model_path = self.settings.ocr_trocr_model_path
        self.device = self.settings.ocr_trocr_device
        self.max_new_tokens = self.settings.ocr_trocr_max_new_tokens
        self._processor = None
        self._model = None
        self._torch = None

    def recognize_lines(self, lines: list[TextLine]) -> list[RecognizedLine]:
        self._ensure_loaded()

        recognized: list[RecognizedLine] = []
        for line in lines:
            if line.crop_path is None:
                recognized.append(RecognizedLine(index=line.index, text="", confidence=None, bbox=line.bbox))
                continue

            text = self._recognize_image(line.crop_path)
            recognized.append(RecognizedLine(index=line.index, text=text, confidence=None, bbox=line.bbox))

        return recognized

    def _ensure_loaded(self) -> None:
        if self._processor is not None and self._model is not None:
            return

        try:
            import torch
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
        except ImportError as exc:
            raise RuntimeError(
                "Transformers/Torch OCR dependencies are not installed. "
                "Run `uv sync --extra ocr --group dev` or build Docker with INSTALL_OCR=true."
            ) from exc

        model_source = str(self.model_path) if self.model_path.exists() else self.model_name

        local_processor_path = self.model_path / "processor"
        if local_processor_path.exists():
            processor_source = str(local_processor_path)
        else:
            processor_source = f"{self.model_name}/processor"

        self._processor = TrOCRProcessor.from_pretrained(processor_source)
        self._model = VisionEncoderDecoderModel.from_pretrained(model_source)
        self._model.to(self.device)
        self._model.eval()
        self._torch = torch

    def _recognize_image(self, image_path: Path) -> str:
        assert self._processor is not None
        assert self._model is not None
        assert self._torch is not None

        with Image.open(image_path) as img:
            image = img.convert("RGB")

        pixel_values = self._processor(images=image, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(self.device)

        with self._torch.inference_mode():
            generated_ids = self._model.generate(
                pixel_values,
                max_new_tokens=self.max_new_tokens,
            )

        text = self._processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return text.strip()
