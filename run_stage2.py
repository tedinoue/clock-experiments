#!/usr/bin/env python3
"""
Clocks Stage 2 — single rich-prime system prompt.

Same image suite as Stage 1, same user prompt. Only variable changed:
a system prompt that combines three primes hypothesized to recover
clock-reading capability:

1. PERSONA INDUCTION — expert clockmaker frame
2. METHODICAL HAND-BY-HAND SCAFFOLDING — name each hand and its
   position before committing
3. UNUSUAL-FEATURE CHECKING — explicit instruction to note mirrored
   numerals, missing faces, subdials, 24-hour rings before reading

User prompt unchanged from Stage 1: "What time does this clock show?"

Per `feedback_never_alter_experimental_prompts.md` — this is a Stage 2
manipulation, not a Stage 1 prompt alteration. The user-side prompt is
held constant; only the system prompt is the experimental variable.

5 models × 8 clocks × N=10 trials = 400 clean completions.
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

USER_PROMPT = "What time does this clock show?"

SYSTEM_PROMPT = """You are an experienced clockmaker who has spent decades reading and repairing analog timepieces. You read clocks methodically, never guessing.

When you examine a clock, you proceed in this order:

1. First, examine the clock face as a whole. Note any unusual features before reading the time: mirrored numerals (numbers running counter-clockwise or flipped), absent face or markers, multiple subdials, 24-hour markings, decorative elements that aren't part of the time-reading. These features change how the time should be read.

2. Identify the HOUR hand — usually shorter and thicker. State precisely which numeral or position it points at, or between which two numerals it sits and how far between them.

3. Identify the MINUTE hand — usually longer and thinner. State precisely which numeral position it points at. Remember each numeral represents 5 minutes, so a hand at the "3" position means 15 minutes, a hand at the "9" position means 45 minutes.

4. Reason about the angles carefully. If the hour hand is between two numerals, estimate where in that interval (1/4 of the way from 7 to 8 means about :15 past 7; 1/2 of the way means :30; 3/4 means :45).

