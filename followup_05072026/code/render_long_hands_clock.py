"""Long-handed simplest clock renderer for the falsifiable prediction test.

Per Ted's hypothesis (validated by halfcircle experiment 2026-05-07):
clock-reading failures are driven by short-pointer extrapolation. The
mechanism predicts: a clock with both hands drawn LONG (tips reaching
numeral ring) should read accurately even on stimuli that fail with
the standard short-thick hour hand.

Setup: same 10 stimuli as the v2 dialogic teaching set (R1 baseline),
same dial style (12 Arabic numerals, hour ticks, minute ticks), but
both hands rendered with LONG-THIN visual.

Hour hand: length 0.72 of inner radius, thin (tapered 8→2)
Minute hand: length 0.82 of inner radius, thin (tapered 8→2)

Both tips sit near or past the numerals (which are at 0.74 of inner
radius). Hour still shorter than minute for role distinction.

Output: scratch/clocks_training/long_hands_clocks/long_hands_HH_MM.png
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path("/Users/tedinoue/work/claude-workspace/scratch")))
import clock_renderer as cr

OUT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training/long_hands_clocks")
OUT.mkdir(parents=True, exist_ok=True)

SIZE = 512


def render_long_hands(hour, minute):
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

    hour_ang, min_ang = cr.angle_for(hour, minute)

    # BOTH HANDS LONG-THIN. Hour is slightly shorter than minute for role.
    # Both tips sit near or past the numeral ring.
    cr.hand(d, cx, cy, hour_ang, length=r * 0.72, base_w=8, tip_w=2, fill="black")
    cr.hand(d, cx, cy, min_ang,  length=r * 0.82, base_w=8, tip_w=2, fill="black")

    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill="black")

    out_path = OUT / f"long_hands_{hour:02d}_{minute:02d}.png"
    img.save(out_path)
    return str(out_path), (hour, minute)


# Same 10 times as the v2 simplest-clock training set (matches R1 baseline)
STIMULI = [
    (3, 0),
    (9, 0),
    (1, 15),
    (4, 30),
    (7, 45),
    (10, 30),
    (2, 35),
    (5, 50),
    (11, 40),
    (8, 25),
]


def main():
    print(f"Rendering {len(STIMULI)} long-handed clocks to {OUT}/")
    for h, m in STIMULI:
        path, _ = render_long_hands(h, m)
        print(f"  {h:02d}:{m:02d} -> {Path(path).name}")
    print(f"\nDone. {len(STIMULI)} stimuli in {OUT}/")


if __name__ == "__main__":
    main()
