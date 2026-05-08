"""Render minute-hand-only clocks for the converse single-hand experiment.

Same stimulus design as simple_clocks (12 Arabic numerals, hour ticks,
minute ticks, white face) but ONLY the minute hand is drawn. No hour
hand. Tests minute-hand position perception in isolation, complementary
to render_hour_only.py.

Output: scratch/clocks_training/minute_only_clocks/minute_only_MM.png
(MM = minutes 00-59)
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path("/Users/tedinoue/work/claude-workspace/scratch")))
import clock_renderer as cr

OUT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training/minute_only_clocks")
OUT.mkdir(parents=True, exist_ok=True)

SIZE = 512


def render_minute_only(minute):
    img = Image.new("RGB", (SIZE, SIZE), "white")
    d = ImageDraw.Draw(img)
    cx, cy = SIZE // 2, SIZE // 2
    r = SIZE // 2 - 16

    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline="black", width=3)

    cr.tick_marks(
        d, cx, cy, r,
        hour_color="black", minute_color="black",
        hour_w=4, minute_w=1,
        hour_inset=0.85, minute_inset=0.93, outer=0.96,
    )

    fnt_num = cr.font("sans_bold", 36)
    for h in range(1, 13):
        ang = h * 30
        nx, ny = cr.polar(cx, cy, ang, r * 0.74)
        cr.draw_text_centered(d, nx, ny, str(h), fnt_num, "black")

    # Minute hand only: same dimensions as in simple_clocks renderer
    _, min_ang = cr.angle_for(12, minute)  # hour=12 is irrelevant; we only use min_ang

    cr.hand(d, cx, cy, min_ang, length=r * 0.78, base_w=8, tip_w=2, fill="black")

    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill="black")

    out_path = OUT / f"minute_only_{minute:02d}.png"
    img.save(out_path)
    return str(out_path), minute


def main():
    print(f"Rendering 60 minute-only clocks to {OUT}/")
    for m in range(60):
        path, _ = render_minute_only(m)
        if m % 10 == 0:
            print(f"  ...{m:02d} -> {Path(path).name}")
    print(f"\nDone. 60 stimuli in {OUT}/")


if __name__ == "__main__":
    main()
