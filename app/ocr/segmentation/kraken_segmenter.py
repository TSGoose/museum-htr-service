from pathlib import Path
from typing import Any

from PIL import Image

from app.core.config import get_settings
from app.ocr.pipeline.result import TextLine


class KrakenSegmenter:
    name = "kraken"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.model_path = self.settings.ocr_kraken_segmentation_model_path
        self.model_name = str(self.model_path)

    def segment(self, image_path: Path) -> list[TextLine]:
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Kraken segmentation model not found: {self.model_path}. "
                "Put BLLA .mlmodel there or switch OCR_SEGMENTER=simple."
            )

        try:
            from kraken import blla
            from kraken.lib.vgsl import TorchVGSLModel
        except ImportError as exc:
            raise RuntimeError(
                "Kraken is not installed. Install OCR dependencies with "
                "`uv sync --extra ocr --group dev` or build Docker with INSTALL_OCR=true."
            ) from exc

        crop_dir = image_path.parent / "line_crops" / image_path.stem
        crop_dir.mkdir(parents=True, exist_ok=True)

        with Image.open(image_path) as img:
            rgb = img.convert("RGB")
            model = TorchVGSLModel.load_model(str(self.model_path))
            segmentation = blla.segment(rgb, model=model, device="cpu")

            raw_lines = self._extract_raw_lines(segmentation)
            lines: list[TextLine] = []
            for index, raw_line in enumerate(raw_lines):
                polygon = self._extract_polygon(raw_line)
                bbox = self._polygon_to_bbox(polygon, rgb.size)
                crop_path = self._save_crop(rgb, bbox, crop_dir, index)
                baseline = self._extract_baseline(raw_line)
                lines.append(
                    TextLine(
                        index=index,
                        bbox=bbox,
                        crop_path=crop_path,
                        baseline=baseline,
                        polygon=polygon,
                    )
                )

            if not lines:
                width, height = rgb.size
                crop_path = self._save_crop(rgb, (0, 0, width, height), crop_dir, 0)
                lines.append(TextLine(index=0, bbox=(0, 0, width, height), crop_path=crop_path))

            return lines

    def _extract_raw_lines(self, segmentation: Any) -> list[Any]:
        if isinstance(segmentation, dict):
            for key in ("lines", "text_lines", "line"):
                value = segmentation.get(key)
                if isinstance(value, list):
                    return value
        for attr in ("lines", "text_lines"):
            value = getattr(segmentation, attr, None)
            if isinstance(value, list):
                return value
        return []

    def _extract_polygon(self, raw_line: Any) -> list[tuple[int, int]] | None:
        candidates: list[Any] = []
        if isinstance(raw_line, dict):
            candidates.extend(
                raw_line.get(key)
                for key in ("boundary", "polygon", "bbox", "coords")
                if raw_line.get(key) is not None
            )
        else:
            candidates.extend(
                getattr(raw_line, key, None)
                for key in ("boundary", "polygon", "bbox", "coords")
                if getattr(raw_line, key, None) is not None
            )

        for candidate in candidates:
            polygon = self._normalize_polygon(candidate)
            if polygon:
                return polygon
        return None

    def _extract_baseline(self, raw_line: Any) -> list[tuple[int, int]] | None:
        value = raw_line.get("baseline") if isinstance(raw_line, dict) else getattr(raw_line, "baseline", None)
        return self._normalize_polygon(value)

    def _normalize_polygon(self, value: Any) -> list[tuple[int, int]] | None:
        if value is None:
            return None

        if (
            isinstance(value, (list, tuple))
            and len(value) == 4
            and all(isinstance(v, (int, float)) for v in value)
        ):
            x1, y1, x2, y2 = [int(v) for v in value]
            return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

        points: list[tuple[int, int]] = []
        if isinstance(value, (list, tuple)):
            for item in value:
                if (
                    isinstance(item, (list, tuple))
                    and len(item) >= 2
                    and isinstance(item[0], (int, float))
                    and isinstance(item[1], (int, float))
                ):
                    points.append((int(item[0]), int(item[1])))
        return points or None

    def _polygon_to_bbox(
        self,
        polygon: list[tuple[int, int]] | None,
        image_size: tuple[int, int],
    ) -> tuple[int, int, int, int]:
        width, height = image_size
        if not polygon:
            return (0, 0, width, height)

        xs = [p[0] for p in polygon]
        ys = [p[1] for p in polygon]
        pad = 8
        x1 = max(0, min(xs) - pad)
        y1 = max(0, min(ys) - pad)
        x2 = min(width, max(xs) + pad)
        y2 = min(height, max(ys) + pad)
        return (x1, y1, x2, y2)

    def _save_crop(
        self,
        image: Image.Image,
        bbox: tuple[int, int, int, int],
        crop_dir: Path,
        index: int,
    ) -> Path:
        crop_path = crop_dir / f"{index:04d}.jpg"
        image.crop(bbox).save(crop_path, format="JPEG", quality=95)
        return crop_path
