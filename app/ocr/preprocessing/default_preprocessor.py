from pathlib import Path

from PIL import Image

from app.core.config import get_settings


class DefaultPreprocessor:
    def process(self, image_path: Path) -> Path:
        settings = get_settings()
        if not settings.ocr_preprocessing_enabled:
            return image_path

        processed_dir = image_path.parent / "preprocessed"
        processed_dir.mkdir(parents=True, exist_ok=True)
        processed_path = processed_dir / image_path.name

        with Image.open(image_path) as img:
            img = img.convert("RGB")
            max_side = settings.ocr_max_image_side
            width, height = img.size
            if max(width, height) > max_side:
                scale = max_side / max(width, height)
                img = img.resize((int(width * scale), int(height * scale)))
            img.save(processed_path, format="JPEG", quality=95)

        return processed_path
