from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import OCRJob


class JobRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, job_id: UUID) -> OCRJob | None:
        return self.db.get(OCRJob, job_id)

    def set_status(
        self,
        job: OCRJob,
        *,
        status: str,
        progress: int | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
        processing_time_ms: int | None = None,
    ) -> OCRJob:
        job.status = status
        if progress is not None:
            job.progress = progress
        job.error_code = error_code
        job.error_message = error_message
        if processing_time_ms is not None:
            job.processing_time_ms = processing_time_ms
        self.db.flush()
        return job
