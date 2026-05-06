"""Hybrid system-prompt eval: knowledge content + anti-reasoning instruction.

Tests whether a brief enumeration of failure modes COMBINED with an explicit
'trust your first impression, don't overthink' instruction can preserve S3c-like
naive-perception wins (clocks 01, 02, 07) while leaving open whether knowledge
helps on the others.

Compare against:
  - S3c (anti-reasoning only, no knowledge): 37.5% across 8 clocks, N=10 (original)
  - 600-word heavy-summary: 12.5%, N=1 (Part 4)
  - 24-turn in-context training: 12.5%, N=1 (Part 3)
"""
import argparse
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic

ROOT = Path("/Users/tedinoue/work/claude-workspace")
TEST_CLOCKS = ROOT / "salon" / "files" / "clocks" / "rendered"
OUT = ROOT / "scratch" / "clocks_training" / "sonnet_hybrid"
OUT.mkdir(exist_ok=True)

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024

STIMULI = [
    ("clock_01", "10:10"),
    ("clock_02", "3:25"),
    ("clock_03", "7:50"),
    ("clock_04", "8:20"),
    ("clock_05", "4:15"),
    ("clock_06", "6:30"),
    ("clock_07", "11:55"),
    ("clock_08", "9:45 OR 2:15"),
]

SYSTEM = """You are about to read an analog clock from an image.

There are some known failure modes that can affect how vision-language models read clocks. They include: confusing decorations (subdials, date windows, day windows) for hands; reversing length identification under visual clutter; failing to detect when a clock is mirrored (numerals running counter-clockwise with flipped glyphs); reading Roman X as XI or vice-versa; mis-locating hands when both are clustered near the same position; misreading the inner ring on a 24-hour double-ring face; and pattern-matching to a "typical clock" layout when the actual layout is different.

That knowledge is available if you need it. But here is the more important instruction: trust your first impression. Look at the clock, read it as you naturally would, and state the time. Don't overthink any individual reading. Don't run through a long checklist of possible failure modes unless something specific in the image flags one. The naive perception is usually right; second-guessing it can introduce errors.

State the time as HH:MM. Brief reasoning is fine but keep it short."""


def encode_image(path):
    return "image/png", base64.standard_b64encode(Path(path).read_bytes()).decode("utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=1)
    args = ap.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(2)

    client = Anthropic(api_key=api_key)
    results = []
    transcript = OUT / "transcript.md"

    with transcript.open("w") as f:
        f.write(f"# Clocks Hybrid (knowledge + anti-reasoning) Eval — Sonnet 4.6\n\n")
        f.write(f"**Started:** {datetime.now().isoformat()}\n")
        f.write(f"**Trials per clock:** {args.trials}\n\n---\n\n")

        for label, gt in STIMULI:
            image = TEST_CLOCKS / f"{label}.png"
            for i in range(args.trials):
                media_type, b64 = encode_image(image)
                resp = client.messages.create(
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                    system=SYSTEM,
                    messages=[{"role": "user", "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
                        {"type": "text", "text": "Read this clock."},
                    ]}],
                )
                text = "".join(b.text for b in resp.content if hasattr(b, "text"))
                r = {
                    "label": label, "trial": i + 1, "ground_truth": gt,
                    "input_tokens": resp.usage.input_tokens,
                    "output_tokens": resp.usage.output_tokens,
                    "raw_response": text,
                }
                results.append(r)
                f.write(f"## {label} trial {i+1} (truth: {gt})\n\n")
                f.write(text + "\n\n")
                f.write(f"_Tokens: {r['input_tokens']} in / {r['output_tokens']} out_\n\n---\n\n")
                f.flush()
                print(f"  {label} trial {i+1}: {r['output_tokens']} out tokens")

    (OUT / "trials.json").write_text(json.dumps(results, indent=2))
    print(f"\nDone. {len(results)} trials.")


if __name__ == "__main__":
    main()
