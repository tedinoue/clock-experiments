"""Render hour-hand-only clocks for the single-hand experiment.

Same stimulus design as simple_clocks (12 Arabic numerals, hour ticks,
minute ticks, white face) but ONLY the hour hand is drawn. No minute
hand. Tests whether the model can:
  (1) Identify the hour numeral correctly across the dial
  (2) Estimate minutes from the hour hand's fractional position between numerals

Output: scratch/clocks_training/hour_only_clocks/hour_only_HH_MM.png
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path("/Users/tedinoue/work/claude-workspace/scratch")))
import clock_renderer as cr

OUT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training/hour_only_clocks")
OUT.mkdir(parents=True, exist_ok=True)

SIZE = 512


def render_hour_only(hour, minute):
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

    hour_ang, _ = cr.angle_for(hour, minute)

    cr.hand(d, cx, cy, hour_ang, length=r * 0.50, base_w=12, tip_w=4, fill="black")

    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill="black")

    out_path = OUT / f"hour_only_{hour:02d}_{minute:02d}.png"
    img.save(out_path)
    return str(out_path), (hour, minute)


# Cover the full dial at every-half-hour granularity (24 stimuli, 15° steps)
TIMES = []
for h in range(12):
    H = 12 if h == 0 else h
    TIMES.append((H, 0))
    TIMES.append((H, 30))


def main():
    print(f"Rendering {len(TIMES)} hour-only clocks to {OUT}/")
    for h, m in TIMES:
        path, _ = render_hour_only(h, m)
        print(f"  {h:02d}:{m:02d} -> {Path(path).name}")
    print(f"\nDone. {len(TIMES)} stimuli in {OUT}/")


if __name__ == "__main__":
    main()
