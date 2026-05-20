# OCR pipeline

## Default development mode

```env
OCR_SEGMENTER=dummy
OCR_RECOGNIZER=dummy
```

This is for infrastructure testing only.

## Real OCR mode

```env
OCR_SEGMENTER=kraken
OCR_RECOGNIZER=transformers_trocr
```

Pipeline:

```text
JPG
→ DefaultPreprocessor
→ KrakenSegmenter
→ line crops
→ TransformersTrOCRRecognizer
→ DefaultPostProcessor
→ OCRResult
```

## Fallback OCR mode without Kraken

```env
OCR_SEGMENTER=simple
OCR_RECOGNIZER=transformers_trocr
```

This is less accurate than Kraken BLLA segmentation but useful for smoke tests.
