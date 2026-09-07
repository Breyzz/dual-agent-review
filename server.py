"""
Minimal local chat server — a browser front end for the same
call_claude/call_gpt functions the CLI uses, with real conversation memory.

Scope, deliberately:
- Binds to 127.0.0.1 only. Nothing outside this machine can reach it, so
  there's no auth — the OS's own user/process boundary is the security
  boundary here, same as any other localhost dev server.
- One shared conversation, held in memory. No multi-session support, no
  persistence to disk — restarting the server clears history. See the
  README's "Next steps" if you want either of those later.
- Claude and GPT keep independent histories of the same conversation: each
  one only ever sees its own past replies, not the other model's answers.

Run with: python server.py
Then open: http://127.0.0.1:8000
"""

import asyncio
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from providers import call_claude, call_gpt

load_dotenv()

app = FastAPI()
STATIC_DIR = Path(__file__).parent / "static"

# In-memory, single shared conversation — see module docstring.
claude_history: list[dict] = []
gpt_history: list[dict] = []


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


async def safe_call(fn, history: list[dict]) -> str:
    """Call fn with a snapshot of history. On failure, remove the user turn
    we just appended so history stays validly alternating for next time —
    otherwise a failed call leaves two consecutive user turns in a row,
    which both providers reject on the following request."""
    try:
        # The SDKs are synchronous; run in a thread so Claude and GPT calls
        # overlap instead of the user waiting for them one after another.
        result = await asyncio.to_thread(fn, list(history))
        history.append({"role": "assistant", "content": result})
        return result
    except Exception as e:
        history.pop()
        return f"[error: {e}]"


@app.post("/api/chat")
async def chat(req: ChatRequest):
    claude_history.append({"role": "user", "content": req.message})
    gpt_history.append({"role": "user", "content": req.message})

    claude_reply, gpt_reply = await asyncio.gather(
        safe_call(call_claude, claude_history),
        safe_call(call_gpt, gpt_history),
    )
    return {"claude": claude_reply, "gpt": gpt_reply}


@app.post("/api/reset")
def reset():
    claude_history.clear()
    gpt_history.clear()
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
