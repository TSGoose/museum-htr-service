from app.ocr.pipeline.result import RecognizedLine, TextLine


class DummyRecognizer:
    name = "dummy"
    model_name = "dummy-recognizer"
    model_version = "0.1.0"

    def recognize_lines(self, lines: list[TextLine]) -> list[RecognizedLine]:
        return [
            RecognizedLine(
                index=line.index,
                text="[DUMMY OCR] Здесь будет распознанный рукописный текст.",
                confidence=0.0,
                bbox=line.bbox,
            )
            for line in lines
        ]
