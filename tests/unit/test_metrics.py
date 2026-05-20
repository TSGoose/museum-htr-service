from app.ocr.evaluation.metrics import calculate_cer, calculate_wer


def test_cer_exact_match() -> None:
    assert calculate_cer("abc", "abc") == 0


def test_cer_insertions() -> None:
    assert calculate_cer("abcd", "abc") > 0


def test_wer_exact_match() -> None:
    assert calculate_wer("hello world", "hello world") == 0
