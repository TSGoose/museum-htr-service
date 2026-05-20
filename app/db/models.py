from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Image(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "images"

    title: Mapped[str] = mapped_column(Text)
    original_filename: Mapped[str] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(String(128))
    storage_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    checksum: Mapped[str] = mapped_column(String(128), index=True)
    file_size: Mapped[int] = mapped_column(Integer)
    image_available: Mapped[bool] = mapped_column(Boolean, default=True)
    has_correction: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    jobs: Mapped[list["OCRJob"]] = relationship(back_populates="image")
    results: Mapped[list["OCRResult"]] = relationship(back_populates="image")
    corrections: Mapped[list["OCRCorrection"]] = relationship(back_populates="image")


class OCRJob(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ocr_jobs"

    image_id: Mapped[str] = mapped_column(ForeignKey("images.id"), index=True)
    status: Mapped[str] = mapped_column(String(64), default="queued", index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    attempt: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    error_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    finished_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    image: Mapped[Image] = relationship(back_populates="jobs")
    result: Mapped["OCRResult | None"] = relationship(back_populates="job")


class OCRResult(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ocr_results"

    image_id: Mapped[str] = mapped_column(ForeignKey("images.id"), index=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("ocr_jobs.id"), index=True, unique=True)

    title: Mapped[str] = mapped_column(Text)
    raw_text: Mapped[str] = mapped_column(Text)
    normalized_text: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    segmenter: Mapped[str] = mapped_column(String(128))
    segmentation_model: Mapped[str] = mapped_column(Text)

    recognizer: Mapped[str] = mapped_column(String(128))
    recognition_model: Mapped[str] = mapped_column(Text)
    recognition_model_version: Mapped[str | None] = mapped_column(Text, nullable=True)

    preprocessing_config: Mapped[dict] = mapped_column(JSONB, default=dict)
    recognition_config: Mapped[dict] = mapped_column(JSONB, default=dict)
    result_json: Mapped[dict] = mapped_column(JSONB, default=dict)

    image: Mapped[Image] = relationship(back_populates="results")
    job: Mapped[OCRJob] = relationship(back_populates="result")
    corrections: Mapped[list["OCRCorrection"]] = relationship(back_populates="ocr_result")


class OCRCorrection(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ocr_corrections"

    image_id: Mapped[str] = mapped_column(ForeignKey("images.id"), index=True)
    ocr_result_id: Mapped[str] = mapped_column(ForeignKey("ocr_results.id"), index=True)

    raw_text: Mapped[str] = mapped_column(Text)
    corrected_text: Mapped[str] = mapped_column(Text)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    cer_before: Mapped[float | None] = mapped_column(Float, nullable=True)
    wer_before: Mapped[float | None] = mapped_column(Float, nullable=True)

    image: Mapped[Image] = relationship(back_populates="corrections")
    ocr_result: Mapped[OCRResult] = relationship(back_populates="corrections")
    training_samples: Mapped[list["TrainingSample"]] = relationship(back_populates="correction")


class TrainingSample(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "training_samples"

    image_id: Mapped[str] = mapped_column(ForeignKey("images.id"), index=True)
    ocr_result_id: Mapped[str] = mapped_column(ForeignKey("ocr_results.id"), index=True)
    correction_id: Mapped[str] = mapped_column(ForeignKey("ocr_corrections.id"), index=True)

    sample_type: Mapped[str] = mapped_column(String(64), default="page")
    status: Mapped[str] = mapped_column(String(64), default="pending")
    image_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    annotation_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    dataset_split: Mapped[str | None] = mapped_column(String(64), nullable=True)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    correction: Mapped[OCRCorrection] = relationship(back_populates="training_samples")


class OCRAttemptLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ocr_attempt_logs"

    image_id: Mapped[str] = mapped_column(ForeignKey("images.id"), index=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("ocr_jobs.id"), index=True)
    stage: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(64))
    message: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
