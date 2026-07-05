from db import get_conn


def save_message(doc_id: int, role: str, content: str) -> None:
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO messages (doc_id, role, content) VALUES (%s, %s, %s)",
            (doc_id, role, content),
        )
        conn.commit()
    finally:
        conn.close()


from typing import List, Dict

def get_history(doc_id: int, limit: int = 6) -> List[Dict]:
    conn = get_conn()
    try:
        cur = conn.cursor()
        # Fetch the most recent `limit` messages, then return them oldest-first
        # so Claude sees the conversation in chronological order.
        cur.execute(
            """
            SELECT role, content FROM (
                SELECT role, content, created_at
                FROM messages WHERE doc_id = %s
                ORDER BY created_at DESC LIMIT %s
            ) sub ORDER BY created_at ASC
            """,
            (doc_id, limit),
        )
        return [{"role": row[0], "content": row[1]} for row in cur.fetchall()]
    finally:
        conn.close()


def touch_document(doc_id: int) -> None:
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE documents_meta SET last_accessed_at = NOW() WHERE id = %s",
            (doc_id,),
        )
        conn.commit()
    finally:
        conn.close()
