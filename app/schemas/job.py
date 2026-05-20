from uuid import UUID

from pydantic import BaseModel, ConfigDict


class JobStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: UUID
    image_id: UUID
    status: str
    progress: int
    error: dict | None = None
