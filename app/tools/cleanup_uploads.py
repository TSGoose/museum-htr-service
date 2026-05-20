from pathlib import Path

from app.core.config import get_settings


def main() -> None:
    settings = get_settings()
    processed_dir = settings.uploads_dir / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(
        [p for p in processed_dir.iterdir() if p.is_file()],
        key=lambda p: p.stat().st_mtime,
    )

    overflow = len(files) - settings.ocr_uploads_max_files
    if overflow <= 0:
        print(f"No cleanup needed: {len(files)} files")
        return

    for file_path in files[:overflow]:
        file_path.unlink(missing_ok=True)
        print(f"Deleted {file_path}")


if __name__ == "__main__":
    main()
