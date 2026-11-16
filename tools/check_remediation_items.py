#!/usr/bin/env python3.13
"""Verify that every item the cross-reference table claims exists in the report.

The report is written in two places at once - a body of numbered sections and a
cross-reference table that maps item numbers to register entries. Those can drift: this
check exists because the body lost six items (12, 13, 17, 18, 19, 20) while the table
went on listing them, and nothing noticed.

Exit 0 when every table row has a matching "### N." heading and every heading has a row.
"""
import re
import sys
from pathlib import Path

REPORT = Path(__file__).resolve().parent.parent / "docs" / "REMEDIATION-REPORT.md"


def main() -> int:
    if not REPORT.is_file():
        print(f"  {REPORT} not found", file=sys.stderr)
        return 2
    text = REPORT.read_text()

    headings = set(re.findall(r"(?m)^### (\d+b?)\.", text))
    table = text[text.index("## Register cross-reference"):]
    rows = set(re.findall(r"(?m)^\| (\d+b?) ", table))

    missing_body = sorted(rows - headings, key=lambda s: (int(s.rstrip("b")), s))
    missing_row = sorted(headings - rows, key=lambda s: (int(s.rstrip("b")), s))

    print(f"  headings: {len(headings)}   table rows: {len(rows)}")
    if missing_body:
        print(f"  table lists items with NO section: {missing_body}")
    if missing_row:
        print(f"  sections with NO table row: {missing_row}")
    if missing_body or missing_row:
        print("RESULT: cross-reference and body disagree")
        return 1
    print("RESULT: every listed item has a section, and every section is listed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
