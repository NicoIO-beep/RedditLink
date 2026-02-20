"""Generiert die Extension-Icons (16, 48, 128px) — einmalig ausführen."""
from PIL import Image, ImageDraw
import os

OUT = os.path.join(os.path.dirname(__file__), "extension")

ORANGE = (249, 115, 22)   # #f97316
WHITE  = (255, 255, 255)


def make_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Abgerundetes Rechteck (orange)
    r = size // 6
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=ORANGE)

    # Download-Pfeil: Schaft + Pfeilspitze + Linie
    cx = size // 2
    pad = size * 0.20

    shaft_top    = size * 0.15
    shaft_bottom = size * 0.58
    shaft_w      = max(2, size * 0.13)

    arrow_w = size * 0.45
    arrow_h = size * 0.22

    line_y   = size * 0.80
    line_w   = max(1, size * 0.09)

    # Schaft
    d.rectangle([cx - shaft_w / 2, shaft_top,
                 cx + shaft_w / 2, shaft_bottom], fill=WHITE)

    # Pfeilspitze (Dreieck)
    d.polygon([
        (cx - arrow_w / 2, shaft_bottom),
        (cx + arrow_w / 2, shaft_bottom),
        (cx,               shaft_bottom + arrow_h),
    ], fill=WHITE)

    # Unterstrich-Linie
    d.rectangle([pad, line_y, size - pad, line_y + line_w], fill=WHITE)

    return img


for sz in (16, 48, 128):
    path = os.path.join(OUT, f"icon{sz}.png")
    make_icon(sz).save(path)
    print(f"Erstellt: {path}")

print("Icons fertig.")
