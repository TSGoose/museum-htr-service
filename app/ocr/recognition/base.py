from typing import Protocol

from app.ocr.pipeline.result import RecognizedLine, TextLine


class Recognizer(Protocol):
    name: str
    model_name: str
    model_version: str | None

    def recognize_lines(self, lines: list[TextLine]) -> list[RecognizedLine]:
        ...
