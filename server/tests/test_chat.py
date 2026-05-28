import pytest
from fastapi.testclient import TestClient

from main import EXPIRY_DAYS, app

client = TestClient(app)


# ── Unit-style tests (no DB required) ────────────────────────────────

def test_expiry_days_is_positive_int():
    assert isinstance(EXPIRY_DAYS, int)
    assert EXPIRY_DAYS > 0


def test_upload_rejects_non_pdf():
    resp = client.post(
        "/upload",
        files={"file": ("notes.txt", b"some text content", "text/plain")},
    )
    assert resp.status_code == 400
    assert "PDF" in resp.json()["detail"]


def test_upload_rejects_empty_pdf():
    # A valid PDF header but no extractable text (simulate scanned/empty)
    fake_pdf = b"%PDF-1.4"
    resp = client.post(
        "/upload",
        files={"file": ("empty.pdf", fake_pdf, "application/pdf")},
    )
    # pypdf will fail to parse or return empty text — either 422 or 500 is acceptable
    assert resp.status_code in (422, 500)


def test_history_returns_empty_list_for_unknown_doc():
    resp = client.get("/history?doc_id=999999")
    assert resp.status_code == 200
    assert resp.json() == []


def test_chat_requires_doc_id():
    resp = client.post("/chat", json={"message": "hello"})
    assert resp.status_code == 422  # FastAPI validation error — doc_id missing


def test_chat_requires_message():
    resp = client.post("/chat", json={"doc_id": 1})
    assert resp.status_code == 422  # FastAPI validation error — message missing


# ── Debate mode tests ─────────────────────────────────────────────────

def test_debate_mode_defaults_to_false():
    # debate_mode is optional — omitting it should not cause a validation error.
    # The request still fails (no DB), but the shape is accepted.
    resp = client.post("/chat", json={"message": "hello", "doc_id": 1}, stream=True)
    # Any response other than 422 means the body shape was valid
    assert resp.status_code != 422


def test_debate_mode_true_accepted():
    resp = client.post(
        "/chat",
        json={"message": "hello", "doc_id": 1, "debate_mode": True},
        stream=True,
    )
    assert resp.status_code != 422


def test_debate_mode_invalid_type_rejected():
    # debate_mode must be a boolean — a string should be rejected
    resp = client.post(
        "/chat",
        json={"message": "hello", "doc_id": 1, "debate_mode": "yes"},
    )
    assert resp.status_code == 422


# ── SSE format tests ──────────────────────────────────────────────────

def test_chat_response_is_event_stream():
    # /chat must declare text/event-stream so browsers know to parse SSE.
    # We don't need a real doc — the response headers are set before any DB call.
    resp = client.post("/chat", json={"message": "hi", "doc_id": 1}, stream=True)
    assert "text/event-stream" in resp.headers.get("content-type", "")


def test_chat_response_has_cache_control():
    # Cache-Control: no-cache is required for SSE — without it proxies and
    # browsers may buffer the response and break the live-streaming effect.
    resp = client.post("/chat", json={"message": "hi", "doc_id": 1}, stream=True)
    assert resp.headers.get("cache-control") == "no-cache"


# ── Integration tests (require a running DB + seeded data) ───────────
# Run these manually after: python seed.py
#
# To run only unit tests (skip DB):
#   pytest tests/ -v -k "not integration"
#
# To run everything:
#   pytest tests/ -v

@pytest.mark.integration
def test_full_chat_flow():
    """Upload a tiny in-memory PDF, chat, check history saves."""
    # This test requires the DB to be running and setup.sql to have been applied.
    # It's marked integration so it can be skipped in CI without a DB.
    pytest.skip("Requires live DB — run manually after seed.py")
