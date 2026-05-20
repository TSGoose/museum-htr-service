from jiwer import wer as jiwer_wer
from rapidfuzz.distance import Levenshtein


def calculate_cer(prediction: str, ground_truth: str) -> float:
    if not ground_truth:
        return 0.0 if not prediction else 1.0
    return Levenshtein.distance(prediction, ground_truth) / len(ground_truth)


def calculate_wer(prediction: str, ground_truth: str) -> float:
    if not ground_truth.strip():
        return 0.0 if not prediction.strip() else 1.0
    return float(jiwer_wer(ground_truth, prediction))
