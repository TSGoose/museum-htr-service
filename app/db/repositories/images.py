from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import Image, OCRJob


class ImageRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_image(
        self,
        *,
        title: str,
        original_filename: str,
        content_type: str,
        storage_path: str,
        checksum: str,
        file_size: int,
        metadata: dict,
    ) -> Image:
        image = Image(
            title=title,
            original_filename=original_filename,
            content_type=content_type,
            storage_path=storage_path,
            checksum=checksum,
            file_size=file_size,
            metadata_json=metadata,
        )
        self.db.add(image)
        self.db.flush()
        return image

    def get(self, image_id: UUID) -> Image | None:
        return self.db.get(Image, image_id)

    def create_job(self, image_id: UUID, max_attempts: int) -> OCRJob:
        job = OCRJob(image_id=image_id, status="queued", progress=0, max_attempts=max_attempts)
        self.db.add(job)
        self.db.flush()
        return job
