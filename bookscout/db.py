"""Lokalna baza SQLite: książki, paczki dla Claude i ustawienia."""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from . import config

JSON_COLUMNS = ("subjects", "toc", "isbn", "availability_detail", "rating", "market")

SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    category TEXT,
    title TEXT NOT NULL,
    author TEXT,
    year INTEGER,
    language TEXT,
    subjects TEXT,
    description TEXT,
    toc TEXT,
    isbn TEXT,
    url TEXT,
    availability TEXT,
    availability_detail TEXT,
    status TEXT NOT NULL DEFAULT 'new',
    flag TEXT NOT NULL DEFAULT '',
    batch_id TEXT,
    rating TEXT,
    market TEXT,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS batches (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    book_ids TEXT NOT NULL,
    created_at REAL NOT NULL,
    imported_at REAL
);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def connect(path: Path | None = None) -> sqlite3.Connection:
    path = path or config.DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    # Jeden użytkownik, krótkie zapytania: wspólne połączenie dla wątków FastAPI.
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def _row(row: sqlite3.Row | None) -> dict | None:
    if row is None:
        return None
    book = dict(row)
    for col in JSON_COLUMNS:
        if col in book and book[col]:
            book[col] = json.loads(book[col])
    return book


def _dump(book: dict) -> dict:
    out = dict(book)
    for col in JSON_COLUMNS:
        if col in out and out[col] is not None and not isinstance(out[col], str):
            out[col] = json.dumps(out[col], ensure_ascii=False)
    return out


def insert_books(conn: sqlite3.Connection, books: list[dict]) -> list[dict]:
    """Dodaje nowe książki; już znane (to samo id) pomija. Zwraca faktycznie dodane."""
    added = []
    now = time.time()
    for book in books:
        if conn.execute("SELECT 1 FROM books WHERE id = ?", (book["id"],)).fetchone():
            continue
        row = _dump({**book, "status": "new", "flag": "", "created_at": now, "updated_at": now})
        cols = ", ".join(row)
        conn.execute(f"INSERT INTO books ({cols}) VALUES ({', '.join('?' * len(row))})", tuple(row.values()))
        added.append(book)
    conn.commit()
    return added


def update_book(conn: sqlite3.Connection, book_id: str, **fields) -> None:
    row = _dump({**fields, "updated_at": time.time()})
    sets = ", ".join(f"{k} = ?" for k in row)
    conn.execute(f"UPDATE books SET {sets} WHERE id = ?", (*row.values(), book_id))
    conn.commit()


def get_book(conn: sqlite3.Connection, book_id: str) -> dict | None:
    return _row(conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone())


def list_books(conn: sqlite3.Connection, statuses: list[str] | None = None, include_dismissed=False) -> list[dict]:
    sql, args = "SELECT * FROM books WHERE 1=1", []
    if statuses:
        sql += f" AND status IN ({', '.join('?' * len(statuses))})"
        args += statuses
    if not include_dismissed:
        sql += " AND flag != 'dismissed'"
    sql += " ORDER BY created_at DESC"
    return [_row(r) for r in conn.execute(sql, args).fetchall()]


def counts(conn: sqlite3.Connection) -> dict:
    rows = conn.execute(
        "SELECT status, COUNT(*) AS n FROM books WHERE flag != 'dismissed' GROUP BY status").fetchall()
    return {r["status"]: r["n"] for r in rows}


def create_batch(conn: sqlite3.Connection, kind: str, book_ids: list[str]) -> str:
    batch_id = f"{kind}_{time.strftime('%Y%m%d_%H%M%S')}_{int(time.time() * 1000) % 1000:03d}"
    conn.execute("INSERT INTO batches (id, kind, book_ids, created_at) VALUES (?, ?, ?, ?)",
                 (batch_id, kind, json.dumps(book_ids), time.time()))
    conn.commit()
    return batch_id


def get_batch(conn: sqlite3.Connection, batch_id: str) -> dict | None:
    row = conn.execute("SELECT * FROM batches WHERE id = ?", (batch_id,)).fetchone()
    if row is None:
        return None
    batch = dict(row)
    batch["book_ids"] = json.loads(batch["book_ids"])
    return batch


def mark_batch_imported(conn: sqlite3.Connection, batch_id: str) -> None:
    conn.execute("UPDATE batches SET imported_at = ? WHERE id = ?", (time.time(), batch_id))
    conn.commit()


def get_settings(conn: sqlite3.Connection) -> dict:
    stored = {r["key"]: json.loads(r["value"]) for r in conn.execute("SELECT * FROM settings")}
    return {**config.DEFAULT_SETTINGS, **stored}


def save_settings(conn: sqlite3.Connection, values: dict) -> dict:
    for key, default in config.DEFAULT_SETTINGS.items():
        if key not in values:
            continue
        value = values[key]
        value = bool(value) if isinstance(default, bool) else type(default)(value)
        conn.execute("INSERT INTO settings (key, value) VALUES (?, ?) "
                     "ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, json.dumps(value)))
    conn.commit()
    return get_settings(conn)
