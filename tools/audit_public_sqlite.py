#!/usr/bin/env python3
"""Report SQLite schema and aggregate privacy indicators without printing row values."""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path
from urllib.parse import quote

SENSITIVE_NAME = re.compile(
    r"(?:^|_)(?:email|phone|mobile|username|first_name|last_name|full_name|"
    r"display_name|address|client|patient|appointment|chat|message|note|"
    r"symptom|diagnos(?:is)?|birth|dob|user_id|profile|contact|session|consent|ip)(?:_|$)",
    re.IGNORECASE,
)
CREDENTIAL_NAME = re.compile(r"(password|secret|token|api[_-]?key|credential)", re.IGNORECASE)
EMAIL = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
PHONE = re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}(?!\d)")
MAX_VALUES_PER_COLUMN = 100_000


def quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def scan_database(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    uri = "file:" + quote(str(path.resolve())) + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    tables = []
    total_rows = 0
    review_fields = []
    credential_fields = []
    scan_incomplete = False
    try:
        table_names = [
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        for table_name in table_names:
            table_sql = quote_identifier(table_name)
            row_count = connection.execute(f"SELECT COUNT(*) FROM {table_sql}").fetchone()[0]
            total_rows += row_count
            columns = []
            for column in connection.execute(f"PRAGMA table_info({table_sql})"):
                column_name = column["name"]
                column_type = (column["type"] or "").upper()
                item = {"name": column_name, "type": column_type}
                if CREDENTIAL_NAME.search(column_name):
                    column_sql = quote_identifier(column_name)
                    nonempty = connection.execute(
                        f"SELECT COUNT(*) FROM {table_sql} "
                        f"WHERE {column_sql} IS NOT NULL AND TRIM(CAST({column_sql} AS TEXT)) <> ''"
                    ).fetchone()[0]
                    credential_fields.append({
                        "table": table_name,
                        "column": column_name,
                        "nonempty_values": nonempty,
                        "values_read": False,
                    })
                if SENSITIVE_NAME.search(column_name):
                    column_sql = quote_identifier(column_name)
                    nonempty = connection.execute(
                        f"SELECT COUNT(*) FROM {table_sql} "
                        f"WHERE {column_sql} IS NOT NULL AND TRIM(CAST({column_sql} AS TEXT)) <> ''"
                    ).fetchone()[0]
                    email_matches = 0
                    phone_matches = 0
                    scanned = 0
                    if nonempty:
                        cursor = connection.execute(
                            f"SELECT CAST({column_sql} AS TEXT) FROM {table_sql} "
                            f"WHERE {column_sql} IS NOT NULL AND TRIM(CAST({column_sql} AS TEXT)) <> '' "
                            f"LIMIT {MAX_VALUES_PER_COLUMN + 1}"
                        )
                        for value_row in cursor:
                            scanned += 1
                            value = value_row[0] or ""
                            email_matches += bool(EMAIL.search(value))
                            phone_matches += bool(PHONE.search(value))
                        if scanned > MAX_VALUES_PER_COLUMN:
                            scan_incomplete = True
                            scanned = MAX_VALUES_PER_COLUMN
                    item.update({
                        "nonempty_values": nonempty,
                        "email_pattern_rows": email_matches,
                        "phone_pattern_rows": phone_matches,
                        "scanned_values": scanned,
                    })
                    if nonempty:
                        review_fields.append({
                            "table": table_name,
                            "column": column_name,
                            "nonempty_values": nonempty,
                            "email_pattern_rows": email_matches,
                            "phone_pattern_rows": phone_matches,
                        })
                columns.append(item)
            tables.append({"name": table_name, "row_count": row_count, "columns": columns})
    finally:
        connection.close()

    return {
        "database": path.name,
        "classification": "metadata_only_not_a_content_or_consent_review",
        "database_contains_records": total_rows > 0,
        "total_rows": total_rows,
        "tables": tables,
        "nonempty_sensitive_shaped_fields": review_fields,
        "credential_columns": credential_fields,
        "manual_privacy_review_required": bool(review_fields) or bool(credential_fields) or scan_incomplete,
        "scan_incomplete": scan_incomplete,
        "values_printed": False,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: audit_public_sqlite.py PATH", file=sys.stderr)
        return 2
    report = scan_database(Path(sys.argv[1]))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
