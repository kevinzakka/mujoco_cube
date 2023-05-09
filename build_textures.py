"""Generate cubelet textures for a 3x3 cube."""

from PIL import Image, ImageDraw
import itertools
import pathlib

colors = {
    "white": (255, 255, 255),
    "red": (137, 18, 20),
    "blue": (13, 72, 172),
    "orange": (255, 85, 37),
    "green": (25, 155, 76),
    "yellow": (254, 213, 47),
}

res = 256  # Texture resolution.
imsize = (res * 4, res * 3)
rad = int(0.2 * res)  # Rounded rectangle radius.
width = int(0.08 * res)  # Fill width.
kwargs = dict(radius=rad, width=width, outline=(0, 0, 0))

pathlib.Path("assets").mkdir(parents=True, exist_ok=True)

# Center cubelets: 1 color.
for color in colors:
    img = Image.new("RGB", imsize, color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((res, res, 2 * res, 2 * res), fill=colors[color], **kwargs)
    img.save(f"assets/{color}.png")

# Edge cubelets: 2 colors.
for color1, color2 in itertools.combinations(colors, 2):
    color1, color2 = sorted([color1, color2])

    # Skip impossible combinations.
    if color1 == "white" and color2 == "yellow":
        continue
    if color1 == "red" and color2 == "orange":
        continue
    if color1 == "blue" and color2 == "green":
        continue

    img = Image.new("RGB", imsize, color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((res, res, 2 * res, 2 * res), fill=colors[color1], **kwargs)
    draw.rounded_rectangle(
        (2 * res, res, 3 * res, 2 * res), fill=colors[color2], **kwargs
    )
    img.save(f"assets/{color1}_{color2}.png")

# Corner cubelets: 3 colors.
for comb in itertools.combinations(colors, 3):
    # Skip impossible combinations.
    if "white" in comb and "yellow" in comb:
        continue
    if "red" in comb and "orange" in comb:
        continue
    if "blue" in comb and "green" in comb:
        continue

    color1, color2, color3 = sorted(comb)

    img = Image.new("RGB", imsize, color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((res, res, 2 * res, 2 * res), fill=colors[color1], **kwargs)
    draw.rounded_rectangle(
        (2 * res, res, 3 * res, 2 * res), fill=colors[color2], **kwargs
    )
    draw.rounded_rectangle(
        (3 * res, res, 4 * res, 2 * res), fill=colors[color3], **kwargs
    )
    img.save(f"assets/{color1}_{color2}_{color3}.png")
