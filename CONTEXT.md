# RAG Chat App — Project Context

> Handoff file for any AI coding assistant (Claude Code, Cursor, GitHub Copilot, etc.).
> Read this first before touching any code.

---

## What This Project Is

A Retrieval-Augmented Generation (RAG) chat app built in Python. The user uploads a PDF → the system splits it into chunks → embeds each chunk as a vector → stores it in PostgreSQL → at query time, finds the most relevant chunks via cosine similarity → passes them as context to Claude (Anthropic) → streams the answer back to the user.

Full pipeline:
```
PDF upload → parse text → chunk → embed (OpenAI) → store (pgvector)
                                                          ↓
User question → embed → cosine similarity search → top-k chunks
                                                          ↓
                              Claude (Anthropic) → streamed answer
```

---

## Design System (Williams College Brand)

| Token | Hex | Tailwind class | Use |
|-------|-----|----------------|-----|
| Purple | `#500082` | `brand-purple` | Nav bar, primary buttons, headings, active states |
| Gold | `#FFBE0A` | `brand-gold` | Accent only — send button, upload highlight, active toggle (1–2 per screen max) |
| Black | `#000000` | `black` | Body text, dark mode base |
| White | `#FFFFFF` | `white` | Page background, card surfaces |

**Rules:**
- Light mode: white page, purple brand elements, gold accents
- Dark mode (`dark` class on `<html>`): `#0d0014` bg, `#2a0050` cards, gold is more prominent
- `darkMode: 'class'` in `tailwind.config.js` — toggled via localStorage + adding class to `<html>`
- Custom shadows: `shadow-purple-sm`, `shadow-purple-md`, `shadow-gold-glow`
- Rounded: `rounded-xl` cards, `rounded-full` buttons/tags
- Typography: system font stack, no decorative fonts

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Web framework | FastAPI (Python) |
| LLM | Anthropic Claude (`claude-haiku-4-5-20251001`) via `anthropic` SDK |
| Embeddings | OpenAI `text-embedding-3-small` (1536 dims) via `openai` SDK |
| Vector DB | PostgreSQL + pgvector extension (`<=>` cosine distance operator) |
| PDF parsing | `pypdf` |
| DB driver | `psycopg2-binary` |
| Python env | `venv` at `./venv/` — activate with `source venv/bin/activate` |
| API keys | Stored in `.env` file (not committed) — needs `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` |

---

## File Map

```
AI--Streaming/
├── main.py          # FastAPI server — /ask and /upload endpoints
├── parse_pdf.py     # parse_pdf(bytes) -> str using pypdf
├── chunker.py       # chunk_text(text, chunk_size=500, overlap=50) -> list[str]
├── embedder.py      # embed_chunks(list[str]) -> list[list[float]] via OpenAI
├── store.py         # create_document(filename) -> int, store_chunks(chunks, vectors, doc_id)
├── query.py         # query_similar(question, top_k=5, doc_id=None) -> list[str]
├── db.py            # get_conn() -> psycopg2 connection
├── setup.sql        # PostgreSQL schema — run once to create tables
├── seed.py          # Test data seeder — seeds 2 docs and runs isolation tests
├── requirements.txt # pip freeze output
├── venv/            # Python virtual environment
└── .env             # API keys (not committed)
```

---

## Database Schema

```sql
-- One row per uploaded document
CREATE TABLE documents_meta (
    id         SERIAL PRIMARY KEY,
    filename   TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- One row per text chunk
CREATE TABLE documents (
    id        SERIAL PRIMARY KEY,
    doc_id    INTEGER NOT NULL REFERENCES documents_meta(id),
    content   TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Important:** Do NOT add an IVFFlat index until you have 1000+ rows. Below that threshold pgvector returns 0 results because query vectors land in empty clusters. Sequential scan is correct and faster on small datasets.

---

## Current API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ask?prompt=...` | Unscoped RAG query — searches all docs, streams Claude answer |
| POST | `/upload` | Upload a PDF → returns `{doc_id, chunk_count, status}` |

---

## Build Roadmap — Progress

### Done
- **Phase 1** — RAG loop wired: `query_similar` called in `/ask` before Claude, chunks passed as system prompt
- **Phase 2** — Document identity: `doc_id` column added, `documents_meta` table, `create_document()` in `store.py`, optional `doc_id` filter in `query.py`, isolation verified via `seed.py`
- **Phase 3** — PDF upload: `POST /upload` endpoint, `parse_pdf.py`, `pypdf` installed

### To Do

**Phase 4 — Chat Endpoint with History + Auto-Expiry**
- Add `messages` table: `id, doc_id, role, content, created_at`
- Add `last_accessed_at` to `documents_meta`
- Add `GET /history?doc_id=...`
- Add `POST /chat` body `{message: str, doc_id: int}`:
  - Fetch last 6 messages for context window
  - Call `query_similar(message, doc_id=doc_id, top_k=5)`
  - Stream via `AsyncAnthropic`
  - Save both turns to `messages` after stream ends
- Add FastAPI `lifespan` background task (runs hourly):
  - Delete messages older than 3 days
  - Delete documents/meta not accessed in 3 days
- Retire old `/ask` endpoint (or keep for debugging)

**Phase 5 — SSE Format**
- Change generator to yield `f"data: {token}\n\n"` per token + `"data: [DONE]\n\n"` at end
- Set `media_type="text/event-stream"` on `StreamingResponse`
- Add `Cache-Control: no-cache` header

**Phase 6 — Debate Mode**
- Add `debate_mode: bool = False` to `POST /chat` body
- Two system prompts: default (answer from context) vs debate (steelman both sides)

**Phase 7 — React Frontend (Vite + TypeScript)**
- `UploadPage`: drag-and-drop PDF → calls `POST /upload` → stores `doc_id`
- `ChatWindow`: text input → `POST /chat` → consume SSE stream → append tokens live
- Load `GET /history` on mount to pre-populate prior messages
- Debate mode toggle in UI

---

## Key Decisions & Gotchas

- **No migrations used** — dev phase, schema changes done by dropping and recreating tables via `setup.sql`. Alembic should be added before production.
- **IVFFlat index disabled** — only add `CREATE INDEX ... USING ivfflat` after 1000+ rows (see comment in `setup.sql`).
- **Claude system prompt** — deliberately avoids the word "context" to prevent Claude from prefacing answers with "Based on the context provided...". The prompt reads: *"Answer the user's question directly using only the information below. Do not say 'based on the context' or similar phrases."*
- **Cosine similarity always returns results** — `query_similar` with a `doc_id` filter never returns empty unless the table has zero rows for that doc. This is expected behaviour, not a bug.
- **Foreign key order** — `documents_meta` must be created before `documents` (FK constraint). When deleting: `documents` first, then `documents_meta`.
- **Scanned PDFs** — `pypdf` returns empty string for image-only PDFs. The `/upload` endpoint returns HTTP 422 in this case.

---

## Running Locally

```bash
# 1. Activate venv
source venv/bin/activate

# 2. Set up DB (run once, or after dropping tables)
psql -U your_user -d your_database -f setup.sql

# 3. Seed test data (optional)
python seed.py

# 4. Start server
uvicorn main:app --reload

# 5. Test upload
curl -F "file=@yourfile.pdf" http://localhost:8000/upload

# 6. Test ask
curl "http://localhost:8000/ask?prompt=what+is+this+about"
```
