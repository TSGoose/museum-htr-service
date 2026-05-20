import json
import shutil
from pathlib import Path
from uuid import UUID

from app.core.config import get_settings
from app.db.models import Image, OCRCorrection, OCRResult, TrainingSample
from sqlalchemy.orm import Session


class TrainingDatasetService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def create_page_sample(
        self,
        *,
        image: Image,
        result: OCRResult,
        correction: OCRCorrection,
    ) -> TrainingSample:
        annotation_dir = self.settings.training_dir / "annotations" / "page"
        image_dir = self.settings.training_dir / "images"
        annotation_dir.mkdir(parents=True, exist_ok=True)
        image_dir.mkdir(parents=True, exist_ok=True)

        training_image_path = None
        if image.storage_path and Path(image.storage_path).exists():
            source = Path(image.storage_path)
            target = image_dir / source.name
            if source.resolve() != target.resolve():
                shutil.move(str(source), str(target))
            training_image_path = str(target)
            image.storage_path = training_image_path
            image.image_available = True

        annotation_path = annotation_dir / f"{image.id}.json"
        annotation = {
            "image_id": str(image.id),
            "title": image.title,
            "raw_text": correction.raw_text,
            "corrected_text": correction.corrected_text,
            "cer_before": correction.cer_before,
            "wer_before": correction.wer_before,
        }
        annotation_path.write_text(
            json.dumps(annotation, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        sample = TrainingSample(
            image_id=image.id,
            ocr_result_id=result.id,
            correction_id=correction.id,
            sample_type="page",
            status="pending",
            image_path=training_image_path,
            annotation_path=str(annotation_path),
            metadata_json={},
        )
        self.db.add(sample)
        self.db.flush()
        return sample
