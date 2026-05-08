"""Half-circle scale renderer for the extrapolation hypothesis test.

Per Ted's design (2026-05-07): test whether short-pointer extrapolation
is the failure mode behind clock-reading errors. Strip away clock context
entirely.

Layout:
  - Half-circle on the right side of canvas
  - Pivot at left-center
  - 19 tic marks at angles 0°, 10°, ..., 180° (clockwise from up)
  - Each tic labeled A, B, C, ..., S (19 letters)
  - A line emanating from the pivot at the specified angle
  - Three line-length conditions: full (reaches letter), 3/4, 1/2

Output: scratch/clocks_training/halfcircle/{full|three_quarter|half}/scale_<deg>.png
"""
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training/halfcircle")

SIZE = 512
PIVOT = (120, 256)
LETTER_RADIUS = 245
TIC_INNER = 200
TIC_OUTER = 225
TIP_FULL_LENGTH = 215      # just inside the letter ring
TIP_75_LENGTH = 215 * 0.75
TIP_50_LENGTH = 215 * 0.5

LETTERS = "ABCDEFGHIJKLMNOPQRS"  # 19 letters
ASSERT_NUM_LETTERS = len(LETTERS)
assert ASSERT_NUM_LETTERS == 19


def find_font():
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, 28)
            except Exception:
                continue
    return ImageFont.load_default()


def angle_to_xy(angle_deg, radius):
    """0° = straight up, increasing clockwise toward 90°=right, 180°=down."""
    rad = math.radians(angle_deg - 90)
    x = PIVOT[0] + radius * math.cos(rad)
    y = PIVOT[1] + radius * math.sin(rad)
    return (x, y)


def render_scale(line_angle_deg, line_length, save_path):
    img = Image.new("RGB", (SIZE, SIZE), "white")
    d = ImageDraw.Draw(img)

    # Half-circle arc (visual aid — thin grey arc)
    bbox = [PIVOT[0] - TIC_INNER, PIVOT[1] - TIC_INNER,
            PIVOT[0] + TIC_INNER, PIVOT[1] + TIC_INNER]
    d.arc(bbox, start=-90, end=90, fill="lightgrey", width=2)

    # Tic marks
    for i in range(19):
        a = i * 10
        inner = angle_to_xy(a, TIC_INNER)
        outer = angle_to_xy(a, TIC_OUTER)
        d.line([inner, outer], fill="black", width=2)

    # Letters
    fnt = find_font()
    for i in range(19):
        a = i * 10
        cx, cy = angle_to_xy(a, LETTER_RADIUS)
        letter = LETTERS[i]
        # Center the text at (cx, cy)
        try:
            bbox_text = d.textbbox((0, 0), letter, font=fnt)
            tw = bbox_text[2] - bbox_text[0]
            th = bbox_text[3] - bbox_text[1]
        except Exception:
            tw, th = fnt.getsize(letter) if hasattr(fnt, 'getsize') else (12, 16)
        d.text((cx - tw / 2, cy - th / 2 - 4), letter, font=fnt, fill="black")

    # Pointer line
    tip = angle_to_xy(line_angle_deg, line_length)
    d.line([PIVOT, tip], fill="black", width=4)

    # Pivot dot
    d.ellipse([PIVOT[0] - 6, PIVOT[1] - 6, PIVOT[0] + 6, PIVOT[1] + 6], fill="black")

    save_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(save_path)
    return save_path


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["samples", "full"], default="full")
    args = ap.parse_args()

    if args.mode == "samples":
        samples = [
            (45, TIP_FULL_LENGTH, "sample_45deg_full.png"),
            (45, TIP_75_LENGTH, "sample_45deg_three_quarter.png"),
            (45, TIP_50_LENGTH, "sample_45deg_half.png"),
            (90, TIP_FULL_LENGTH, "sample_90deg_full.png"),
            (90, TIP_50_LENGTH, "sample_90deg_half.png"),
        ]
        sample_dir = ROOT / "samples"
        for ang, length, fname in samples:
            render_scale(ang, length, sample_dir / fname)
        print(f"Wrote {len(samples)} samples to {sample_dir}/")
        return

    # Full stimulus set: 37 angles (every 5° from 0° to 180°) × 3 lengths
    angles = list(range(0, 181, 5))  # 0, 5, 10, ..., 180  (37 angles)
    length_specs = [
        ("full", TIP_FULL_LENGTH),
        ("three_quarter", TIP_75_LENGTH),
        ("half", TIP_50_LENGTH),
    ]
    count = 0
    for length_label, length in length_specs:
        outdir = ROOT / length_label
        for ang in angles:
            fname = outdir / f"scale_{ang:03d}.png"
            render_scale(ang, length, fname)
            count += 1
    print(f"Wrote {count} stimuli ({len(angles)} angles × {len(length_specs)} lengths) under {ROOT}/")


if __name__ == "__main__":
    main()
