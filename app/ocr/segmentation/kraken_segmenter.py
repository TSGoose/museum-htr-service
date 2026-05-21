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

            try:
                segmentation = blla.segment(rgb, model=model, device="cpu")
            except TypeError:
                segmentation = blla.segment(rgb, model=model)

            raw_lines = self._extract_raw_lines(segmentation)

            fragments: list[tuple[int, int, int, int]] = []
            for raw_line in raw_lines:
                polygon = self._extract_polygon(raw_line)
                bbox = self._polygon_to_bbox(polygon, rgb.size)
                fragments.append(bbox)

            grouped_bboxes = self._group_fragments_into_lines(fragments)

            lines: list[TextLine] = []
            for index, bbox in enumerate(grouped_bboxes):
                crop_path = self._save_crop(rgb, bbox, crop_dir, index)
                lines.append(
                    TextLine(
                        index=index,
                        bbox=bbox,
                        crop_path=crop_path,
                        baseline=None,
                        polygon=None,
                    )
                )

            if not lines:
                width, height = rgb.size
                crop_path = self._save_crop(rgb, (0, 0, width, height), crop_dir, 0)
                lines.append(TextLine(index=0, bbox=(0, 0, width, height), crop_path=crop_path))

            return lines

    def _group_fragments_into_lines(
        self,
        fragments: list[tuple[int, int, int, int]],
    ) -> list[tuple[int, int, int, int]]:
        if not fragments:
            return []

        # Убираем слишком мелкий мусор.
        cleaned: list[tuple[int, int, int, int]] = []
        for x1, y1, x2, y2 in fragments:
            width = x2 - x1
            height = y2 - y1

            if width < 10:
                continue
            if height < 10:
                continue

            cleaned.append((x1, y1, x2, y2))

        if not cleaned:
            return []

        # Сортируем сверху вниз, потом слева направо.
        cleaned.sort(key=lambda b: ((b[1] + b[3]) / 2, b[0]))

        groups: list[list[tuple[int, int, int, int]]] = []

        for bbox in cleaned:
            x1, y1, x2, y2 = bbox
            cy = (y1 + y2) / 2
            height = y2 - y1

            matched_group = None
            best_distance = None

            for group in groups:
                group_y1 = min(b[1] for b in group)
                group_y2 = max(b[3] for b in group)
                group_cy = (group_y1 + group_y2) / 2
                group_height = group_y2 - group_y1

                tolerance = max(18, min(45, max(height, group_height) * 0.75))
                distance = abs(cy - group_cy)

                if distance <= tolerance:
                    if best_distance is None or distance < best_distance:
                        matched_group = group
                        best_distance = distance

            if matched_group is None:
                groups.append([bbox])
            else:
                matched_group.append(bbox)

        merged: list[tuple[int, int, int, int]] = []

        for group in groups:
            # Сортируем фрагменты внутри строки слева направо.
            group.sort(key=lambda b: b[0])

            x1 = min(b[0] for b in group)
            y1 = min(b[1] for b in group)
            x2 = max(b[2] for b in group)
            y2 = max(b[3] for b in group)

            width = x2 - x1
            height = y2 - y1

            # После группировки отбрасываем всё, что всё ещё не похоже на строку.
            if width < 80:
                continue
            if height < 15:
                continue
            if width / max(height, 1) < 2.0:
                continue

            pad_x = 12
            pad_y = 10

            merged.append(
                (
                    max(0, x1 - pad_x),
                    max(0, y1 - pad_y),
                    x2 + pad_x,
                    y2 + pad_y,
                )
            )

        # Финальная сортировка строк сверху вниз.
        merged.sort(key=lambda b: b[1])

        return merged
    
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
        width, height = image.size
        x1, y1, x2, y2 = bbox

        x1 = max(0, min(x1, width))
        y1 = max(0, min(y1, height))
        x2 = max(0, min(x2, width))
        y2 = max(0, min(y2, height))

        crop_path = crop_dir / f"{index:04d}.jpg"
        image.crop((x1, y1, x2, y2)).save(crop_path, format="JPEG", quality=95)
        return crop_path
