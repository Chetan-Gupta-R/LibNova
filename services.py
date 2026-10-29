
"""LibNova: library business rules and transaction-safe operations."""

import sqlite3
from contextlib import contextmanager
from datetime import date, timedelta
from typing import Optional

from database import get_connection


# --------------------------------------------------
# LIBRARY POLICIES
# --------------------------------------------------

MAX_ACTIVE_LOANS = 3
LOAN_PERIOD_DAYS = 14
FINE_PER_DAY = 5.0


class ServiceError(Exception):
    """Raised when a library operation violates a rule."""


# --------------------------------------------------
# TRANSACTION MANAGEMENT
# --------------------------------------------------

@contextmanager
def transaction():
    """
    Commit all changes together, or roll them all back.
    BEGIN IMMEDIATE helps serialize competing write operations.
    """
    conn = get_connection()

    try:
        conn.execute("BEGIN IMMEDIATE")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def read_connection():
    """Open and reliably close a read connection."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def _today(value: Optional[date] = None) -> date:
    return value or date.today()


def _log(conn, action, entity_type, entity_id, details):
    """Write an audit record inside the current transaction."""
    conn.execute(
        """
        INSERT INTO audit_logs
            (action, entity_type, entity_id, details)
        VALUES (?, ?, ?, ?)
        """,
        (action, entity_type, entity_id, details),
    )


# --------------------------------------------------
# INTERNAL VALIDATION
# --------------------------------------------------

def _get_book(conn, book_id):
    book = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,),
    ).fetchone()

    if book is None:
        raise ServiceError("Book not found.")

    return book


def _get_member(conn, member_id):
    member = conn.execute(
        "SELECT * FROM members WHERE id = ?",
        (member_id,),
    ).fetchone()

    if member is None:
        raise ServiceError("Member not found.")

    if member["active"] != 1:
        raise ServiceError("This member account is inactive.")

    return member


def _active_loan_count(conn, member_id):
    row = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM loans
        WHERE member_id = ?
          AND returned_at IS NULL
        """,
        (member_id,),
    ).fetchone()

    return row["total"]


def _has_overdue_loan(conn, member_id, today):
    row = conn.execute(
        """
        SELECT id, due_at
        FROM loans
        WHERE member_id = ?
          AND returned_at IS NULL
          AND due_at < ?
        ORDER BY due_at
        LIMIT 1
        """,
        (member_id, today.isoformat()),
    ).fetchone()

    return row is not None


def _has_active_copy(conn, member_id, book_id):
    row = conn.execute(
        """
        SELECT id
        FROM loans
        WHERE member_id = ?
          AND book_id = ?
          AND returned_at IS NULL
        LIMIT 1
        """,
        (member_id, book_id),
    ).fetchone()

    return row is not None


def _available_copies(conn, book_id):
    row = conn.execute(
        """
        SELECT
            b.total_copies -
            (
                SELECT COUNT(*)
                FROM loans l
                WHERE l.book_id = b.id
                  AND l.returned_at IS NULL
            ) AS available
        FROM books b
        WHERE b.id = ?
        """,
        (book_id,),
    ).fetchone()

    if row is None:
        raise ServiceError("Book not found.")

    return row["available"]


def _first_waiting_reservation(conn, book_id):
    return conn.execute(
        """
        SELECT id, member_id
        FROM reservations
        WHERE book_id = ?
          AND status = 'WAITING'
        ORDER BY created_at, id
        LIMIT 1
        """,
        (book_id,),
    ).fetchone()


def _check_member_eligible(conn, member_id, book_id, today):
    """Validate rules that apply before a book can be issued."""
    _get_member(conn, member_id)

    if _has_overdue_loan(conn, member_id, today):
        raise ServiceError(
            "Borrowing blocked: return your overdue books first."
        )

    if _active_loan_count(conn, member_id) >= MAX_ACTIVE_LOANS:
        raise ServiceError(
            f"Borrowing limit reached ({MAX_ACTIVE_LOANS} books)."
        )

    if _has_active_copy(conn, member_id, book_id):
        raise ServiceError(
            "This member already has an active loan for this book."
        )


