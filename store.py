# ============================================================
# store.py — Save chunks + their embedding vectors to PostgreSQL
# ============================================================
# This file is the bridge between our text processing pipeline
# and the database. It takes the output of chunker.py and
# embedder.py and writes both the raw text AND the vector
# into the documents table we created in setup.sql.
# ============================================================

import psycopg2.extras  # Provides execute_values() for fast bulk inserts
from db import get_conn  # Our shared connection helper from db.py


def store_chunks(chunks: list[str], vectors: list[list[float]]) -> None:
    """
    Insert a list of text chunks and their vectors into the database.

    Args:
        chunks:  List of text strings from chunker.py.
        vectors: List of 1536-float vectors from embedder.py.
                 Must be the same length as chunks — index 0 matches index 0.

    Example:
        chunks  = ["The ocean is deep", "Fish live underwater"]
        vectors = [[0.02, -0.14, ...], [0.05, -0.11, ...]]
        store_chunks(chunks, vectors)
        # → 2 rows inserted into the documents table
    """

    # Pair each chunk with its vector: [("text1", [v1...]), ("text2", [v2...])]
    # zip() walks both lists in parallel, giving us one (chunk, vector) pair
    # at a time — like zipping two sides of a zipper together.
    rows = [(chunk, vector) for chunk, vector in zip(chunks, vectors)]

    # Open a database connection (from db.py)
    conn = get_conn()
    try:
        cur = conn.cursor()  # A cursor is the object we use to send SQL commands

        # INSERT all rows in one SQL call using execute_values().
        # This is much faster than calling cur.execute() in a loop —
        # one round-trip to the database instead of N round-trips.
        #
        # The SQL:
        #   INSERT INTO documents (content, embedding) VALUES ...
        #   %s        → psycopg2 fills in the chunk text (safe, prevents SQL injection)
        #   %s::vector → fills in the vector and casts it to pgvector's vector type
        psycopg2.extras.execute_values(
            cur,
            "INSERT INTO documents (content, embedding) VALUES %s",
            [(chunk, str(vector)) for chunk, vector in rows],
            # We convert the vector list to a string like "[0.02,-0.14,...]"
            # because that's the format pgvector expects for the ::vector cast.
            template="(%s, %s::vector)",
        )

        conn.commit()  # Save the inserts permanently — without this, nothing is written

        print(f"Stored {len(rows)} chunks into the database.")

    finally:
        conn.close()  # Always close the connection, even if an error occurred
