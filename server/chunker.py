# ============================================================
# chunker.py — Split a long text into overlapping chunks
# ============================================================
# The AI assistant can't search one giant wall of text efficiently.
# Instead, we cut the text into small pieces (chunks) and store
# each chunk separately. At query time, we find the most relevant
# chunks and send only those to the LLM — not the whole document.
# ============================================================


from typing import List

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split `text` into a list of overlapping chunks.

    Args:
        text:       The full document text to split.
        chunk_size: How many characters per chunk (default 500).
        overlap:    How many characters to repeat between chunks (default 50).

    Returns:
        A list of strings, each up to chunk_size characters long.

    Example:
        chunk_text("abcde", chunk_size=3, overlap=1)
        → ["abc", "cde"]
              ↑ the "c" is shared — that's the overlap
    """

    chunks = []   # We'll collect all chunks here
    start = 0     # Start position of the current chunk in the text

    # Keep slicing until we've covered the whole text
    while start < len(text):

        # Calculate the end position of this chunk
        end = start + chunk_size  # e.g. start=0, chunk_size=500 → end=500

        # Slice the text from start to end.
        # If end goes past the end of the text, Python just takes what's left.
        chunk = text[start:end]

        # Only add non-empty chunks (safety check for trailing whitespace)
        if chunk.strip():
            chunks.append(chunk)

        # Move start forward by (chunk_size - overlap).
        # Subtracting the overlap means the next chunk begins overlap chars
        # BEFORE where this chunk ended — creating the shared region.
        # e.g. chunk_size=500, overlap=50 → advance by 450 each time
        start += chunk_size - overlap

    return chunks  # Return the full list of chunks
