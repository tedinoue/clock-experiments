"""Render fundamental-perception baseline stimuli for Sonnet 4.6.

Tests whether Sonnet's encoder can resolve angle and length under conditions
isolated from clock-reading semantics. If the encoder is fine on these primitives,
the clock failure modes (length-reversal, hand-id swap, fine-angle-resolution)
must live at the categorical / procedural layer where prompting operates. If the
encoder fails on the primitives, the failure modes are perceptual and unreachable
by prompting.

Four sub-experiments:

B1. Single line, clean: 12 angles (every 30 degrees, clock-convention with 0=up),
    white background, single black hand-style line from center to a point near
    the rim. No anchor markings. Ask: which clock-face position (1-12) does the
    line point toward.

B2. Single line, with chronograph clutter: same 12 angles but with three
    decorative subdial-circles in the background. Tests whether visual clutter
    induces angle-misperception in isolation of clock semantics.

B3. Two lines, clean: two lines from center, one straight up (0 degrees), one
    pointing right (90 degrees). Lengths controlled by a ratio. Ratios: 1.0,
    1.1, 1.2, 1.3, 1.5; for non-1.0 ratios, both directions of "longer" tested.
    Ask: which line is longer (or are they equal).

B4. Two lines, with chronograph clutter: same as B3 but with subdial background.
"""
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, "/Users/tedinoue/work/claude-workspace/scratch")
import clock_renderer as cr

OUT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training/perception_baseline")
OUT.mkdir(parents=True, exist_ok=True)


def draw_subdials(d, cx, cy, SIZE):
    sub_r = SIZE * 0.10
    sub_positions = [
        (cx, cy - SIZE * 0.20),
        (cx - SIZE * 0.18, cy + SIZE * 0.12),
        (cx + SIZE * 0.18, cy + SIZE * 0.12),
    ]
    for sx, sy in sub_positions:
        d.ellipse([sx - sub_r, sy - sub_r, sx + sub_r, sy + sub_r],
                  outline=(180, 180, 180), width=2)
        for tick_angle in range(0, 360, 30):
            ta = math.radians(tick_angle)
            x1 = sx + (sub_r * 0.85) * math.cos(ta)
            y1 = sy + (sub_r * 0.85) * math.sin(ta)
            x2 = sx + sub_r * math.cos(ta)
            y2 = sy + sub_r * math.sin(ta)
            d.line([(x1, y1), (x2, y2)], fill=(160, 160, 160), width=1)
        # tiny stationary hand pointing somewhere fixed
        ta = math.radians(60 - 90)
        d.line([(sx, sy),
                (sx + sub_r * 0.7 * math.cos(ta),
                 sy + sub_r * 0.7 * math.sin(ta))],
               fill=(80, 80, 80), width=2)


def render_single_line(angle_deg, label, subdir, with_clutter=False):
    """Single hand-style black line, anchored at center, extending toward radius
    at the given angle (clock convention: 0=up, 90=right, 180=down, 270=left)."""
    SIZE = cr.SIZE
    im = Image.new("RGB", (SIZE, SIZE), (255, 255, 255))
    d = ImageDraw.Draw(im)
    cx, cy = SIZE // 2, SIZE // 2
    radius = SIZE * 0.40
    if with_clutter:
        draw_subdials(d, cx, cy, SIZE)
    cr.hand(d, cx, cy, angle_deg, radius, 8, 4, (0, 0, 0))
    out = OUT / subdir / f"{label}.png"
    out.parent.mkdir(exist_ok=True)
    im.save(out)
    return out, angle_deg


def render_two_lines(ratio, longer, label, subdir, with_clutter=False):
    """Two hand-style black lines from center: one straight up (0 deg, toward 12),
    one pointing right (90 deg, toward 3). Length controlled by ratio.
    longer in {'up', 'right', 'equal'}."""
    SIZE = cr.SIZE
    im = Image.new("RGB", (SIZE, SIZE), (255, 255, 255))
    d = ImageDraw.Draw(im)
    cx, cy = SIZE // 2, SIZE // 2
    if with_clutter:
        draw_subdials(d, cx, cy, SIZE)
    base_r = SIZE * 0.30
    if longer == "up":
        up_r, right_r = base_r * ratio, base_r
    elif longer == "right":
        up_r, right_r = base_r, base_r * ratio
    else:
        up_r = right_r = base_r
    # Up = 0 degrees
    cr.hand(d, cx, cy, 0, up_r, 8, 4, (0, 0, 0))
    # Right = 90 degrees
    cr.hand(d, cx, cy, 90, right_r, 8, 4, (0, 0, 0))
    out = OUT / subdir / f"{label}.png"
    out.parent.mkdir(exist_ok=True)
    im.save(out)
    return out, ratio, longer


def main():
    # Wipe previous outputs
    for sub in ("b1", "b2", "b3", "b4"):
        d = OUT / sub
        if d.exists():
            for f in d.iterdir():
                f.unlink()

    # B1 + B2: 12 angles every 30 degrees
    angles = list(range(0, 360, 30))
    print("B1 (clean single-line):")
    for a in angles:
        path, _ = render_single_line(a, f"angle_{a:03d}", "b1", with_clutter=False)
        print(f"  {a:03d}°: {path.name}")
    print("\nB2 (cluttered single-line):")
    for a in angles:
        path, _ = render_single_line(a, f"angle_{a:03d}", "b2", with_clutter=True)
        print(f"  {a:03d}°: {path.name}")

    # B3 + B4: ratios with both directions
    ratios = [(1.0, "equal"),
              (1.1, "up"), (1.1, "right"),
              (1.2, "up"), (1.2, "right"),
              (1.3, "up"), (1.3, "right"),
              (1.5, "up"), (1.5, "right")]
    print("\nB3 (clean two-lines):")
    for ratio, longer in ratios:
        label = f"ratio_{int(ratio*10):02d}_{longer}"
        path, _, _ = render_two_lines(ratio, longer, label, "b3", with_clutter=False)
        print(f"  ratio={ratio} longer={longer}: {path.name}")
    print("\nB4 (cluttered two-lines):")
    for ratio, longer in ratios:
        label = f"ratio_{int(ratio*10):02d}_{longer}"
        path, _, _ = render_two_lines(ratio, longer, label, "b4", with_clutter=True)
        print(f"  ratio={ratio} longer={longer}: {path.name}")


if __name__ == "__main__":
    main()
