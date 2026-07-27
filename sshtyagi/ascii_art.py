"""Render a bundled image as monochrome shaded ASCII art (no color, just
character density), styled by the caller like any other figlet banner.

Uses 3 tone levels chosen from this image's own luminance histogram: near-
white background stays blank, the mid-tone (gold) ring/lettering gets a
light shade block, and the darker tones get a solid block.
"""

from pathlib import Path

from PIL import Image

_LEVELS = [
    (220, " "),
    (150, "░"),  # light shade
    (0, "█"),  # full block
]


def render_shaded(image_path: Path, cols: int, char_aspect: float = 0.55) -> str:
    img = Image.open(image_path).convert("L")
    rows = max(1, round(cols * img.height / img.width * char_aspect))
    small = img.resize((cols, rows), Image.LANCZOS)
    pixels = small.load()

    lines = []
    for row in range(rows):
        chars = []
        for col in range(cols):
            lum = pixels[col, row]
            for threshold, ch in _LEVELS:
                if lum >= threshold:
                    chars.append(ch)
                    break
        lines.append("".join(chars))
    return "\n".join(lines)
