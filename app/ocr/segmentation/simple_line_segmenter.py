from pathlib import Path

from PIL import Image, ImageOps

from app.core.config import get_settings
from app.ocr.pipeline.result import TextLine


class SimpleLineSegmenter:
    name = "simple_line_projection"
    model_name = "pil-horizontal-projection"

    def segment(self, image_path: Path) -> list[TextLine]:
        settings = get_settings()
        crop_dir = image_path.parent / "line_crops" / image_path.stem
        crop_dir.mkdir(parents=True, exist_ok=True)

        with Image.open(image_path) as img:
            rgb = img.convert("RGB")
            gray = ImageOps.grayscale(rgb)
            width, height = gray.size
            pixels = gray.load()

            row_scores: list[float] = []
            for y in range(height):
                dark = 0
                for x in range(width):
                    if pixels[x, y] < 210:
                        dark += 1
                row_scores.append(dark / max(width, 1))

            threshold = settings.ocr_simple_segmenter_min_ink_ratio
            min_height = settings.ocr_simple_segmenter_min_line_height

            ranges: list[tuple[int, int]] = []
            start: int | None = None
            for y, score in enumerate(row_scores):
                if score >= threshold and start is None:
                    start = y
                elif score < threshold and start is not None:
                    if y - start >= min_height:
                        ranges.append((start, y))
                    start = None
            if start is not None and height - start >= min_height:
                ranges.append((start, height))

            if not ranges:
                ranges = [(0, height)]

            lines: list[TextLine] = []
            for index, (y1, y2) in enumerate(ranges):
                pad = 6
                top = max(0, y1 - pad)
                bottom = min(height, y2 + pad)
                crop = rgb.crop((0, top, width, bottom))
                crop_path = crop_dir / f"{index:04d}.jpg"
                crop.save(crop_path, format="JPEG", quality=95)
                lines.append(TextLine(index=index, bbox=(0, top, width, bottom), crop_path=crop_path))

            return lines
