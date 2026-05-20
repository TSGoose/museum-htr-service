# Museum OCR Service

Async OCR/HTR service for handwritten Russian museum cards.

## MVP architecture

```text
FastAPI
PostgreSQL
Redis
Dramatiq
local volume storage
Kraken segmentation
Transformers TrOCR recognition
correction/training dataset foundation
```

## Target OCR pipeline

```text
JPG
→ preprocessing
→ Kraken BLLA segmentation
→ line crops
→ Kansallisarkisto/cyrillic-htr-model recognition
→ postprocessing
→ OCR result
→ user correction
→ training dataset
```

## Safe infrastructure run

This starts with the dummy OCR pipeline, which is useful for checking API/DB/queue flow.

```bash
cp .env.example .env
docker compose up --build
docker compose exec ocr-api alembic upgrade head
```

Open API docs:

```text
http://localhost:8000/docs
```

## Local tests

```bash
uv sync --group dev
uv run pytest
```

## Enable OCR dependencies locally

```bash
uv sync --group dev --extra ocr
```

Download the default Hugging Face model:

```bash
uv run python -m app.tools.download_hf_model \
  --model Kansallisarkisto/cyrillic-htr-model \
  --output ./models/huggingface/Kansallisarkisto/cyrillic-htr-model
```

## Enable OCR in Docker

Build with OCR dependencies:

```bash
INSTALL_OCR=true docker compose build
INSTALL_OCR=true docker compose up
```

Then set these values in `.env`:

```env
OCR_PIPELINE=kraken-segmentation-transformers-trocr
OCR_SEGMENTER=kraken
OCR_RECOGNIZER=transformers_trocr
OCR_TROCR_MODEL_PATH=/app/models/huggingface/Kansallisarkisto/cyrillic-htr-model
OCR_KRAKEN_SEGMENTATION_MODEL_PATH=/app/models/kraken/segmentation/blla.mlmodel
```

If Kraken is not installed or the BLLA model is not ready, use the lightweight fallback:

```env
OCR_SEGMENTER=simple
OCR_RECOGNIZER=transformers_trocr
```

## Endpoints

```text
GET  /api/v1/health
GET  /api/v1/ready
POST /api/v1/images
GET  /api/v1/jobs/{job_id}
GET  /api/v1/images/{image_id}/result
GET  /api/v1/images/{image_id}/result?include_lines=true
POST /api/v1/images/{image_id}/correction
POST /api/v1/evaluation/calculate
```

## Notes

The Kraken adapter expects a BLLA `.mlmodel` at:

```text
models/kraken/segmentation/blla.mlmodel
```

The Transformers recognizer expects line images. For real OCR use either:

```text
OCR_SEGMENTER=kraken
```

or, for rough local experiments:

```text
OCR_SEGMENTER=simple
```