5. Only after you have identified both hands and their positions, commit to a specific time."""

COHORT = [
    ("anthropic", "claude-opus-4-7",                "Opus 4.7"),
    ("anthropic", "claude-sonnet-4-6",              "Sonnet 4.6"),
    ("anthropic", "claude-haiku-4-5-20251001",      "Haiku 4.5"),
    ("openai",    "gpt-5",                          "GPT-5"),
    ("google",    "gemini-2.5-pro",                 "Gemini 2.5 Pro"),
]

CLOCKS_DIR = Path(__file__).parent / "rendered"
RESULTS_DIR = Path(__file__).parent / "results"

CLOCKS = [
    ("clock_01", "10:10"),
    ("clock_02", "03:25"),
    ("clock_03", "07:50"),
    ("clock_04", "08:20"),
    ("clock_05", "04:15"),
    ("clock_06", "06:30"),
    ("clock_07", "11:55"),
    ("clock_08", "09:45"),
]

MAX_RETRIES_PER_TRIAL = 8
RETRY_BACKOFF_BASE = 4.0
TIMEOUT = 240  # bumped from 180; system prompt + reasoning takes longer


def load_image_b64(path):
    return base64.b64encode(open(path, "rb").read()).decode("ascii")


def http_post(url, headers, payload, timeout=TIMEOUT):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def call_anthropic(model_id, key, image_b64):
    r = http_post(
        "https://api.anthropic.com/v1/messages",
        {"x-api-key": key, "anthropic-version": "2023-06-01"},
        {
            "model": model_id,
            "max_tokens": 4096,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": [
                {"type": "image", "source": {
                    "type": "base64", "media_type": "image/png", "data": image_b64,
                }},
                {"type": "text", "text": USER_PROMPT},
            ]}],
        },
    )
    return "".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text").strip()


def call_openai(model_id, key, image_b64):
    r = http_post(
        "https://api.openai.com/v1/chat/completions",
        {"Authorization": f"Bearer {key}"},
        {
            "model": model_id,
            "max_completion_tokens": 4096,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/png;base64,{image_b64}",
                    }},
                    {"type": "text", "text": USER_PROMPT},
                ]},
            ],
        },
    )
    return r["choices"][0]["message"]["content"].strip()


def call_google(model_id, key, image_b64):
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{model_id}:generateContent?key={key}")
    r = http_post(url, {}, {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"parts": [
            {"inline_data": {"mime_type": "image/png", "data": image_b64}},
            {"text": USER_PROMPT},
        ]}],
        "generationConfig": {"maxOutputTokens": 4096},
    })
    cand = r.get("candidates", [{}])[0]
    return "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", [])).strip()


DISPATCH = {"anthropic": call_anthropic, "openai": call_openai, "google": call_google}


def run_one_with_retry(provider, model_id, key, image_b64,
                       max_retries=MAX_RETRIES_PER_TRIAL):
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            t0 = time.time()
            raw = DISPATCH[provider](model_id, key, image_b64)
            return raw, time.time() - t0, attempt, None
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:300]
            last_err = f"HTTP {e.code}: {body}"
            if 400 <= e.code < 500 and e.code != 429:
                return None, 0.0, attempt, last_err
        except urllib.error.URLError as e:
            last_err = f"URLError: {e.reason}"
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
        if attempt < max_retries:
            wait = RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
            print(f"      retry {attempt}/{max_retries-1} in {wait:.0f}s ({last_err[:80]})", flush=True)
            time.sleep(wait)
    return None, 0.0, max_retries, last_err


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-trials", type=int, default=10)
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--clocks", nargs="*", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    keys = {
        "anthropic": os.environ.get("ANTHROPIC_API_KEY", ""),
        "openai": os.environ.get("OPENAI_API_KEY", ""),
        "google": os.environ.get("GOOGLE_API_KEY", ""),
    }

    cohort = COHORT
    if args.models:
        cohort = [m for m in COHORT if any(f in m[1] for f in args.models)]
    clocks = CLOCKS
    if args.clocks:
        clocks = [c for c in CLOCKS if any(f in c[0] for f in args.clocks)]

    total_trials = len(cohort) * len(clocks) * args.n_trials
    print(f"Stage 2 plan: {len(cohort)} models × {len(clocks)} clocks × {args.n_trials} trials = {total_trials} clean completions")
    for provider, mid, name in cohort:
        print(f"  {provider:9s} {mid:36s} {name}")
    print(f"User prompt: {USER_PROMPT!r}")
    print(f"System prompt ({len(SYSTEM_PROMPT)} chars):")
    print("  " + "\n  ".join(SYSTEM_PROMPT.split("\n")))

    if args.dry_run:
        return 0

    missing = sorted({p for p, _, _ in cohort if not keys[p]})
    if missing:
        print(f"FATAL: missing API keys: {missing}", file=sys.stderr)
        return 2

    images = {}
    for cid, _ in clocks:
        path = CLOCKS_DIR / f"{cid}.png"
        if not path.exists():
            print(f"FATAL: missing {path}", file=sys.stderr)
            return 2
        images[cid] = load_image_b64(path)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    grand_t0 = time.time()
    for provider, model_id, name in cohort:
        out_path = RESULTS_DIR / f"clocks_stage2_{model_id}.json"
        results = []
        print(f"\n=== {name} ({provider}/{model_id}) ===", flush=True)
        for cid, gt in clocks:
            print(f"  {cid} (gt={gt}): ", end="", flush=True)
            for trial in range(1, args.n_trials + 1):
                raw, elapsed, attempts, err = run_one_with_retry(
                    provider, model_id, keys[provider], images[cid])
                rec = {
                    "model_id": model_id,
                    "model_name": name,
                    "clock_id": cid,
                    "ground_truth": gt,
                    "trial": trial,
                    "raw_response": raw,
                    "elapsed_s": round(elapsed, 2),
                    "attempts": attempts,
                    "error": err,
                    "stage": 2,
                }
                results.append(rec)
                print("." if raw else "X", end="", flush=True)
                with open(out_path, "w") as f:
                    json.dump(results, f, indent=2)
            print(f" ({sum(1 for r in results[-args.n_trials:] if r['raw_response'])}/{args.n_trials})")
        clean = sum(1 for r in results if r["raw_response"])
        print(f"  {name}: {clean}/{len(results)} clean. Saved {out_path}")

    elapsed_min = (time.time() - grand_t0) / 60
    print(f"\nDONE. Total elapsed {elapsed_min:.1f} minutes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
