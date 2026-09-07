"""
Thin wrappers around the Anthropic and OpenAI SDKs.

Kept in one small file on purpose: if you ever need to audit exactly what
leaves your machine and where it goes, this is the only file that matters.
Nothing here talks to anything but api.anthropic.com and api.openai.com.
"""

import os

from anthropic import Anthropic
from openai import OpenAI

# Defaults — override via env vars if a newer model is available on your
# account. Model names change often; check
#   https://docs.claude.com/en/docs/about-claude/models
#   https://platform.openai.com/docs/models
# before assuming these are current.
DEFAULT_CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")
DEFAULT_GPT_MODEL = os.environ.get("GPT_MODEL", "gpt-5")

MAX_TOKENS = 4096


def call_claude(prompt: str, model: str = DEFAULT_CLAUDE_MODEL) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and fill it in."
        )
    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def call_gpt(prompt: str, model: str = DEFAULT_GPT_MODEL) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and fill it in."
        )
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
