# ============================================================
# db.py — PostgreSQL connection manager
# ============================================================
# This file is the single place in the app that knows how to
# connect to the database. Every other file imports get_conn()
# from here instead of managing connections themselves.
# ============================================================

import os        # To read environment variables (DB credentials)
import psycopg2  # The PostgreSQL driver — lets Python talk to Postgres
                 # Install with: pip install psycopg2-binary

# Load .env file so DB credentials don't have to be hardcoded.
# We reuse the same .env loading pattern from the rest of the project.
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ[key] = value


def get_conn():
    """
    Open and return a new PostgreSQL connection.

    Each caller is responsible for closing the connection when done.
    Use it like this:

        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT ...")
            conn.commit()
        finally:
            conn.close()
    """

    # psycopg2.connect() opens a TCP connection to the PostgreSQL server.
    # We read credentials from environment variables — never hardcode passwords.
    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],         # e.g. "localhost"
        port=os.environ.get("DB_PORT", "5432"),  # default Postgres port
        dbname=os.environ["DB_NAME"],       # the database to connect to
        user=os.environ["DB_USER"],         # Postgres username
        password=os.environ["DB_PASSWORD"], # Postgres password
    )

    return conn  # Return the open connection to the caller
