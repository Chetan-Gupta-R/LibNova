
"""Basic isolated tests for LibNova services."""

import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

import database
import services


class TestLibNovaServices(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(
    ignore_cleanup_errors=True
        )
        self.db_path = Path(self.temp_dir.name) / "test.db"

        # Redirect database.py to an isolated test database.
        self.data_dir_patch = patch.object(
            database, "DATA_DIR", Path(self.temp_dir.name)
        )
        self.db_path_patch = patch.object(
            database, "DB_PATH", self.db_path
        )
        self.data_dir_patch.start()
        self.db_path_patch.start()

        database.initialize_database()

        self.today = date(2026, 10, 28)

        self.book_id = services.add_book(
            title="Python Basics",
            author="Test Author",
            category="Programming",
            total_copies=2,
            isbn="TEST-001",
        )

        self.member_ids = [
            services.add_member(
                f"TEST{i}",
                f"Student {i}",
                f"student{i}@example.test",
            )
            for i in range(1, 6)
        ]

    def tearDown(self):
        self.data_dir_patch.stop()
        self.db_path_patch.stop()
        self.temp_dir.cleanup()

    def test_issue_and_return(self):
        result = services.issue_book(
            self.book_id, self.member_ids[0], self.today
        )
        self.assertEqual(
            result["due_at"], "2026-11-11"
        )

        returned = services.return_book(
            result["loan_id"], self.today
        )
        self.assertEqual(returned["fine_amount"], 0)

        availability = services.get_book_availability(
            self.book_id
        )
        self.assertEqual(availability["available_copies"], 2)

    def test_overdue_fine(self):
        loan = services.issue_book(
            self.book_id, self.member_ids[0], self.today
        )

        result = services.return_book(
            loan["loan_id"], date(2026, 11, 14)
        )

        # Due Nov 11; returned Nov 14: 3 days late.
        self.assertEqual(result["overdue_days"], 3)
        self.assertEqual(result["fine_amount"], 15)

    def test_three_loan_limit(self):
        other_book_ids = [
            services.add_book(
                f"Book {i}", "Author", "Testing",
                total_copies=1,
                isbn=f"OTHER-{i}",
            )
            for i in range(1, 4)
        ]

        for book_id in other_book_ids:
            services.issue_book(
                book_id, self.member_ids[0], self.today
            )

        with self.assertRaises(services.ServiceError):
            services.issue_book(
                self.book_id, self.member_ids[0], self.today
            )

    def test_reservation_queue(self):
        # Borrow both available copies.
        first = services.issue_book(
            self.book_id, self.member_ids[0], self.today
        )
        services.issue_book(
            self.book_id, self.member_ids[1], self.today
        )

        reservation = services.reserve_book(
            self.book_id, self.member_ids[2], self.today
        )
        self.assertEqual(reservation["position"], 1)

        returned = services.return_book(
            first["loan_id"], self.today
        )

        self.assertIsNotNone(returned["allocation"])
        self.assertEqual(
            returned["allocation"]["member_id"],
            self.member_ids[2],
        )

    def test_duplicate_return_rejected(self):
        loan = services.issue_book(
            self.book_id, self.member_ids[0], self.today
        )
        services.return_book(loan["loan_id"], self.today)

        with self.assertRaises(services.ServiceError):
            services.return_book(loan["loan_id"], self.today)


if __name__ == "__main__":
    unittest.main(verbosity=2)
