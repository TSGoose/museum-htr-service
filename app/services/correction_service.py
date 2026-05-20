from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.db.models import OCRCorrection
from app.db.repositories.results import ResultRepository
from app.ocr.evaluation.metrics import calculate_cer, calculate_wer
from app.ocr.training.dataset_service import TrainingDatasetService


class CorrectionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.results = ResultRepository(db)
        self.training = TrainingDatasetService(db)

    def create_correction(
        self,
        *,
        image_id: UUID,
        corrected_text: str,
        comment: str | None,
        metadata: dict,
    ) -> tuple[OCRCorrection, object]:
        result = self.results.get_latest_by_image_id(image_id)
        if result is None:
            raise not_found("OCR_RESULT_NOT_FOUND", "OCR result not found")

        image = result.image
        cer = calculate_cer(result.normalized_text, corrected_text)
        wer = calculate_wer(result.normalized_text, corrected_text)

        correction = OCRCorrection(
            image_id=image_id,
            ocr_result_id=result.id,
            raw_text=result.normalized_text,
            corrected_text=corrected_text,
            comment=comment,
            metadata_json=metadata,
            cer_before=cer,
            wer_before=wer,
        )
        image.has_correction = True
        self.db.add(correction)
        self.db.flush()

        sample = self.training.create_page_sample(image=image, result=result, correction=correction)
        self.db.commit()
        return correction, sample
