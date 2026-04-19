# ============================================================
# query.py — Find the most relevant chunks for a user's question
# ============================================================
# This is the "retrieval" part of RAG (Retrieval-Augmented Generation).
# The user asks a question → we embed it → we search the database
# for the chunks whose vectors are closest to the question's vector
# → we return those chunks as context for the LLM to answer from.
# ============================================================

from embedder import embed_chunks  # Reuse our embedder to embed the question
from db import get_conn            # Our shared connection helper


def query_similar(question: str, top_k: int = 5) -> list[str]:
    """
    Find the top_k most relevant text chunks for a given question.

    Steps:
      1. Embed the question into a 1536-dim vector
      2. Compare that vector against every stored embedding using cosine distance
      3. Return the top_k closest chunks as plain text strings

    Args:
        question: The user's question in plain English.
        top_k:    How many chunks to return (default 5).

    Returns:
        A list of text strings — the most relevant chunks from the database.
        These get passed to the LLM as context in the next step.
    """

    # Step 1: Embed the question.
    # We pass it as a list because embed_chunks() expects a list.
    # [0] gets the single vector back out of the returned list.
    question_vector = embed_chunks([question])[0]

    # Convert the vector list to the string format pgvector expects:
    # [0.02, -0.14, ...] → "[0.02,-0.14,...]"
    vector_str = str(question_vector)

    # Step 2: Search the database
    conn = get_conn()
    try:
        cur = conn.cursor()

        # The SQL query uses pgvector's <=> operator (cosine distance).
        # It computes the distance between the question vector and every
        # stored embedding, then returns the closest ones first.
        #
        # ORDER BY embedding <=> %s::vector
        #   <=>  = cosine distance operator (0 = identical, 2 = opposite)
        #   Sorting ascending puts the MOST SIMILAR chunks first.
        #
        # LIMIT %s
        #   Only return the top_k results — we don't need all 10,000 chunks.
        cur.execute(
            """
            SELECT content
            FROM documents
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (vector_str, top_k),  # psycopg2 safely fills in both %s placeholders
        )

        # fetchall() returns a list of tuples: [("chunk text",), ("chunk text",), ...]
        # row[0] extracts just the text string from each tuple.
        results = [row[0] for row in cur.fetchall()]

    finally:
        conn.close()

    return results  # List of the top_k most relevant chunk strings


# ── Quick test ────────────────────────────────────────────────────────
# Run this file directly to test: python query.py
if __name__ == "__main__":
    question = "What lives in the deep ocean?"
    print(f"Question: {question}\n")

    chunks = query_similar(question, top_k=3)

    print(f"Top {len(chunks)} relevant chunks:\n")
    for i, chunk in enumerate(chunks, 1):
        print(f"--- Chunk {i} ---")
        print(chunk)
        print()
