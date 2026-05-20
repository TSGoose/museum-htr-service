from fastapi import APIRouter

from app.ocr.evaluation.metrics import calculate_cer, calculate_wer
from app.schemas.evaluation import EvaluationRequest, EvaluationResponse

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post("/calculate", response_model=EvaluationResponse)
def calculate(payload: EvaluationRequest) -> EvaluationResponse:
    return EvaluationResponse(
        cer=calculate_cer(payload.prediction, payload.ground_truth),
        wer=calculate_wer(payload.prediction, payload.ground_truth),
    )
