import hashlib
import shutil
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile

from app.core.config import get_settings


class ImageStorageService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.uploads_dir = self.settings.uploads_dir
        self.processed_dir = self.uploads_dir / "processed"
        self.pending_dir = self.uploads_dir / "pending"
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.pending_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, *, image_id: UUID, file: UploadFile) -> tuple[Path, str, int]:
        suffix = Path(file.filename or "image.jpg").suffix.lower() or ".jpg"
        path = self.pending_dir / f"{image_id}{suffix}"

        sha = hashlib.sha256()
        size = 0
        with path.open("wb") as out:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                sha.update(chunk)
                out.write(chunk)

        return path, sha.hexdigest(), size

    def mark_processed(self, path: Path) -> Path:
        target = self.processed_dir / path.name
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            shutil.move(str(path), str(target))
        return target

    def move_to_training(self, *, image_id: UUID, current_path: str | None) -> Path | None:
        if not current_path:
            return None
        source = Path(current_path)
        if not source.exists():
            return None

        target_dir = self.settings.training_dir / "images"
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / source.name
        shutil.move(str(source), str(target))
        return target
