from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.db.repositories.jobs import JobRepository
from app.db.session import get_db
from app.schemas.job import JobStatusResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job(job_id: UUID, db: Session = Depends(get_db)) -> JobStatusResponse:
    job = JobRepository(db).get(job_id)
    if job is None:
        raise not_found("JOB_NOT_FOUND", "Job not found")

    error = None
    if job.error_code or job.error_message:
        error = {"code": job.error_code, "message": job.error_message}

    return JobStatusResponse(
        job_id=job.id,
        image_id=job.image_id,
        status=job.status,
        progress=job.progress,
        error=error,
    )
