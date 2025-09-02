import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name('sandbox.db')
INIT_SQL = Path(__file__).with_name('init.sql').read_text()

def get_conn():
    return sqlite3.connect(DB_PATH)

def reset_db():
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = get_conn()
    conn.executescript(INIT_SQL)
    conn.commit()
    conn.close()

def execute_query(query: str):
    conn = get_conn()
    try:
        cur = conn.execute(query)
        rows = cur.fetchall()
        columns = [d[0] for d in cur.description] if cur.description else []
        return {"columns": columns, "rows": rows}
    finally:
        conn.close()

# Initialize database on import
if not DB_PATH.exists():
    reset_db()
