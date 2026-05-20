from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import OCRResult


class ResultRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_latest_by_image_id(self, image_id: UUID) -> OCRResult | None:
        stmt = (
            select(OCRResult)
            .where(OCRResult.image_id == image_id)
            .order_by(OCRResult.created_at.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, **kwargs) -> OCRResult:
        result = OCRResult(**kwargs)
        self.db.add(result)
        self.db.flush()
        return result
