"""Generiert die Extension-Icons (16, 48, 128px) — einmalig ausführen."""
from PIL import Image, ImageDraw
import os, math

OUT = os.path.join(os.path.dirname(__file__), "extension")

BG     = (24, 24, 27)      # #18181b  (UI-Hintergrund)
ORANGE = (249, 115, 22)    # #f97316
WHITE  = (255, 255, 255)


def make_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d   = ImageDraw.Draw(img)

    # ── Hintergrund: abgerundetes Rechteck ──────────────────────────
    r = size // 5
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=BG)

    # ── Orangener Ring ───────────────────────────────────────────────
    cx, cy = size / 2, size / 2
    ring_r  = size * 0.36
    ring_w  = max(2, size * 0.09)
    d.ellipse(
        [cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r],
        outline=ORANGE, width=int(ring_w)
    )

    # ── Weißer Pfeil (Schaft + Spitze + Linie) ───────────────────────
    shaft_w = max(2, size * 0.11)
    shaft_t = cy - ring_r * 0.55
    shaft_b = cy + ring_r * 0.15
    arr_w   = ring_r * 0.75
    arr_h   = ring_r * 0.48
    line_y  = cy + ring_r * 0.58
    line_hw = ring_r * 0.55
    line_h  = max(2, size * 0.08)

    # Schaft
    d.rectangle(
        [cx - shaft_w / 2, shaft_t, cx + shaft_w / 2, shaft_b],
        fill=WHITE
    )
    # Pfeilspitze
    d.polygon([
        (cx - arr_w, shaft_b),
        (cx + arr_w, shaft_b),
        (cx, shaft_b + arr_h),
    ], fill=WHITE)
    # Linie
    d.rectangle(
        [cx - line_hw, line_y, cx + line_hw, line_y + line_h],
        fill=WHITE
    )

    return img


for sz in (16, 48, 128):
    path = os.path.join(OUT, f"icon{sz}.png")
    make_icon(sz).save(path)
    print(f"Erstellt: {path}")

print("Icons fertig.")
