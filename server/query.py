# ============================================================
# query.py — Find the most relevant chunks for a user's question
# ============================================================
# This is the "retrieval" part of RAG (Retrieval-Augmented Generation).
# The user asks a question → we embed it → we search the database
# for the chunks whose vectors are closest to the question's vector
# → we return those chunks as context for the LLM to answer from.
# ============================================================

from typing import List, Optional
from embedder import embed_chunks
from db import get_conn


def query_similar(question: str, top_k: int = 5, doc_id: Optional[int] = None) -> List[str]:
    """
    Find the top_k most relevant text chunks for a given question.

    Args:
        question: The user's question in plain English.
        top_k:    How many chunks to return (default 5).
        doc_id:   If provided, only search chunks from this document.
                  If omitted, search across all documents (Phase 1 behaviour).

    Returns:
        A list of text strings — the most relevant chunks from the database.
    """

    # Embed the question into a 1536-dim vector.
    # We pass it as a list because embed_chunks() expects a list;
    # [0] pulls the single vector back out.
    question_vector = embed_chunks([question])[0]
    vector_str = str(question_vector)

    conn = get_conn()
    try:
        cur = conn.cursor()

        if doc_id is not None:
            # Scoped search: only return chunks that belong to this document.
            # The WHERE clause filters rows BEFORE the cosine distance is ranked,
            # so we never compare against chunks from other documents.
            cur.execute(
                """
                SELECT content
                FROM documents
                WHERE doc_id = %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (doc_id, vector_str, top_k),
            )
        else:
            # Unscoped search: compare against every chunk in the database.
            # Used by the legacy /ask endpoint (Phase 1).
            cur.execute(
                """
                SELECT content
                FROM documents
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (vector_str, top_k),
            )

        # fetchall() returns [("chunk text",), ...] — row[0] extracts the string.
        results = [row[0] for row in cur.fetchall()]

    finally:
        conn.close()

    return results


# ── Quick test ────────────────────────────────────────────────────────
# Run this file directly to test: python query.py
if __name__ == "__main__":
    question = "What was the retrieval accuracy of NeuroSearch-7?"
    print(f"Question: {question}\n")

    chunks = query_similar(question, top_k=3)
    print(f"Top {len(chunks)} relevant chunks (all docs):\n")
    for i, chunk in enumerate(chunks, 1):
        print(f"--- Chunk {i} ---")
        print(chunk)
        print()