def _create_loan(conn, book_id, member_id, today):
    """Insert a loan after all validations have passed."""
    issued_at = today
    due_at = issued_at + timedelta(days=LOAN_PERIOD_DAYS)

    cursor = conn.execute(
        """
        INSERT INTO loans
            (book_id, member_id, issued_at, due_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            book_id,
            member_id,
            issued_at.isoformat(),
            due_at.isoformat(),
        ),
    )

    loan_id = cursor.lastrowid

    _log(
        conn,
        "BOOK_ISSUED",
        "loan",
        loan_id,
        (
            f"book_id={book_id}; member_id={member_id}; "
            f"issued_at={issued_at}; due_at={due_at}"
        ),
    )

    return {
        "loan_id": loan_id,
        "book_id": book_id,
        "member_id": member_id,
        "issued_at": issued_at.isoformat(),
        "due_at": due_at.isoformat(),
    }


# --------------------------------------------------
# INVENTORY AND AVAILABILITY
# --------------------------------------------------

def get_book_availability(book_id):
    """Return total, borrowed and available copy counts."""
    with read_connection() as conn:
        book = _get_book(conn, book_id)
        borrowed = conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM loans
            WHERE book_id = ?
              AND returned_at IS NULL
            """,
            (book_id,),
        ).fetchone()["total"]

        return {
            "book_id": book_id,
            "title": book["title"],
            "total_copies": book["total_copies"],
            "borrowed_copies": borrowed,
            "available_copies": book["total_copies"] - borrowed,
        }


def list_books(search=""):
    """Search the catalog by title, author, ISBN or category."""
    search = search.strip()

    with read_connection() as conn:
        return conn.execute(
            """
            SELECT
                b.*,
                b.total_copies -
                (
                    SELECT COUNT(*)
                    FROM loans l
                    WHERE l.book_id = b.id
                      AND l.returned_at IS NULL
                ) AS available_copies
            FROM books b
            WHERE ? = ''
               OR b.title LIKE ?
               OR b.author LIKE ?
               OR COALESCE(b.isbn, '') LIKE ?
               OR b.category LIKE ?
            ORDER BY b.title COLLATE NOCASE
            """,
            (
                search,
                f"%{search}%",
                f"%{search}%",
                f"%{search}%",
                f"%{search}%",
            ),
        ).fetchall()


# --------------------------------------------------
# BOOK AND MEMBER REGISTRATION
# --------------------------------------------------

