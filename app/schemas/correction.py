from uuid import UUID

from pydantic import BaseModel, Field


class CorrectionCreateRequest(BaseModel):
    corrected_text: str = Field(min_length=1)
    comment: str | None = None
    metadata: dict = Field(default_factory=dict)


class CorrectionCreateResponse(BaseModel):
    image_id: UUID
    correction_id: UUID
    cer_before: float | None
    wer_before: float | None
    training_sample_id: UUID
    status: str
