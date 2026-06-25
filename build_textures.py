"""Generate a single UV sticker-atlas texture for the 3x3 cube.

Instead of baking one cube-map texture per cubelet (the old approach), we emit a
single horizontal atlas with one square swatch per sticker color, plus a black
swatch for the chamfered bevels and any face without a sticker. The cubelet
meshes carry UV coordinates that map each face into the right swatch, so the
whole model needs only one texture and one material. See ``build_mjcf.py``.
"""

import pathlib

from PIL import Image, ImageDraw

# Sticker colors. "black" is the first swatch and is used for the chamfer bevels
# and for any cubelet face that does not carry a sticker.
COLORS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "yellow": (254, 213, 47),
    "red": (137, 18, 20),
    "orange": (255, 85, 37),
    "blue": (13, 72, 172),
    "green": (25, 155, 76),
}

# Atlas order; index i occupies u in [i / N, (i + 1) / N].
SWATCH_ORDER = list(COLORS.keys())

RES = 256  # Per-swatch resolution.
RAD = int(0.2 * RES)  # Rounded-rectangle corner radius.
WIDTH = int(0.08 * RES)  # Outline width.


def build_atlas() -> Image.Image:
    n = len(SWATCH_ORDER)
    img = Image.new("RGB", (RES * n, RES), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    for i, name in enumerate(SWATCH_ORDER):
        if name == "black":
            continue  # Leave it black.
        x0 = i * RES
        draw.rounded_rectangle(
            (x0, 0, x0 + RES, RES),
            radius=RAD,
            width=WIDTH,
            outline=(0, 0, 0),
            fill=COLORS[name],
        )
    return img


def main() -> None:
    pathlib.Path("assets").mkdir(parents=True, exist_ok=True)
    build_atlas().save("assets/sticker.png")


if __name__ == "__main__":
    main()
