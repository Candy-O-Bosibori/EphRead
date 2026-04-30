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
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from query import query_similar
from parse_pdf import parse_pdf
from chunker import chunk_text
from embedder import embed_chunks
from store import store_chunks, create_document
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
    # Retrieve the most relevant chunks from the database for this question.
    # query_similar embeds the prompt and runs a cosine similarity search.
    print(prompt)
    try:
        chunks = query_similar(prompt, top_k=5)
        print('Chunks returned:', len(chunks))
    except Exception as e:
        print('Error:', e)

    # Join the chunks into a single block of context text.
    # Two newlines between chunks make the boundary visible to Claude.
    context = "\n\n".join(chunks)

    async with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        # The system prompt is separate from the conversation messages.
        # Claude treats it as authoritative background — telling it to
        # answer ONLY from the retrieved context prevents hallucination.
        system=f"Answer the user's question directly using only the information below. "
               f"Do not say 'based on the context' or similar phrases — just answer. "
               f"If the answer is not present, say so in one sentence.\n\n"
               f"{context}",
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
    return StreamingResponse(stream_claude(prompt), media_type="text/plain")


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_bytes = await file.read()
    text = parse_pdf(file_bytes)

    if not text.strip():
        raise HTTPException(status_code=422, detail="No extractable text found in PDF.")

    doc_id = create_document(file.filename)
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    vectors = embed_chunks(chunks)
    store_chunks(chunks, vectors, doc_id)

    return {"doc_id": doc_id, "chunk_count": len(chunks), "status": "ready"}