def add_book(
    title,
    author,
    category,
    total_copies=1,
    isbn=None,
    publisher=None,
    publication_year=None,
):
    """Register a new book title."""
    title = title.strip()
    author = author.strip()
    category = category.strip()

    if not title or not author or not category:
        raise ServiceError(
            "Title, author and category are required."
        )

    if not isinstance(total_copies, int) or isinstance(
        total_copies, bool
    ) or total_copies < 0:
        raise ServiceError(
            "Total copies must be a non-negative integer."
        )

    if publication_year is not None:
        if not 1 <= publication_year <= 9999:
            raise ServiceError("Invalid publication year.")

    isbn = isbn.strip() if isbn else None
    publisher = publisher.strip() if publisher else None

    try:
        with transaction() as conn:
            cursor = conn.execute(
                """
                INSERT INTO books
                    (isbn, title, author, category, publisher,
                     publication_year, total_copies)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    isbn,
                    title,
                    author,
                    category,
                    publisher,
                    publication_year,
                    total_copies,
                ),
            )

            book_id = cursor.lastrowid

            _log(
                conn,
                "BOOK_ADDED",
                "book",
                book_id,
                f"title={title}; copies={total_copies}",
            )

            return book_id

    except sqlite3.IntegrityError as exc:
        raise ServiceError(
            "Could not add book. Check for a duplicate ISBN "
            "or invalid book details."
        ) from exc


def add_member(
    member_code,
    full_name,
    email=None,
    department=None,
):
    """Register a new library member."""
    member_code = member_code.strip()
    full_name = full_name.strip()
    email = email.strip() if email else None
    department = department.strip() if department else None

    if not member_code or not full_name:
        raise ServiceError(
            "Member code and full name are required."
        )

    try:
        with transaction() as conn:
            cursor = conn.execute(
                """
                INSERT INTO members
                    (member_code, full_name, email, department)
                VALUES (?, ?, ?, ?)
                """,
                (member_code, full_name, email, department),
            )

            member_id = cursor.lastrowid

            _log(
                conn,
                "MEMBER_ADDED",
                "member",
                member_id,
                f"member_code={member_code}; name={full_name}",
            )

            return member_id

    except sqlite3.IntegrityError as exc:
        raise ServiceError(
            "Could not add member. The member code or email "
            "may already exist."
        ) from exc


# --------------------------------------------------
# ISSUE A BOOK
# --------------------------------------------------

def issue_book(book_id, member_id, today=None):
    """
    Issue one copy if all borrowing policies are satisfied.

    The optional date is useful for deterministic testing.
    """
    today = _today(today)

    with transaction() as conn:
        book = _get_book(conn, book_id)

        _check_member_eligible(
            conn, member_id, book_id, today
        )

        available = _available_copies(conn, book_id)

        if available <= 0:
            raise ServiceError(
                "No copies are currently available. "
                "Create a reservation instead."
            )

        # Respect the FIFO waiting list.
        waiting = _first_waiting_reservation(conn, book_id)

        if waiting is not None:
            if waiting["member_id"] != member_id:
                raise ServiceError(
                    "This book has a waiting list. "
                    "It must be allocated to the earliest reservation."
                )

        loan = _create_loan(conn, book_id, member_id, today)

        # Fulfil the member's reservation, if they were first.
        if waiting is not None:
            conn.execute(
                """
                UPDATE reservations
                SET status = 'FULFILLED'
                WHERE id = ?
                """,
                (waiting["id"],),
            )

            _log(
                conn,
                "RESERVATION_FULFILLED",
                "reservation",
                waiting["id"],
                f"loan_id={loan['loan_id']}",
            )

        return {
            "success": True,
            "message": (
                f"Issued '{book['title']}'. "
                f"Due date: {loan['due_at']}."
            ),
            **loan,
        }


# --------------------------------------------------
# RETURN A BOOK
# --------------------------------------------------

def return_book(loan_id, today=None):
    """
    Return an active loan, calculate its fine, and
    allocate the copy to the earliest eligible reservation.
    """
    today = _today(today)

    with transaction() as conn:
        loan = conn.execute(
            """
            SELECT
                l.*,
                b.title,
                m.full_name
            FROM loans l
            JOIN books b ON b.id = l.book_id
            JOIN members m ON m.id = l.member_id
            WHERE l.id = ?
            """,
            (loan_id,),
        ).fetchone()

        if loan is None:
            raise ServiceError("Loan record not found.")

        if loan["returned_at"] is not None:
            raise ServiceError("This book has already been returned.")

        due_date = date.fromisoformat(loan["due_at"])
        overdue_days = max(0, (today - due_date).days)
        fine = overdue_days * FINE_PER_DAY

        conn.execute(
            """
            UPDATE loans
            SET returned_at = ?, fine_amount = ?
            WHERE id = ? AND returned_at IS NULL
            """,
            (today.isoformat(), fine, loan_id),
        )

        _log(
            conn,
            "BOOK_RETURNED",
            "loan",
            loan_id,
            (
                f"book_id={loan['book_id']}; "
                f"member_id={loan['member_id']}; "
                f"overdue_days={overdue_days}; fine={fine:.2f}"
            ),
        )

        # The returned copy goes to the first eligible
        # reservation, rather than skipping the queue.
        waiting = _first_waiting_reservation(
            conn, loan["book_id"]
        )

        allocation = None

        if waiting is not None:
            reserved_member = conn.execute(
                """
                SELECT * FROM members
                WHERE id = ? AND active = 1
                """,
                (waiting["member_id"],),
            ).fetchone()

            if reserved_member is not None:
                eligible = (
                    not _has_overdue_loan(
                        conn, reserved_member["id"], today
                    )
                    and _active_loan_count(
                        conn, reserved_member["id"]
                    ) < MAX_ACTIVE_LOANS
                    and not _has_active_copy(
                        conn,
                        reserved_member["id"],
                        loan["book_id"],
                    )
                )

                if eligible:
                    new_loan = _create_loan(
                        conn,
                        loan["book_id"],
                        reserved_member["id"],
                        today,
                    )

                    conn.execute(
                        """
                        UPDATE reservations
                        SET status = 'FULFILLED'
                        WHERE id = ?
                          AND status = 'WAITING'
                        """,
                        (waiting["id"],),
                    )

                    _log(
                        conn,
                        "RESERVATION_FULFILLED",
                        "reservation",
                        waiting["id"],
                        f"loan_id={new_loan['loan_id']}",
                    )

                    allocation = {
                        "member_id": reserved_member["id"],
                        "member_name": reserved_member["full_name"],
                        "loan_id": new_loan["loan_id"],
                        "due_at": new_loan["due_at"],
                    }

        message = (
            f"Returned '{loan['title']}'. "
            f"Fine: ₹{fine:.2f}."
        )

        if allocation:
            message += (
                f" Copy allocated to reservation holder "
                f"{allocation['member_name']}."
            )

        elif waiting is not None:
            message += (
                " A reservation is waiting, but its holder "
                "is not currently eligible. The copy remains "
                "available only to that queue position."
            )

        return {
            "success": True,
            "message": message,
            "loan_id": loan_id,
            "overdue_days": overdue_days,
            "fine_amount": fine,
            "allocation": allocation,
        }


# --------------------------------------------------
# RESERVATIONS
# --------------------------------------------------

def reserve_book(book_id, member_id, today=None):
    """Add a member to the FIFO queue for an unavailable book."""
    today = _today(today)

    with transaction() as conn:
        book = _get_book(conn, book_id)
        _get_member(conn, member_id)

        if _has_active_copy(conn, member_id, book_id):
            raise ServiceError(
                "You already have an active loan for this book."
            )

        existing = conn.execute(
            """
            SELECT id FROM reservations
            WHERE book_id = ?
              AND member_id = ?
              AND status = 'WAITING'
            LIMIT 1
            """,
            (book_id, member_id),
        ).fetchone()

        if existing:
            raise ServiceError(
                "You already have a waiting reservation for this book."
            )

        if _available_copies(conn, book_id) > 0:
            raise ServiceError(
                "A copy is available. Please issue it instead."
            )

        cursor = conn.execute(
            """
            INSERT INTO reservations (book_id, member_id)
            VALUES (?, ?)
            """,
            (book_id, member_id),
        )

        reservation_id = cursor.lastrowid

        _log(
            conn,
            "BOOK_RESERVED",
            "reservation",
            reservation_id,
            f"book_id={book_id}; member_id={member_id}",
        )

        position = conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM reservations
            WHERE book_id = ?
              AND status = 'WAITING'
              AND (
                  created_at < (
                      SELECT created_at
                      FROM reservations
                      WHERE id = ?
                  )
                  OR (
                      created_at = (
                          SELECT created_at
                          FROM reservations
                          WHERE id = ?
                      )
                      AND id <= ?
                  )
              )
            """,
            (
                book_id,
                reservation_id,
                reservation_id,
                reservation_id,
            ),
        ).fetchone()["total"]

        return {
            "success": True,
            "reservation_id": reservation_id,
            "position": position,
            "message": (
                f"Reservation created for '{book['title']}'. "
                f"Queue position: {position}."
            ),
        }


