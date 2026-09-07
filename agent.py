#!/usr/bin/env python3
"""
Private two-model agent: sends the same diff or question to Claude and GPT,
saves each response as a local markdown file. No third-party service, no
cloud orchestrator — just your two API keys and your filesystem.

Usage:
    python agent.py review                       # diff of uncommitted changes in the current repo
    python agent.py review --path ../other-repo   # diff of uncommitted changes in another repo
    python agent.py review --against main          # diff of current branch vs. main
    python agent.py ask "What's the tradeoff between X and Y?"
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime

from dotenv import load_dotenv

from providers import call_claude, call_gpt

load_dotenv()

REVIEW_PROMPT_TEMPLATE = """\
You are reviewing a code diff. Focus on correctness, edge cases, security \
issues, and architectural concerns. Be specific and cite the relevant lines \
where you can. Skip generic praise — if there's nothing wrong with a section, \
say so briefly and move on.

Diff:
```diff
{diff}
```
"""

ASK_PROMPT_TEMPLATE = """\
{question}

Where you're uncertain about a factual claim, say so directly rather than \
stating it with unearned confidence.
"""


def get_diff(path: str, against: str | None) -> str:
    cmd = ["git", "diff", f"{against}...HEAD"] if against else ["git", "diff", "HEAD"]
    try:
        result = subprocess.run(
            cmd, cwd=path, capture_output=True, text=True, check=True
        )
    except FileNotFoundError:
        print("git not found — is it installed and on PATH?", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"git diff failed:\n{e.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def save_output(out_dir: str, task_name: str, model_name: str, content: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{task_name}_{model_name}.md"
    path = os.path.join(out_dir, filename)
    with open(path, "w") as f:
        f.write(content)
    return path


def run(prompt: str, task_name: str, out_dir: str) -> None:
    print("Calling Claude...")
    try:
        claude_out = call_claude(prompt)
        print(f"Saved: {save_output(out_dir, task_name, 'claude', claude_out)}")
    except Exception as e:
        print(f"Claude call failed: {e}", file=sys.stderr)

    print("Calling GPT...")
    try:
        gpt_out = call_gpt(prompt)
        print(f"Saved: {save_output(out_dir, task_name, 'gpt', gpt_out)}")
    except Exception as e:
        print(f"GPT call failed: {e}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Private two-model review/research agent")
    sub = parser.add_subparsers(dest="command", required=True)

    review_p = sub.add_parser("review", help="Review a git diff with Claude and GPT")
    review_p.add_argument("--path", default=".", help="Path to the git repo (default: current directory)")
    review_p.add_argument("--against", default=None, help="Compare current branch against this ref instead of diffing working tree vs HEAD")
    review_p.add_argument("--out-dir", default="./out", help="Where to write output notes (default: ./out)")

    ask_p = sub.add_parser("ask", help="Ask a research question to Claude and GPT")
    ask_p.add_argument("question", help="The question to ask")
    ask_p.add_argument("--out-dir", default="./out", help="Where to write output notes (default: ./out)")

    args = parser.parse_args()

    if args.command == "review":
        diff = get_diff(args.path, args.against)
        if not diff.strip():
            print("No diff found — nothing to review.")
            return
        prompt = REVIEW_PROMPT_TEMPLATE.format(diff=diff)
        run(prompt, "review", args.out_dir)
    else:
        prompt = ASK_PROMPT_TEMPLATE.format(question=args.question)
        run(prompt, "ask", args.out_dir)


if __name__ == "__main__":
    main()
