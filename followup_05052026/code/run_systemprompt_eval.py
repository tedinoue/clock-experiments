"""Fresh-state evaluation of trained-techniques-as-system-prompt on the original 8 test clocks.

Part 3 of the clocks dialogic-teaching findings showed that 24 turns of in-context
teaching did NOT transfer to held-out test stimuli (1/8 strict, at or below S1
baseline). Two competing hypotheses for why:
  (a) long-context degradation: the 24-turn context itself degraded perception
      independent of what the context contained;
  (b) knowledge-installed-but-not-reflexively-applied: techniques are encoded as
      stated procedure but the model doesn't engage them under cold-call.

This script tests (a) vs (b). Condense the 24-turn arc into a single system prompt
synthesizing every failure mode + technique, run each of the 8 original test clocks
in a FRESH conversation state with that system prompt, single trial per clock.

If summary-prompt outperforms the in-context Part 3 result, (a) is the dominant
effect.
If summary-prompt produces similar failures, (b) is the dominant effect.

Compare against:
  - Original Sonnet S1 naive baseline: 25% across the 8 clocks
  - Original Sonnet best-of-condition envelope: 62.5%
  - Trained-context Sonnet (Part 3): 12.5% strict / 25% within_5_min

Usage:
  ANTHROPIC_API_KEY=... python3 run_systemprompt_eval.py [--trials N]

Writes per-trial responses to scratch/clocks_training/sonnet_systemprompt/trials.json
and a human-readable transcript at sonnet_systemprompt/transcript.md.
"""
import argparse
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from anthropic import Anthropic
except ImportError:
    print("ERROR: anthropic SDK not installed.", file=sys.stderr)
    sys.exit(1)

ROOT = Path("/Users/tedinoue/work/claude-workspace")
TEST_CLOCKS = ROOT / "salon" / "files" / "clocks" / "rendered"
OUT = ROOT / "scratch" / "clocks_training" / "sonnet_systemprompt"
OUT.mkdir(exist_ok=True)

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024

# Eight test clocks with ground truth
STIMULI = [
    ("clock_01", "10:10"),
    ("clock_02", "3:25"),
    ("clock_03", "7:50"),
    ("clock_04", "8:20"),
    ("clock_05", "4:15"),
    ("clock_06", "6:30"),
    ("clock_07", "11:55"),
    ("clock_08", "9:45 OR 2:15"),  # mirrored — both readings acceptable
]

SYSTEM = """You are about to read an analog clock from an image. Apply the procedure below carefully. The procedure encodes specific failure modes that vision-language models exhibit on clock-reading tasks; some of them may apply to you. Be vigilant for them.

GENERAL PROCEDURE
1. Detect the clock type before anything else: standard / chronograph (with decorative subdials) / Roman numeral / 24-hour double-ring / mirrored (numerals run counter-clockwise, glyphs flipped) / no-numerals (rainbow or otherwise) / naked-hands (no face).
2. Identify the two main hands at the central pivot. Ignore subdials, date windows, day windows, and any text strips. These are decorative; they are not hands.
3. Identify which hand is the hour and which is the minute.
4. Determine each hand's tip position (NOT the pivot angle — what number does the TIP land on or near?).
5. Read the time. Apply the lower-of-two rule for the hour when the hour hand sits between two numerals.

HOUR-VS-MINUTE IDENTIFICATION — IMPORTANT
The standard rule is "longer hand = minute, shorter hand = hour." This rule fails on certain configurations because length perception in vision encoders can reverse under visual clutter (subdials, double rings, busy backgrounds) or when both hands are close in angle near the top of the face. To guard against this:

- Use BASE-WIDTH-AT-PIVOT as the primary cue, not whole-hand thickness. Look at the very base of each hand where it meets the central pivot. The hour hand's base is wider; the minute hand's base is narrower. This signal is more reliable than length under clutter.
- If base-widths look similar at this rendering, fall back to length, but explicitly cross-check against the consistency of your reading (e.g., at X:30 the hour hand should be halfway between X and X+1; at X:00 the hour hand should point directly at X).

MIRROR CLOCKS
If numerals run counter-clockwise (1 to the LEFT of 12, 11 to the RIGHT of 12) and the glyphs themselves appear horizontally flipped, the clock is mirrored. Read the numerals as they are actually printed at each position. Do not import normal-clock numeral positions ("9 is on the right" is wrong on a mirror; 9 is in the middle-right, where 3 sits on a normal clock). Mirrored "MON" appears as "NOM" — that is a normal date window, not a hand or anomaly.

ROMAN NUMERALS
- IIII (not IV) for 4, by clock-face convention.
- X is two crossed strokes only. XI has an additional vertical stroke to the right of the X. XII has two vertical strokes. When the hour hand sits near a numeral, identify the FULL numeral structure before committing — distinguish "just past X" from "at XI" by looking for the additional vertical stroke.

24-HOUR DOUBLE-RING CLOCKS
Some clocks have an inner 12-hour ring and an outer 24-hour ring. The hands move at the standard 12-hour rate and read against the INNER ring, not the outer. The outer ring is decorative. Read in 12-hour format unless asked otherwise.

NO-ANCHOR STIMULI
On naked-hand clocks (no numerals, no tick marks), angle estimation has roughly 30-degree resolution. Be honest about uncertainty. Use tick marks if present; estimate from standard positions (12 top, 3 right, 6 bottom, 9 left) otherwise.

TIP-TRACING
For each hand, trace from the pivot to the very TIP. The tip determines where the hand points, not the angle near the pivot. Hands sometimes look like they point in one direction near the pivot but actually end up elsewhere at the tip.

GUARD AGAINST PATTERN-MATCHING
If two hands are close in angle and clustered together (especially near the top of the face), you may be tempted to imagine the layout as a "typical clock" with hands in opposite quadrants. Resist this. Trace each tip literally to where it actually lands. Two hands clustered straight down at 6:30 do not look like the famous "10:10" two-hands-spread display.

OUTPUT FORMAT
Walk through your reasoning step by step: clock type detected, hand widths at the pivot, tip positions of each hand, any guardrails that apply, lower-of-two rule applied, consistency check. Then state the time as HH:MM."""


