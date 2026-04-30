-- ============================================================
-- setup.sql — Run this once to prepare your PostgreSQL database
-- ============================================================
-- This file creates everything the RAG pipeline needs at the
-- database level. Run it with:
--   psql -U your_user -d your_database -f setup.sql
--
-- To reset and re-run (drops all data):
--   psql -U your_user -d your_database -c "DROP TABLE IF EXISTS documents; DROP TABLE IF EXISTS documents_meta;"
--   psql -U your_user -d your_database -f setup.sql
-- ============================================================

-- Enable the pgvector extension.
-- pgvector adds a new column type called "vector" to PostgreSQL.
-- Without this, PostgreSQL has no idea what a vector (embedding) is.
CREATE EXTENSION IF NOT EXISTS vector;

-- documents_meta: one row per uploaded file.
-- Created BEFORE documents because documents has a foreign key pointing here.
-- A foreign key means: "every doc_id in documents must exist here first."
CREATE TABLE IF NOT EXISTS documents_meta (
    id         SERIAL PRIMARY KEY,   -- auto-assigned document ID (1, 2, 3...)
    filename   TEXT NOT NULL,        -- original filename, e.g. "paper.pdf"
    created_at TIMESTAMP DEFAULT NOW()
);

-- documents: one row per text chunk from a document.
-- Each chunk belongs to exactly one document via doc_id.
CREATE TABLE IF NOT EXISTS documents (
    id          SERIAL PRIMARY KEY,

    -- doc_id links each chunk back to its source document.
    -- REFERENCES documents_meta(id) = foreign key constraint:
    --   you cannot insert a chunk with a doc_id that doesn't exist in documents_meta.
    doc_id      INTEGER NOT NULL REFERENCES documents_meta(id),

    content     TEXT NOT NULL,
    embedding   vector(1536) NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- IVFFlat index for fast similarity search at scale.
-- Only add this once you have at least 1000 rows — on small datasets it
-- returns 0 results because the query lands in an empty cluster.
-- Sequential scan (no index) is correct and faster below ~1000 rows.
--
-- Run this manually when your documents table has real data:
--
--   CREATE INDEX documents_embedding_idx
--       ON documents
--       USING ivfflat (embedding vector_cosine_ops)
--       WITH (lists = 100);
 