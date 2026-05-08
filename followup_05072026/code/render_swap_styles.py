"""Visual-style swap experiments + numerals-removed variant.

Generates three new stimulus sets:

(A) minute_only_thick: minute-hand angles 0-59, drawn with SHORT THICK
    (hour-hand) visual style. Pairs with existing minute_only_clocks.
(B) hour_only_thin: hour-hand angles for 12:00..11:30, drawn with
    LONG THIN (minute-hand) visual style. Pairs with existing
    hour_only_clocks.
(C) hour_only_no_numerals: same hour-hand angles as (B's pair)
    but with NO numerals on the dial — just tick marks.

Tests whether the residual hour-vs-minute asymmetry in Sonnet (15°
median vs 6° median) is visual-style or numeral-attractor or intrinsic
angular bias.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path("/Users/tedinoue/work/claude-workspace/scratch")))
import clock_renderer as cr

ROOT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training")
SIZE = 512


def base_dial(d, cx, cy, r, draw_numerals=True):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline="black", width=3)
    cr.tick_marks(
        d, cx, cy, r,
        hour_color="black", minute_color="black",
        hour_w=4, minute_w=1,
        hour_inset=0.85, minute_inset=0.93, outer=0.96,
    )
    if draw_numerals:
        fnt_num = cr.font("sans_bold", 36)
        for h in range(1, 13):
            ang = h * 30
            nx, ny = cr.polar(cx, cy, ang, r * 0.74)
            cr.draw_text_centered(d, nx, ny, str(h), fnt_num, "black")


def render_minute_only_thick(minute):
    """Minute-hand angle, but drawn with SHORT THICK (hour-hand) visual."""
    img = Image.new("RGB", (SIZE, SIZE), "white")
    d = ImageDraw.Draw(img)
    cx, cy = SIZE // 2, SIZE // 2
    r = SIZE // 2 - 16
    base_dial(d, cx, cy, r, draw_numerals=True)
    _, ang = cr.angle_for(12, minute)
    cr.hand(d, cx, cy, ang, length=r * 0.50, base_w=12, tip_w=4, fill="black")
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill="black")
    return img


def render_hour_only_thin(hour, minute):
    """Hour-hand angle, drawn with LONG THIN (minute-hand) visual."""
    img = Image.new("RGB", (SIZE, SIZE), "white")
    d = ImageDraw.Draw(img)
    cx, cy = SIZE // 2, SIZE // 2
    r = SIZE // 2 - 16
    base_dial(d, cx, cy, r, draw_numerals=True)
    ang, _ = cr.angle_for(hour, minute)
    cr.hand(d, cx, cy, ang, length=r * 0.78, base_w=8, tip_w=2, fill="black")
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill="black")
    return img


def render_hour_only_no_numerals(hour, minute):
    """Hour-hand standard short-thick visual, but NO numerals on the dial."""
    img = Image.new("RGB", (SIZE, SIZE), "white")
    d = ImageDraw.Draw(img)
    cx, cy = SIZE // 2, SIZE // 2
    r = SIZE // 2 - 16
    base_dial(d, cx, cy, r, draw_numerals=False)
    ang, _ = cr.angle_for(hour, minute)
    cr.hand(d, cx, cy, ang, length=r * 0.50, base_w=12, tip_w=4, fill="black")
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill="black")
    return img


HOUR_TIMES = []
for h in range(12):
    H = 12 if h == 0 else h
    HOUR_TIMES.append((H, 0))
    HOUR_TIMES.append((H, 30))


def main():
    # (A) minute_only_thick — 60 stimuli
    out_a = ROOT / "minute_only_thick"
    out_a.mkdir(parents=True, exist_ok=True)
    for m in range(60):
        render_minute_only_thick(m).save(out_a / f"minute_only_thick_{m:02d}.png")
    print(f"(A) minute_only_thick: 60 stimuli at {out_a}/")

    # (B) hour_only_thin — 24 stimuli
    out_b = ROOT / "hour_only_thin"
    out_b.mkdir(parents=True, exist_ok=True)
    for h, m in HOUR_TIMES:
        render_hour_only_thin(h, m).save(out_b / f"hour_only_thin_{h:02d}_{m:02d}.png")
    print(f"(B) hour_only_thin: 24 stimuli at {out_b}/")

    # (C) hour_only_no_numerals — 24 stimuli
    out_c = ROOT / "hour_only_no_numerals"
    out_c.mkdir(parents=True, exist_ok=True)
    for h, m in HOUR_TIMES:
        render_hour_only_no_numerals(h, m).save(out_c / f"hour_only_nonum_{h:02d}_{m:02d}.png")
    print(f"(C) hour_only_no_numerals: 24 stimuli at {out_c}/")


if __name__ == "__main__":
    main()
