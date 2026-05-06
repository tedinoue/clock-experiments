"""Single-turn API harness for the clocks dialogic-teaching session.

Usage:
    python3 teach.py "<new user message>" [--image path/to/clock.png]
    python3 teach.py --reset                    # wipe conversation state
    python3 teach.py --status                   # show turn count + last response

Maintains conversation state at scratch/clocks_training/conversation.json
and a human-readable transcript at scratch/clocks_training/transcript.md.

API key: source /tmp/clocks_training_keys.env (chmod 600) before invoking.
Model: claude-haiku-4-5-20251001 (per CLAUDE.md model ID).
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
    print("ERROR: anthropic SDK not installed. pip install anthropic", file=sys.stderr)
    sys.exit(1)

ROOT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training")
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_SESSION = "haiku"
MAX_TOKENS = 2048

def session_paths(session):
    base = ROOT / session
    base.mkdir(exist_ok=True)
    return base / "conversation.json", base / "transcript.md"
SYSTEM = (
    "You are an attentive student. The Salon (Terry) is teaching you to read "
    "analog clocks across multiple turns. Engage seriously, answer carefully, "
    "and when you make mistakes, treat the correction as a learning opportunity."
)

def load_state(state_path):
    if state_path.exists():
        return json.loads(state_path.read_text())
    return {"messages": [], "started_at": datetime.now().isoformat()}

def save_state(state, state_path):
    state_path.write_text(json.dumps(state, indent=2))

def encode_image(path):
    data = Path(path).read_bytes()
    if path.lower().endswith(".png"):
        media_type = "image/png"
    elif path.lower().endswith((".jpg", ".jpeg")):
        media_type = "image/jpeg"
    else:
        raise ValueError(f"Unsupported image type: {path}")
    return media_type, base64.standard_b64encode(data).decode("utf-8")

def append_transcript(transcript_path, model, turn_idx, role, text, image_path=None):
    if not transcript_path.exists():
        transcript_path.write_text(
            f"# Clocks Dialogic Teaching Session\n\n"
            f"**Started:** {datetime.now().isoformat()}\n"
            f"**Model (student):** {model}\n"
            f"**Teacher:** Terry (Salon, Opus 4.7 in Claude Code CLI, driving turn-by-turn)\n\n"
            f"---\n\n"
        )
    with transcript_path.open("a") as f:
        f.write(f"## Turn {turn_idx} — {role.title()}\n\n")
        if image_path:
            rel = Path(image_path).name
            f.write(f"![{rel}](../clocks/{rel})\n\n")
        f.write(text + "\n\n---\n\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("message", nargs="?", default=None)
    ap.add_argument("--image", default=None, help="Path to image to attach")
    ap.add_argument("--model", default=DEFAULT_MODEL, help="Model ID (e.g., claude-haiku-4-5-20251001 or claude-sonnet-4-6)")
    ap.add_argument("--session", default=DEFAULT_SESSION, help="Session name (subdir under clocks_training/) for state and transcript")
    ap.add_argument("--reset", action="store_true")
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()

    state_path, transcript_path = session_paths(args.session)

    if args.reset:
        if state_path.exists():
            state_path.unlink()
        if transcript_path.exists():
            transcript_path.unlink()
        print(f"Session '{args.session}' state and transcript reset.")
        return

    state = load_state(state_path)
    n_turns = len(state["messages"]) // 2  # messages are user/assistant pairs

    if args.status:
        print(f"Session: {args.session}")
        print(f"Turns completed: {n_turns}")
        if state["messages"]:
            last = state["messages"][-1]
            text_blocks = [b for b in (last.get("content") or []) if isinstance(b, dict) and b.get("type") == "text"]
            if text_blocks:
                preview = text_blocks[0]["text"][:200]
                print(f"Last {last['role']}: {preview}{'...' if len(text_blocks[0]['text']) > 200 else ''}")
        return

    if args.message is None:
        print("ERROR: provide a message or use --reset / --status", file=sys.stderr)
        sys.exit(2)

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set. source /tmp/clocks_training_keys.env first.", file=sys.stderr)
        sys.exit(3)

    # Build user content
    user_content = []
    if args.image:
        media_type, b64 = encode_image(args.image)
        user_content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": b64},
        })
    user_content.append({"type": "text", "text": args.message})

    state["messages"].append({"role": "user", "content": user_content})
    append_transcript(transcript_path, args.model, n_turns + 1, "teacher (terry)", args.message, image_path=args.image)

    client = Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=args.model,
        max_tokens=MAX_TOKENS,
        system=SYSTEM,
        messages=state["messages"],
    )
    assistant_text = "".join(b.text for b in resp.content if hasattr(b, "text"))
    state["messages"].append({"role": "assistant", "content": [{"type": "text", "text": assistant_text}]})
    append_transcript(transcript_path, args.model, n_turns + 1, f"student ({args.model.split('-')[1]} {args.model.split('-')[2]})", assistant_text)

    save_state(state, state_path)

    print(f"--- Turn {n_turns + 1} complete (session: {args.session}, model: {args.model}) ---")
    print(f"Input tokens: {resp.usage.input_tokens}")
    print(f"Output tokens: {resp.usage.output_tokens}")
    print(f"Stop reason: {resp.stop_reason}")
    print()
    print("Student response:")
    print(assistant_text)

if __name__ == "__main__":
    main()
