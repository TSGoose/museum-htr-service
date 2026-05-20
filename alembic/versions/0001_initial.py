"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-20
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "images",
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("original_filename", sa.Text(), nullable=False),
        sa.Column("content_type", sa.String(length=128), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=True),
        sa.Column("checksum", sa.String(length=128), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("image_available", sa.Boolean(), nullable=False),
        sa.Column("has_correction", sa.Boolean(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_images_checksum"), "images", ["checksum"], unique=False)

    op.create_table(
        "ocr_jobs",
        sa.Column("image_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("error_code", sa.String(length=128), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.String(length=64), nullable=True),
        sa.Column("finished_at", sa.String(length=64), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["image_id"], ["images.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ocr_jobs_image_id"), "ocr_jobs", ["image_id"], unique=False)
    op.create_index(op.f("ix_ocr_jobs_status"), "ocr_jobs", ["status"], unique=False)

    op.create_table(
        "ocr_results",
        sa.Column("image_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("normalized_text", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("segmenter", sa.String(length=128), nullable=False),
        sa.Column("segmentation_model", sa.Text(), nullable=False),
        sa.Column("recognizer", sa.String(length=128), nullable=False),
        sa.Column("recognition_model", sa.Text(), nullable=False),
        sa.Column("recognition_model_version", sa.Text(), nullable=True),
        sa.Column("preprocessing_config", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("recognition_config", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("result_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["image_id"], ["images.id"]),
        sa.ForeignKeyConstraint(["job_id"], ["ocr_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id"),
    )
    op.create_index(op.f("ix_ocr_results_image_id"), "ocr_results", ["image_id"], unique=False)
    op.create_index(op.f("ix_ocr_results_job_id"), "ocr_results", ["job_id"], unique=False)

    op.create_table(
        "ocr_corrections",
        sa.Column("image_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ocr_result_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("corrected_text", sa.Text(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("cer_before", sa.Float(), nullable=True),
        sa.Column("wer_before", sa.Float(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["image_id"], ["images.id"]),
        sa.ForeignKeyConstraint(["ocr_result_id"], ["ocr_results.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ocr_corrections_image_id"), "ocr_corrections", ["image_id"], unique=False)
    op.create_index(op.f("ix_ocr_corrections_ocr_result_id"), "ocr_corrections", ["ocr_result_id"], unique=False)

    op.create_table(
        "training_samples",
        sa.Column("image_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ocr_result_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("correction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sample_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("image_path", sa.Text(), nullable=True),
        sa.Column("annotation_path", sa.Text(), nullable=True),
        sa.Column("dataset_split", sa.String(length=64), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["correction_id"], ["ocr_corrections.id"]),
        sa.ForeignKeyConstraint(["image_id"], ["images.id"]),
        sa.ForeignKeyConstraint(["ocr_result_id"], ["ocr_results.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_training_samples_correction_id"), "training_samples", ["correction_id"], unique=False)
    op.create_index(op.f("ix_training_samples_image_id"), "training_samples", ["image_id"], unique=False)
    op.create_index(op.f("ix_training_samples_ocr_result_id"), "training_samples", ["ocr_result_id"], unique=False)

    op.create_table(
        "ocr_attempt_logs",
        sa.Column("image_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stage", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["image_id"], ["images.id"]),
        sa.ForeignKeyConstraint(["job_id"], ["ocr_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ocr_attempt_logs_image_id"), "ocr_attempt_logs", ["image_id"], unique=False)
    op.create_index(op.f("ix_ocr_attempt_logs_job_id"), "ocr_attempt_logs", ["job_id"], unique=False)


def downgrade() -> None:
    op.drop_table("ocr_attempt_logs")
    op.drop_table("training_samples")
    op.drop_table("ocr_corrections")
    op.drop_table("ocr_results")
    op.drop_table("ocr_jobs")
    op.drop_table("images")
