"""Color-coded clock renderer — final controlled validation.

Per Ted's design (2026-05-07): full-length hands, color-disambiguated.
Hour hand RED. Minute hand BLUE. Hour wider than minute so when they
overlap the red hour shows behind the blue minute. Both reach the tic
marks.

This removes the role-identification confound entirely (color makes role
unambiguous) AND keeps both tips at the labels (extrapolation isn't an
issue). If clocks still fail under this condition, the position-to-hour
conversion error is the real residual mechanism. If they read correctly,
the multi-mechanism story collapses back toward perception.

Output: scratch/clocks_training/color_clocks/color_HH_MM.png
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path("/Users/tedinoue/work/claude-workspace/scratch")))
import clock_renderer as cr

OUT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training/color_clocks")
OUT.mkdir(parents=True, exist_ok=True)

SIZE = 512

HOUR_COLOR = (200, 30, 30)     # red
MINUTE_COLOR = (30, 80, 200)   # blue


def render_color_clock(hour, minute):
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

    # Draw HOUR FIRST (red, wider) so it sits "behind" the minute.
    # Both reach the inner tic edge (0.85 of inner radius).
    cr.hand(d, cx, cy, hour_ang, length=r * 0.85, base_w=16, tip_w=6, fill=HOUR_COLOR)
    # Then MINUTE on top (blue, narrower). Slightly longer so its tip
    # extends to the minor tic ring at 0.93.
    cr.hand(d, cx, cy, min_ang,  length=r * 0.92, base_w=8,  tip_w=2, fill=MINUTE_COLOR)

    # Center pivot dot in black for clarity
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill="black")

    out_path = OUT / f"color_{hour:02d}_{minute:02d}.png"
    img.save(out_path)
    return str(out_path), (hour, minute)


# Same 10 times as the v2 simplest-clock training set
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
    print(f"Rendering {len(STIMULI)} color-coded clocks to {OUT}/")
    for h, m in STIMULI:
        path, _ = render_color_clock(h, m)
        print(f"  {h:02d}:{m:02d} -> {Path(path).name}")
    print(f"\nDone. {len(STIMULI)} stimuli in {OUT}/")


if __name__ == "__main__":
    main()
