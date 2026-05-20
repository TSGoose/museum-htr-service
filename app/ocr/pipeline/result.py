from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TextLine:
    index: int
    bbox: tuple[int, int, int, int]
    crop_path: Path | None = None
    baseline: list[tuple[int, int]] | None = None
    polygon: list[tuple[int, int]] | None = None


@dataclass
class RecognizedLine:
    index: int
    text: str
    confidence: float | None = None
    bbox: tuple[int, int, int, int] | None = None


@dataclass
class PipelineResult:
    raw_text: str
    normalized_text: str
    body: str
    confidence: float | None
    segmenter: str
    segmentation_model: str
    recognizer: str
    recognition_model: str
    recognition_model_version: str | None
    preprocessing_config: dict[str, Any] = field(default_factory=dict)
    recognition_config: dict[str, Any] = field(default_factory=dict)
    result_json: dict[str, Any] = field(default_factory=dict)