def cancel_reservation(reservation_id, member_id):
    """Allow a member to cancel their own waiting reservation."""
    with transaction() as conn:
        reservation = conn.execute(
            """
            SELECT * FROM reservations
            WHERE id = ? AND member_id = ?
            """,
            (reservation_id, member_id),
        ).fetchone()

        if reservation is None:
            raise ServiceError("Reservation not found for this member.")

        if reservation["status"] != "WAITING":
            raise ServiceError(
                "Only waiting reservations can be cancelled."
            )

        conn.execute(
            """
            UPDATE reservations
            SET status = 'CANCELLED'
            WHERE id = ?
            """,
            (reservation_id,),
        )

        _log(
            conn,
            "RESERVATION_CANCELLED",
            "reservation",
            reservation_id,
            f"member_id={member_id}",
        )

        return {
            "success": True,
            "message": "Reservation cancelled.",
        }


# --------------------------------------------------
# REPORTING HELPERS
# --------------------------------------------------

def list_active_loans():
    """Return active loans with member and book details."""
    with read_connection() as conn:
        return conn.execute(
            """
            SELECT
                l.id AS loan_id,
                b.title,
                b.author,
                m.member_code,
                m.full_name,
                l.issued_at,
                l.due_at
            FROM loans l
            JOIN books b ON b.id = l.book_id
            JOIN members m ON m.id = l.member_id
            WHERE l.returned_at IS NULL
            ORDER BY l.due_at, l.id
            """
        ).fetchall()


def list_reservations(book_id=None):
    """List reservation queues, optionally for one book."""
    with read_connection() as conn:
        return conn.execute(
            """
            SELECT
                r.*,
                b.title,
                m.member_code,
                m.full_name
            FROM reservations r
            JOIN books b ON b.id = r.book_id
            JOIN members m ON m.id = r.member_id
            WHERE (? IS NULL OR r.book_id = ?)
            ORDER BY r.created_at, r.id
            """,
            (book_id, book_id),
        ).fetchall()


def list_audit_logs(limit=100):
    """Return recent audit events."""
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise ServiceError("Limit must be an integer.")

    limit = max(1, min(limit, 1000))

    with read_connection() as conn:
        return conn.execute(
            """
            SELECT * FROM audit_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
