from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.db.repositories.results import ResultRepository
from app.db.session import get_db
from app.schemas.image import ImageCreateResponse, OCRResultResponse
from app.services.upload_service import UploadService

router = APIRouter(prefix="/images", tags=["images"])


@router.post("", response_model=ImageCreateResponse)
async def upload_image(
    file: UploadFile = File(...),
    title: str = Form(...),
    metadata: str | None = Form(default=None),
    db: Session = Depends(get_db),
) -> ImageCreateResponse:
    image_id, job_id, status = await UploadService(db).create_image_job(
        file=file,
        title=title,
        metadata_raw=metadata,
    )
    return ImageCreateResponse(image_id=image_id, job_id=job_id, status=status)


@router.get("/{image_id}/result", response_model=OCRResultResponse)
def get_result(
    image_id: UUID,
    include_lines: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> OCRResultResponse:
    result = ResultRepository(db).get_latest_by_image_id(image_id)
    if result is None:
        raise not_found("OCR_RESULT_NOT_FOUND", "OCR result not found")

    lines = result.result_json.get("lines") if include_lines else None
    return OCRResultResponse(
        image_id=result.image_id,
        job_id=result.job_id,
        status=result.job.status,
        title=result.title,
        body=result.body,
        raw_text=result.raw_text,
        normalized_text=result.normalized_text,
        confidence=result.confidence,
        segmenter=result.segmenter,
        recognizer=result.recognizer,
        recognition_model=result.recognition_model,
        metrics={"processing_time_ms": result.job.processing_time_ms},
        metadata=result.image.metadata_json,
        lines=lines,
    )