def encode_image(path):
    data = Path(path).read_bytes()
    return "image/png", base64.standard_b64encode(data).decode("utf-8")


def run_one(client, image_path, label, trial_idx):
    media_type, b64 = encode_image(image_path)
    user_content = [
        {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
        {"type": "text", "text": f"Read this clock."},
    ]
    resp = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM,
        messages=[{"role": "user", "content": user_content}],
    )
    text = "".join(b.text for b in resp.content if hasattr(b, "text"))
    return {
        "label": label,
        "trial": trial_idx,
        "input_tokens": resp.usage.input_tokens,
        "output_tokens": resp.usage.output_tokens,
        "stop_reason": resp.stop_reason,
        "raw_response": text,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=1, help="Trials per clock")
    args = ap.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(2)

    client = Anthropic(api_key=api_key)

    results = []
    transcript_path = OUT / "transcript.md"
    trials_path = OUT / "trials.json"

    with transcript_path.open("w") as f:
        f.write(f"# Clocks Systemprompt-Summary Eval — Sonnet 4.6\n\n")
        f.write(f"**Started:** {datetime.now().isoformat()}\n")
        f.write(f"**Trials per clock:** {args.trials}\n\n")
        f.write(f"**System prompt synthesizes:** every failure mode + technique discovered across the 24-turn dialogic teaching arc (Parts 1-2 of FINDINGS.md). Length-vs-base-width, mirror-reading convention, tip-tracing, ignore-decorations, Roman edge disambiguation, 24-hour double-ring rule, ~30° no-anchor resolution, pattern-matching guard.\n\n")
        f.write(f"---\n\n")

        for label, gt in STIMULI:
            image = TEST_CLOCKS / f"{label}.png"
            for i in range(args.trials):
                r = run_one(client, image, label, i + 1)
                r["ground_truth"] = gt
                results.append(r)
                f.write(f"## {label} trial {i+1} (truth: {gt})\n\n")
                f.write(f"![{label}.png](../../salon/files/clocks/rendered/{label}.png)\n\n")
                f.write(r["raw_response"] + "\n\n")
                f.write(f"_Tokens: {r['input_tokens']} in / {r['output_tokens']} out_\n\n---\n\n")
                f.flush()
                print(f"  {label} trial {i+1}: {r['output_tokens']} out tokens")

    trials_path.write_text(json.dumps(results, indent=2))
    print(f"\nWrote {len(results)} trials to {trials_path}")
    print(f"Transcript: {transcript_path}")


if __name__ == "__main__":
    main()
