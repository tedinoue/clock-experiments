"""Opus 4.7 simplest-clock comparison: 8 stimuli × 2 thinking modes.

Single-shot reads on the 10 simplest-clock stimuli (the same ones used in
v2 dialogic teaching rounds). Question: "What time does this clock show?"
R1-style generic system prompt.

Goal: distinguish "Sonnet-specific" from "Anthropic-architecture-general"
for the B1 zone analysis. If Opus shows the same B1-zone failure pattern
as Sonnet, the architectural bias generalizes. If Opus is robust on the
B1 failure-zone stimuli, the bias is Sonnet-specific.
"""
import argparse, base64, json, os, sys, re
from pathlib import Path
from anthropic import Anthropic

ROOT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training")
SIMPLE = ROOT / "simple_clocks"
MODEL = "claude-opus-4-7"
THINKING_BUDGET = 10000
MAX_TOKENS = 16384

# All 10 simplest stimuli
STIMULI = [
    ("simple_03_00.png", "3:00"),
    ("simple_09_00.png", "9:00"),
    ("simple_01_15.png", "1:15"),
    ("simple_04_30.png", "4:30"),
    ("simple_07_45.png", "7:45"),
    ("simple_02_35.png", "2:35"),
    ("simple_08_25.png", "8:25"),
    ("simple_05_50.png", "5:50"),
    ("simple_10_30.png", "10:30"),
    ("simple_11_40.png", "11:40"),
]

R1_SYSTEM = (
    "You are an attentive student. The Salon (Terry) is teaching you to read "
    "analog clocks across multiple turns. Engage seriously, answer carefully, "
    "and when you make mistakes, treat the correction as a learning opportunity."
)

USER_PROMPT = "What time does this clock show?"

def encode_image(p):
    return "image/png", base64.standard_b64encode(p.read_bytes()).decode()

def run_one(client, image_path, thinking_on):
    media_type, b64 = encode_image(image_path)
    kwargs = dict(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=R1_SYSTEM,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
            {"type": "text", "text": USER_PROMPT},
        ]}],
    )
    if thinking_on:
        # Opus 4.7 uses adaptive thinking API instead of explicit budget_tokens
        kwargs["thinking"] = {"type": "adaptive"}
        kwargs["output_config"] = {"effort": "high"}
    resp = client.messages.create(**kwargs)
    text = "".join(b.text for b in resp.content if b.type == "text")
    thinking = "".join(b.thinking for b in resp.content if b.type == "thinking")
    return text, thinking, resp.usage.input_tokens, resp.usage.output_tokens

def extract_time(text):
    """Find the first H:MM-ish time pattern in the text."""
    # Prefer bolded times
    bold = re.findall(r'\*\*\s*(\d{1,2}:\d{2})\s*\*\*', text)
    if bold:
        return bold[0]
    # Otherwise first H:MM
    m = re.findall(r'\b(\d{1,2}:\d{2})\b', text)
    return m[0] if m else "(none)"

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr); sys.exit(2)
    client = Anthropic(api_key=api_key)

    # Resume mode: skip arms already done by checking existing file
    out_path = ROOT / "opus_simplest_results.json"
    if out_path.exists():
        results = json.loads(out_path.read_text())
    else:
        results = {"thinking_off": [], "thinking_on": []}

    arms = [(False, "thinking_off"), (True, "thinking_on")]
    for thinking_on, key in arms:
        # Skip if all 10 stimuli already completed for this arm
        completed = {t.get("stimulus") for t in results.get(key, []) if "answer" in t and "error" not in t}
        if len(completed) >= len(STIMULI):
            print(f"\n=== Opus 4.7 — thinking {'ON' if thinking_on else 'OFF'} (already complete, skipping) ===")
            continue
        # Reset arm if we're re-running it
        results[key] = []
        print(f"\n=== Opus 4.7 — thinking {'ON' if thinking_on else 'OFF'} ===")
        for filename, truth in STIMULI:
            try:
                text, thinking, in_tok, out_tok = run_one(client, SIMPLE / filename, thinking_on)
                answer = extract_time(text)
                # Lenient match: exact OR within 5 min
                correct = (answer == truth)
                marker = "✓" if correct else "✗"
                print(f"  {marker} {filename:<22} truth={truth:<6} answer={answer:<10} (in={in_tok}, out={out_tok}, think={len(thinking)})")
                results[key].append({
                    "stimulus": filename, "truth": truth, "answer": answer,
                    "correct": correct, "response": text, "thinking_chars": len(thinking),
                    "in_tok": in_tok, "out_tok": out_tok,
                })
            except Exception as e:
                print(f"  ERROR {filename}: {e}")
                results[key].append({"stimulus": filename, "truth": truth, "error": str(e)})

    out_path = ROOT / "opus_simplest_results.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nSaved: {out_path}")

    # Summary table
    print("\n=== Summary: Opus 4.7 vs Sonnet 4.6 R1 ===")
    print(f"{'Stimulus':<22} {'Truth':<7} {'Sonnet R1':<12} {'Opus think-OFF':<16} {'Opus think-ON':<14}")
    sonnet_r1 = {
        "simple_03_00.png": "3:00 ✓", "simple_09_00.png": "9:00 ✓",
        "simple_01_15.png": "1:15 ✓", "simple_04_30.png": "4:30 ✓",
        "simple_07_45.png": "8:45 ✗", "simple_02_35.png": "7:15 ✗",
        "simple_08_25.png": "9:25 ✗", "simple_05_50.png": "10:30 ✗",
        "simple_10_30.png": "(not tested)", "simple_11_40.png": "(not tested)",
    }
    for filename, truth in STIMULI:
        off = next((t for t in results["thinking_off"] if t.get("stimulus") == filename), {})
        on  = next((t for t in results["thinking_on"]  if t.get("stimulus") == filename), {})
        off_str = f"{off.get('answer','?')} {'✓' if off.get('correct') else '✗'}"
        on_str  = f"{on.get('answer','?')} {'✓' if on.get('correct') else '✗'}"
        print(f"{filename:<22} {truth:<7} {sonnet_r1[filename]:<12} {off_str:<16} {on_str:<14}")

if __name__ == "__main__":
    main()
