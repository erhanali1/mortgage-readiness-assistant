"""Load synthetic mortgage applications from CSV."""

from __future__ import annotations

import csv
from pathlib import Path

BOOLEAN_FIELDS = (
    "income_verified",
    "identity_verified",
    "credit_authorized",
    "purchase_contract",
    "appraisal_complete",
    "insurance_verified",
    "disclosures_signed",
)

INTEGER_FIELDS = ("days_in_stage", "last_contact_days")


def parse_bool(value: str) -> bool:
    normalized = str(value).strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"Expected true/false, got {value!r}")


def parse_int(value: str) -> int:
    return int(str(value).strip())


def coerce_row(row: dict) -> dict:
    parsed = dict(row)
    for field in BOOLEAN_FIELDS:
        if field in parsed:
            parsed[field] = parse_bool(parsed[field])
    for field in INTEGER_FIELDS:
        if field in parsed:
            parsed[field] = parse_int(parsed[field])
    return parsed


def load_applications(csv_path: str | Path) -> list[dict]:
    path = Path(csv_path)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [coerce_row(row) for row in reader]
