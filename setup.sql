-- ============================================================
-- setup.sql — Run this once to prepare your PostgreSQL database
-- ============================================================
-- This file creates everything the RAG pipeline needs at the
-- database level. Run it with:
--   psql -U your_user -d your_database -f setup.sql
-- ============================================================

-- Enable the pgvector extension.
-- pgvector adds a new column type called "vector" to PostgreSQL.
-- Without this, PostgreSQL has no idea what a vector (embedding) is.
-- "IF NOT EXISTS" means it won't error if it's already enabled.
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the documents table.
-- This is where every chunk of text + its embedding vector gets stored.
CREATE TABLE IF NOT EXISTS documents (

    -- id: a unique number automatically assigned to each row.
    -- SERIAL means PostgreSQL auto-increments it (1, 2, 3...).
    -- PRIMARY KEY means no two rows can share the same id.
    id          SERIAL PRIMARY KEY,

    -- content: the raw text of the chunk.
    -- We store this so we can return readable text to the LLM at query time.
    -- TEXT has no length limit — important for variable-length chunks.
    content     TEXT NOT NULL,

    -- embedding: the vector representation of the chunk's meaning.
    -- vector(1536) matches text-embedding-3-small's output dimension exactly.
    -- This is what pgvector searches through to find similar chunks.
    embedding   vector(1536) NOT NULL,

    -- created_at: timestamp of when this chunk was inserted.
    -- Useful for debugging, auditing, or future filtering by date.
    -- DEFAULT NOW() means PostgreSQL fills this in automatically.
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Create an index to make vector similarity searches fast.
-- Without this, every search scans ALL rows one-by-one (slow at scale).
-- ivfflat is a type of approximate nearest-neighbor index — it trades
-- a tiny bit of accuracy for a large speed gain on large datasets.
-- lists=100 means the index divides vectors into 100 clusters to search.
CREATE INDEX IF NOT EXISTS documents_embedding_idx
    ON documents
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
-- vector_cosine_ops → tells the index we'll be using cosine distance (<=>)
-- This must match the distance operator used in query.py
