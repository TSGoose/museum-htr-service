import argparse
from pathlib import Path

from app.core.config import get_settings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise RuntimeError("Install OCR dependencies first: uv sync --extra ocr --group dev") from exc

    settings = get_settings()
    model_name = args.model or settings.ocr_trocr_model_name
    output = Path(args.output) if args.output else settings.ocr_trocr_model_path
    output.mkdir(parents=True, exist_ok=True)

    path = snapshot_download(
        repo_id=model_name,
        local_dir=str(output),
    )
    print(path)


if __name__ == "__main__":
    main()
