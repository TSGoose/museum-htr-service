from pydantic import BaseModel


class ErrorEnvelope(BaseModel):
    error: dict
