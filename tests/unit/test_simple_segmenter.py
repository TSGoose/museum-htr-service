from pathlib import Path

from PIL import Image, ImageDraw

from app.ocr.segmentation.simple_line_segmenter import SimpleLineSegmenter


def test_simple_segmenter_returns_at_least_one_line(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.jpg"
    img = Image.new("RGB", (300, 120), "white")
    draw = ImageDraw.Draw(img)
    draw.rectangle((20, 25, 250, 38), fill="black")
    draw.rectangle((20, 70, 250, 83), fill="black")
    img.save(image_path)

    lines = SimpleLineSegmenter().segment(image_path)

    assert len(lines) >= 1
    assert all(line.crop_path is not None for line in lines)
