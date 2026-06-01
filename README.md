# EphRead

A RAG (Retrieval-Augmented Generation) chat app built for College students. Upload a PDF, ask questions about it, and get streaming answers from Claude — grounded in the actual document content.

## What it does

- Upload any text-based PDF
- The document is chunked, embedded (OpenAI), and stored in a vector database
- Ask questions in a chat interface — relevant chunks are retrieved and sent to Claude as context
- Claude streams its answer back token by token
- All past conversations persist per document; the sidebar lets you switch between documents
- A "Debate mode" makes Claude steelman both sides of any claim before concluding
- Data auto-expires after 3 days (configurable)

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS v3 |
| Backend | FastAPI (Python), asyncio, Server-Sent Events |
| Embeddings | OpenAI `text-embedding-3-small` (1536 dimensions) |
| LLM | Anthropic Claude (`claude-haiku-4-5`) |
| Database | PostgreSQL + pgvector extension |
| Dev proxy | Vite dev server → FastAPI (no CORS needed locally) |


## Local development

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL with the [pgvector extension](https://github.com/pgvector/pgvector)
- An OpenAI API key
- An Anthropic API key

### 1 — Database setup

```bash
# Create the database and user
psql -U postgres -c "CREATE USER rag_user WITH PASSWORD 'password';"
psql -U postgres -c "CREATE DATABASE rag_db OWNER rag_user;"

# Enable pgvector and create tables
psql -U rag_user -d rag_db -f server/setup.sql
```

### 2 — Backend

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp server/.env.example server/.env
# Edit server/.env with your API keys and DB credentials

# Start the server
cd server
uvicorn main:app --reload
# Runs at http://localhost:8000
```

### 3 — Frontend

```bash
cd client
npm install
npm run dev
# Runs at http://localhost:5173
# All /api/* requests are proxied to localhost:8000 automatically
```

Open `http://localhost:5173` — upload a PDF and start chatting.

## Environment variables

Create `server/.env` with:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rag_db
DB_USER=rag_user
DB_PASSWORD=password

# API keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

In production (Railway), these are set as environment variables in the dashboard — no `.env` file needed.

## API endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/upload` | Upload a PDF; returns `doc_id` and chunk count |
| `GET` | `/documents` | List all uploaded documents |
| `DELETE` | `/documents/{id}` | Delete a document and all its chat history |
| `POST` | `/chat` | Stream a chat response (SSE) |
| `GET` | `/history` | Get chat history for a document |

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for the full Railway + Vercel deployment guide.

**Quick summary:**
- **Railway** — hosts the FastAPI backend and PostgreSQL database (with pgvector)
- **Vercel** — hosts the React frontend as a static build; a rewrite rule proxies `/api/*` to Railway

## Configuration

| Constant | File | Default | Description |
|---|---|---|---|
| `EXPIRY_DAYS` | `server/main.py` | `3` | Days before chat history and documents are auto-deleted |
| `top_k` | `server/main.py` | `12` | Number of chunks retrieved per query |
| `chunk_size` | `server/main.py` | `500` | Characters per chunk when processing PDFs |

## Running tests

```bash
cd server
source ../venv/bin/activate
pytest tests/ -v
```
