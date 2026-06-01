import os
import psycopg2
from urllib.parse import urlparse

# Load .env for local development (skipped in production — Railway injects env vars directly)
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ.setdefault(key, value)


def get_conn():
    url = os.environ.get("DATABASE_URL")
    if url:
        r = urlparse(url)
        return psycopg2.connect(
            host=r.hostname,
            port=r.port or 5432,
            dbname=r.path.lstrip("/"),
            user=r.username,
            password=r.password,
            sslmode="require",
        )
    # Local fallback using individual DB_* vars
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )
