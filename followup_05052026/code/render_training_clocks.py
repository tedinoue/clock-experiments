"""Render a training clock set at NEW times distinct from the 8 test stimuli.

Test times (avoid all): 10:10, 3:25, 7:50, 8:20, 4:15, 6:30, 11:55, 9:45/2:15.

Calls the existing render functions in scratch/clock_renderer.py with new
(hour, minute) values. Output to scratch/clocks_training/clocks/.
"""
import sys
from pathlib import Path

# Make the existing renderer importable + override its OUT to a training subdir
sys.path.insert(0, str(Path("/Users/tedinoue/work/claude-workspace/scratch")))
import clock_renderer as cr

TRAINING_OUT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training/clocks")
TRAINING_OUT.mkdir(parents=True, exist_ok=True)
cr.OUT = TRAINING_OUT  # redirect output

# Training set — 8 clocks at NEW times, mirroring the 8 style categories.
SPEC = [
    ("train_01_chronograph_arabic", cr.render_clock_01_chronograph_arabic, 2, 50),
    ("train_02_chronograph_arabic_b", cr.render_clock_01_chronograph_arabic, 8, 35),
    ("train_03_roman_date", cr.render_clock_02_roman_date, 11, 20),
    ("train_04_naked_hands", cr.render_clock_04_naked_hands, 5, 10),
    ("train_05_24hour", cr.render_clock_03_24hour, 14, 30),  # 14:30 = 2:30 PM (12-hour read = 2:30)
    ("train_06_mirrored", cr.render_clock_08_mirrored, 6, 40),
    ("train_07_dark_simple", cr.render_clock_07_dark_simple, 7, 35),
    ("train_08_no_numerals", cr.render_clock_06_rainbow_no_numerals, 12, 5),
]

def main():
    rendered = []
    for label, fn, h, m in SPEC:
        # Each render function writes to cr.OUT/clock_NN.png with its hardcoded
        # filename. We need to rename after each call. Since cr.OUT is now the
        # training dir, files land there but with the stock names. Rename.
        path, gt = fn(h, m)
        new_name = TRAINING_OUT / f"{label}.png"
        Path(path).rename(new_name)
        rendered.append((label, new_name, gt))
        print(f"  {label}: {gt[0]:02d}:{gt[1]:02d} -> {new_name}")
    print(f"\nRendered {len(rendered)} training clocks at {TRAINING_OUT}/")
    return rendered

if __name__ == "__main__":
    main()
