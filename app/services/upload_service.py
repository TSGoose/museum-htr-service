import json
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import bad_request
from app.db.repositories.images import ImageRepository
from app.services.image_storage import ImageStorageService
from app.workers.tasks import process_ocr_job


class UploadService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.storage = ImageStorageService()
        self.images = ImageRepository(db)

    async def create_image_job(
        self,
        *,
        file: UploadFile,
        title: str,
        metadata_raw: str | None,
    ) -> tuple[UUID, UUID, str]:
        if file.content_type not in {"image/jpeg", "image/jpg"}:
            raise bad_request("INVALID_FILE_TYPE", "Only JPG images are supported")

        metadata = {}
        if metadata_raw:
            try:
                metadata = json.loads(metadata_raw)
            except json.JSONDecodeError as exc:
                raise bad_request("INVALID_METADATA", "metadata must be valid JSON") from exc

        image = self.images.create_image(
            title=title,
            original_filename=file.filename or "image.jpg",
            content_type=file.content_type or "image/jpeg",
            storage_path="",
            checksum="pending",
            file_size=0,
            metadata=metadata,
        )
        path, checksum, size = await self.storage.save_upload(image_id=image.id, file=file)
        if size > self.settings.max_upload_size_bytes:
            path.unlink(missing_ok=True)
            raise bad_request("FILE_TOO_LARGE", "Uploaded file is too large")

        image.storage_path = str(path)
        image.checksum = checksum
        image.file_size = size

        job = self.images.create_job(image.id, max_attempts=self.settings.ocr_job_max_retries)
        self.db.commit()

        process_ocr_job.send(str(job.id))
        return image.id, job.id, job.status
