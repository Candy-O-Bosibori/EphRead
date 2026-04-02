# ============================================================
# FastAPI Streaming Endpoint
# ============================================================
# FastAPI is a Python web framework — it lets you build APIs
# (URLs that return data) with very little code.
#
# This file creates one endpoint:
#   GET /ask?prompt=your question here
#
# Instead of waiting for the full reply, it streams Claude's
# response chunk-by-chunk directly to the browser — just like
# the terminal script, but over the web.
# ============================================================

import os
import anthropic
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
# StreamingResponse → tells FastAPI to send data piece-by-piece
#                     instead of all at once

# Load API key from .env file
env_path = os.path.join(os.path.dirname(__file__), ".env")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ[key] = value

# Create the FastAPI app — this is the "server" object
app = FastAPI()

# Create the async Anthropic client (one shared instance for the whole app)
client = anthropic.AsyncAnthropic()


# ── Generator function ────────────────────────────────────────────────
# This function is a "generator" — instead of returning one big value,
# it "yields" small pieces one at a time using "yield".
# FastAPI's StreamingResponse calls this repeatedly to get each chunk.
async def stream_claude(prompt: str):
    async with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[
            {"role": "user", "content": prompt}
        ],
    ) as stream:
        async for text in stream.text_stream:
            yield text  # Send this chunk to the browser immediately


# ── The /ask endpoint ─────────────────────────────────────────────────
# @app.get("/ask") tells FastAPI: "when someone visits /ask, run this function"
# prompt: str      tells FastAPI: "expect a URL parameter called 'prompt'"
@app.get("/ask")
async def ask(prompt: str):
    # StreamingResponse wraps our generator and streams it to the browser.
    # media_type="text/plain" tells the browser to display it as plain text.
    return StreamingResponse(stream_claude(prompt), media_type="text/plain")
