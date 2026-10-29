
import sqlite3
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "libnova.db"


def get_connection():
    """Create a connection to the LibNova database."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DB_PATH,
        timeout=10
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    """Create all core library tables if they do not exist."""

    with get_connection() as conn:

        # Books: one row represents a book title.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isbn TEXT UNIQUE,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT NOT NULL,
                publisher TEXT,
                publication_year INTEGER,
                total_copies INTEGER NOT NULL DEFAULT 1
                    CHECK(total_copies >= 0),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CHECK(length(trim(title)) > 0),
                CHECK(length(trim(author)) > 0)
            )
        """)

        # Members: students or other authorized borrowers.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_code TEXT NOT NULL UNIQUE,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE,
                department TEXT,
                active INTEGER NOT NULL DEFAULT 1
                    CHECK(active IN (0, 1)),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CHECK(length(trim(full_name)) > 0)
            )
        """)

        # Loans: each row represents one issued book copy.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                member_id INTEGER NOT NULL,
                issued_at TEXT NOT NULL,
                due_at TEXT NOT NULL,
                returned_at TEXT,
                fine_amount REAL NOT NULL DEFAULT 0
                    CHECK(fine_amount >= 0),
                FOREIGN KEY(book_id) REFERENCES books(id),
                FOREIGN KEY(member_id) REFERENCES members(id),
                CHECK(due_at >= issued_at)
            )
        """)

        # Reservations: waiting list for unavailable books.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                member_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'WAITING'
                    CHECK(status IN (
                        'WAITING', 'FULFILLED',
                        'CANCELLED', 'EXPIRED'
                    )),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(book_id) REFERENCES books(id),
                FOREIGN KEY(member_id) REFERENCES members(id)
            )
        """)

        # Audit log: record important operations.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id INTEGER,
                details TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Useful indexes for frequent searches.
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_books_title
            ON books(title)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_loans_member
            ON loans(member_id, returned_at)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_reservations_queue
            ON reservations(book_id, status, created_at)
        """)


if __name__ == "__main__":
    initialize_database()
    print("LibNova database initialized successfully.")
    print(f"Database location: {DB_PATH}")
