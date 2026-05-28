# ============================================================
# store.py — Save chunks + their embedding vectors to PostgreSQL
# ============================================================
# Two functions:
#   create_document(filename) → registers a new document, returns its id
#   store_chunks(chunks, vectors, doc_id) → stores all chunks for that document
#
# Always call create_document() first to get a doc_id, then pass
# that doc_id into store_chunks().
# ============================================================

import psycopg2.extras
from db import get_conn


def create_document(filename: str) -> int:
    """
    Register a new document in documents_meta and return its ID.

    This must be called before store_chunks() — you need a doc_id
    to attach chunks to. The doc_id is the auto-incremented primary
    key that PostgreSQL assigns when the row is inserted.

    Args:
        filename: The original filename, e.g. "paper.pdf".

    Returns:
        The new document's integer ID.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        # RETURNING id tells PostgreSQL to give back the new row's id
        # immediately after the INSERT, without needing a second query.
        cur.execute(
            "INSERT INTO documents_meta (filename) VALUES (%s) RETURNING id",
            (filename,),
        )
        doc_id = cur.fetchone()[0]
        conn.commit()
        return doc_id
    finally:
        conn.close()


def store_chunks(chunks: list[str], vectors: list[list[float]], doc_id: int) -> None:
    """
    Insert a list of text chunks and their vectors into the database,
    all linked to the given document ID.

    Args:
        chunks:  List of text strings from chunker.py.
        vectors: List of 1536-float vectors from embedder.py.
                 Must be the same length as chunks.
        doc_id:  The document ID from create_document() — links every
                 chunk back to its source document.

    Example:
        doc_id = create_document("paper.pdf")
        store_chunks(["chunk one", "chunk two"], [vec1, vec2], doc_id)
    """
    conn = get_conn()
    try:
        cur = conn.cursor()

        # INSERT all rows in one SQL call — one round-trip instead of N.
        # Template has three slots: content, embedding::vector, doc_id.
        psycopg2.extras.execute_values(
            cur,
            "INSERT INTO documents (content, embedding, doc_id) VALUES %s",
            [(chunk, str(vector), doc_id) for chunk, vector in zip(chunks, vectors)],
            template="(%s, %s::vector, %s)",
        )

        conn.commit()
        print(f"Stored {len(chunks)} chunks for doc_id={doc_id}.")

    finally:
        conn.close()
