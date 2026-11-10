
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = BASE_DIR / 'static' / 'img' / 'source'
OUTPUT_DIR = BASE_DIR / 'static' / 'img'


def make_versions(filename, prefix, widths):
    """Создать разные размеры изображения, сохранив пропорции."""
    source = SOURCE_DIR / filename
    if not source.is_file():
        raise FileNotFoundError(f'Не найден исходник: {source}')

    with Image.open(source) as original:
        for width in widths:
            image = original.copy()
            image.thumbnail((width, 10000), Image.Resampling.LANCZOS)

            output = OUTPUT_DIR / f'{prefix}-{width}.png'
            image.save(output, 'PNG', optimize=True)

            print(f'Создано: {output}')


if __name__ == '__main__':
    # Исходные изображения проекта.
    make_versions('logo.png', 'logo', (480, 900, 1250))
    make_versions('ad.png', 'ad', (640, 1100, 1650))

    # Новые варианты логотипа и баннера.
    make_versions('blue-violet_logo.png', 'logo-violet', (480, 900))
    make_versions('red-pink_logo.png', 'logo-pink', (480, 900))
    make_versions('pink_banner.png', 'ad-pink', (640, 1100))