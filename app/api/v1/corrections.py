from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.correction import CorrectionCreateRequest, CorrectionCreateResponse
from app.services.correction_service import CorrectionService

router = APIRouter(prefix="/images", tags=["corrections"])


@router.post("/{image_id}/correction", response_model=CorrectionCreateResponse)
def create_correction(
    image_id: UUID,
    payload: CorrectionCreateRequest,
    db: Session = Depends(get_db),
) -> CorrectionCreateResponse:
    correction, sample = CorrectionService(db).create_correction(
        image_id=image_id,
        corrected_text=payload.corrected_text,
        comment=payload.comment,
        metadata=payload.metadata,
    )
    return CorrectionCreateResponse(
        image_id=image_id,
        correction_id=correction.id,
        cer_before=correction.cer_before,
        wer_before=correction.wer_before,
        training_sample_id=sample.id,
        status="accepted",
    )
