"""Render rainbow no-numerals clock at a new time with normal vs. thick hands
for A/B testing of hand-thickness on Sonnet 4.6 length-perception failure mode.

Test time: 12:55 (close-angle-near-top configuration, similar to T17's 12:05
failure). Two renders: normal-thickness (matching original train_08) and
2x-thicker (both hands proportionally widened, ratio preserved).

Both written to scratch/clocks_training/clocks_held_out/.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, "/Users/tedinoue/work/claude-workspace/scratch")
import clock_renderer as cr

OUT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training/clocks_held_out")
OUT.mkdir(parents=True, exist_ok=True)


def render_rainbow_with_hand_widths(hour, minute, hour_base_w, hour_tip_w,
                                    minute_base_w, minute_tip_w, label):
    """Re-implementation of cr.render_clock_06_rainbow_no_numerals
    parameterized on hand widths."""
    SIZE = cr.SIZE
    im, d, cx, cy = cr.base_canvas()
    bezel_r = SIZE * 0.49
    face_r = SIZE * 0.46
    bezel_color = (50, 50, 50)
    d.ellipse([cx-bezel_r, cy-bezel_r, cx+bezel_r, cy+bezel_r], fill=bezel_color)

    # Rainbow stripe interior (clipped to circle via mask)
    inner = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
    d2 = ImageDraw.Draw(inner)
    stripe_h = SIZE / 7
    colors = [
        (255, 99, 99), (255, 165, 79), (255, 235, 79),
        (140, 220, 110), (110, 180, 240), (95, 130, 230),
        (180, 130, 220),
    ]
    for i, color in enumerate(colors):
        y0 = int(i * stripe_h)
        y1 = int((i + 1) * stripe_h)
        d2.rectangle([0, y0, SIZE, y1], fill=color)

    mask = Image.new("L", (SIZE, SIZE), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([cx-face_r, cy-face_r, cx+face_r, cy+face_r], fill=255)
    im.paste(inner, (0, 0), mask)
    d2 = ImageDraw.Draw(im)

    # Tick marks
    import math
    for i in range(60):
        ang = math.radians(i * 6 - 90)
        is_hour = (i % 5 == 0)
        outer = face_r * 0.96
        inner_r = face_r * 0.86 if is_hour else face_r * 0.91
        x1 = cx + outer * math.cos(ang); y1 = cy + outer * math.sin(ang)
        x2 = cx + inner_r * math.cos(ang); y2 = cy + inner_r * math.sin(ang)
        if is_hour:
            d2.line([(x1, y1), (x2, y2)], fill=(60, 60, 60), width=3)
        else:
            d2.line([(x1, y1), (x2, y2)], fill=(80, 80, 80), width=1)

    # Date window center-low
    win_cx, win_cy = cx, cy + face_r * 0.30
    win_w, win_h = SIZE * 0.28, SIZE * 0.06
    d2.rectangle([win_cx-win_w/2, win_cy-win_h/2, win_cx+win_w/2, win_cy+win_h/2],
                 fill=(252, 252, 252), outline=(60, 60, 60), width=1)
    fnt_date = cr.font("sans_bold", int(SIZE * 0.030))
    bb = d2.textbbox((0, 0), "MON  03  MAY", font=fnt_date)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    d2.text((win_cx-tw/2-bb[0], win_cy-th/2-bb[1]), "MON  03  MAY",
            fill=(20, 20, 20), font=fnt_date)

    # Hands at parameterized widths
    ha, ma = cr.angle_for(hour, minute)
    cr.hand(d2, cx, cy, ha, face_r * 0.55, hour_base_w, hour_tip_w, (255, 255, 255))
    cr.hand(d2, cx, cy, ma, face_r * 0.80, minute_base_w, minute_tip_w, (255, 255, 255))

    out_path = OUT / f"{label}.png"
    im.save(out_path)
    return out_path, (hour, minute)


def main():
    # Time: 12:55 — minute hand at 11 (near top, slight left), hour hand at 12.92
    # (slight right of top). Close angle, both upper, similar geometry to T17's
    # 12:05 failure but on the other side of 12.
    p1, gt1 = render_rainbow_with_hand_widths(
        12, 55,
        hour_base_w=9, hour_tip_w=5, minute_base_w=6, minute_tip_w=3,
        label="rainbow_held_out_12_55_normal",
    )
    print(f"NORMAL hands: {p1} at {gt1}")

    # 2x proportional thicker: 9->18, 5->10, 6->12, 3->6
    p2, gt2 = render_rainbow_with_hand_widths(
        12, 55,
        hour_base_w=18, hour_tip_w=10, minute_base_w=12, minute_tip_w=6,
        label="rainbow_held_out_12_55_thick",
    )
    print(f"THICK hands:  {p2} at {gt2}")


if __name__ == "__main__":
    main()
