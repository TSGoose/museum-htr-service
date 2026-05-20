from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ImageCreateResponse(BaseModel):
    image_id: UUID
    job_id: UUID
    status: str


class OCRResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    image_id: UUID
    job_id: UUID
    status: str
    title: str
    body: str
    raw_text: str
    normalized_text: str
    confidence: float | None
    segmenter: str
    recognizer: str
    recognition_model: str
    metrics: dict
    metadata: dict
    lines: list[dict] | None = None
