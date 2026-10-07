from pathlib import Path

from PIL import Image


BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = BASE_DIR / "static" / "img" / "source"
OUTPUT_DIR = BASE_DIR / "static" / "img"


def make_versions(filename, prefix, widths):
    source = SOURCE_DIR / filename

    with Image.open(source) as original:
        for width in widths:
            image = original.copy()
            image.thumbnail((width, 10000), Image.Resampling.LANCZOS)

            output = OUTPUT_DIR / f"{prefix}-{width}.png"
            image.save(output, "PNG", optimize=True)

            print(f"Создано: {output}")


make_versions("logo.png", "logo", (480, 900, 1250))
make_versions("ad.png", "ad", (640, 1100, 1650))