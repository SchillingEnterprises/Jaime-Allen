import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from audit_public_sqlite import scan_database


class PublicSQLiteAuditTests(unittest.TestCase):
    def test_reports_aggregate_privacy_indicators_without_values(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "sample.sqlite3"
            connection = sqlite3.connect(database)
            connection.execute("CREATE TABLE contacts (id INTEGER PRIMARY KEY, email TEXT, note TEXT, password TEXT)")
            connection.execute("INSERT INTO contacts (email, note, password) VALUES (?, ?, ?)", ("person@example.test", "private note text", "not-a-real-hash"))
            connection.commit()
            connection.close()

            report = scan_database(database)
            serialized = json.dumps(report)

            self.assertTrue(report["database_contains_records"])
            self.assertTrue(report["manual_privacy_review_required"])
            self.assertEqual(report["total_rows"], 1)
            self.assertEqual(report["nonempty_sensitive_shaped_fields"][0]["email_pattern_rows"], 1)
            self.assertTrue(any(field["column"] == "password" and field["nonempty_values"] == 1 for field in report["credential_columns"]))
            self.assertFalse(report["values_printed"])
            self.assertNotIn("person@example.test", serialized)
            self.assertNotIn("private note text", serialized)
            self.assertNotIn("not-a-real-hash", serialized)

    def test_empty_database_does_not_report_populated_sensitive_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "empty.sqlite3"
            connection = sqlite3.connect(database)
            connection.execute("CREATE TABLE clients (id INTEGER PRIMARY KEY, email TEXT)")
            connection.commit()
            connection.close()

            report = scan_database(database)
            self.assertFalse(report["database_contains_records"])
            self.assertFalse(report["manual_privacy_review_required"])
            self.assertEqual(report["nonempty_sensitive_shaped_fields"], [])


if __name__ == "__main__":
    unittest.main()
