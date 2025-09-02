from datetime import datetime, timedelta
from typing import Optional
import sqlite3
from pathlib import Path

from jose import JWTError, jwt
from passlib.context import CryptContext

DB_PATH = Path(__file__).with_name('users.db')
SECRET_KEY = 'secret'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


INIT_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    hashed_password TEXT
);
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(INIT_SQL)
    conn.commit()
    return conn


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_user(username: str, password: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO users (username, hashed_password) VALUES (?, ?)",
        (username, get_password_hash(password)),
    )
    conn.commit()
    conn.close()


def authenticate_user(username: str, password: str) -> bool:
    conn = get_conn()
    cur = conn.execute("SELECT hashed_password FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False
    return verify_password(password, row[0])


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
