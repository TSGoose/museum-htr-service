from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "museum-ocr-service"
    app_env: str = "local"
    app_version: str = "0.2.0"
    api_v1_prefix: str = "/api/v1"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "museum_ocr"
    postgres_user: str = "museum_ocr"
    postgres_password: str = "museum_ocr"

    redis_url: str = "redis://localhost:6379/0"

    data_dir: Path = Path("./data")
    uploads_dir: Path = Path("./data/uploads")
    training_dir: Path = Path("./data/training")
    models_dir: Path = Path("./models")
    logs_dir: Path = Path("./data/logs")

    ocr_uploads_max_files: int = 500
    ocr_keep_corrected_images: bool = True
    ocr_save_line_crops: bool = True
    ocr_save_technical_json: bool = True

    ocr_pipeline: str = "dummy"
    ocr_preprocessing_enabled: bool = True
    ocr_max_image_side: int = 3000

    ocr_segmenter: str = "dummy"
    ocr_simple_segmenter_min_line_height: int = 16
    ocr_simple_segmenter_min_ink_ratio: float = 0.005
    ocr_kraken_segmentation_model_path: Path = Path("./models/kraken/segmentation/blla.mlmodel")

    ocr_recognizer: str = "dummy"
    ocr_trocr_model_name: str = "Kansallisarkisto/cyrillic-htr-model"
    ocr_trocr_model_path: Path = Path("./models/huggingface/Kansallisarkisto/cyrillic-htr-model")
    ocr_trocr_device: str = "cpu"
    ocr_trocr_max_new_tokens: int = 256

    ocr_fallback_recognizer: str = "dummy"
    ocr_fallback_model_name: str = "raxtemur/trocr-base-ru"

    ocr_job_max_retries: int = 3
    ocr_job_timeout_seconds: int = 300
    ocr_worker_concurrency: int = 1

    log_level: str = "INFO"
    log_format: str = "json"

    max_upload_size_bytes: int = Field(default=25 * 1024 * 1024)

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
