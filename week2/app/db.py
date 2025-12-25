from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional, List
from contextlib import contextmanager

from .db_models import NoteRecord, ActionItemRecord


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"


def ensure_data_directory_exists() -> None:
    """Ensure the data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    ensure_data_directory_exists()
    connection = None
    try:
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row  # Enable column access by name
        yield connection
    except sqlite3.Error as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if connection:
            connection.close()


def init_db() -> None:
    """Initialize the database with required tables."""
    ensure_data_directory_exists()
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS action_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                text TEXT NOT NULL,
                done INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (note_id) REFERENCES notes(id)
            );
            """
        )
        connection.commit()


def insert_note(content: str) -> int:
    """Insert a new note and return its ID."""
    if not content or not content.strip():
        raise ValueError("Content cannot be empty")

    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO notes (content) VALUES (?)", (content.strip(),))
        connection.commit()
        return int(cursor.lastrowid)


def list_notes() -> List[NoteRecord]:
    """List all notes."""
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
        rows = cursor.fetchall()
        return [
            NoteRecord(
                id=row["id"],
                content=row["content"],
                created_at=row["created_at"]
            )
            for row in rows
        ]


def get_note(note_id: int) -> Optional[NoteRecord]:
    """Get a specific note by ID."""
    if note_id <= 0:
        raise ValueError("Note ID must be a positive integer")

    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, content, created_at FROM notes WHERE id = ?",
            (note_id,),
        )
        row = cursor.fetchone()
        if row:
            return NoteRecord(
                id=row["id"],
                content=row["content"],
                created_at=row["created_at"]
            )
        return None


def insert_action_items(items: List[str], note_id: Optional[int] = None) -> List[int]:
    """Insert multiple action items and return their IDs."""
    if note_id is not None and note_id <= 0:
        raise ValueError("Note ID must be a positive integer or None")

    with get_db_connection() as connection:
        cursor = connection.cursor()
        ids: List[int] = []
        for item in items:
            if item and item.strip():  # Only insert non-empty items
                cursor.execute(
                    "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                    (note_id, item.strip()),
                )
                ids.append(int(cursor.lastrowid))
        connection.commit()
        return ids


def list_action_items(note_id: Optional[int] = None) -> List[ActionItemRecord]:
    """List all action items, optionally filtered by note ID."""
    if note_id is not None and note_id <= 0:
        raise ValueError("Note ID must be a positive integer or None")

    with get_db_connection() as connection:
        cursor = connection.cursor()
        if note_id is None:
            cursor.execute(
                "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
            )
        else:
            cursor.execute(
                "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                (note_id,),
            )
        rows = cursor.fetchall()
        return [
            ActionItemRecord(
                id=row["id"],
                note_id=row["note_id"],
                text=row["text"],
                done=row["done"],
                created_at=row["created_at"]
            )
            for row in rows
        ]


def mark_action_item_done(action_item_id: int, done: bool) -> None:
    """Mark an action item as done or not done."""
    if action_item_id <= 0:
        raise ValueError("Action item ID must be a positive integer")

    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE action_items SET done = ? WHERE id = ?",
            (1 if done else 0, action_item_id),
        )
        connection.commit()
        if cursor.rowcount == 0:
            raise ValueError(f"Action item with ID {action_item_id} not found")


