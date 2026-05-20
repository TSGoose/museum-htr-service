from pydantic import BaseModel, Field


class EvaluationRequest(BaseModel):
    prediction: str = Field(default="")
    ground_truth: str = Field(default="")


class EvaluationResponse(BaseModel):
    cer: float
    wer: float
