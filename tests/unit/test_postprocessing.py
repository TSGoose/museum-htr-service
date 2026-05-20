from app.ocr.postprocessing.default_postprocessor import DefaultPostProcessor


def test_postprocessor_normalizes_spaces() -> None:
    result = DefaultPostProcessor().process("abc   def\n\n\nxyz")
    assert result == "abc def\n\nxyz"
