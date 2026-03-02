#!/usr/bin/env python3
"""Load MA legislation CSVs into a SQLite database."""

import csv
import sqlite3
from pathlib import Path

DB_PATH = Path("ma_legislation.db")
DATA_DIR = Path("data")

SCHEMA = """
CREATE TABLE people (
    id TEXT PRIMARY KEY,
    name TEXT,
    current_party TEXT,
    current_district TEXT,
    current_chamber TEXT,
    given_name TEXT,
    family_name TEXT,
    gender TEXT,
    email TEXT,
    biography TEXT,
    birth_date TEXT,
    death_date TEXT,
    image TEXT,
    links TEXT,
    sources TEXT,
    capitol_address TEXT,
    capitol_voice TEXT,
    capitol_fax TEXT,
    district_address TEXT,
    district_voice TEXT,
    district_fax TEXT,
    twitter TEXT,
    youtube TEXT,
    instagram TEXT,
    facebook TEXT,
    wikidata TEXT
);

CREATE TABLE organizations (
    id TEXT PRIMARY KEY,
    name TEXT,
    classification TEXT,
    parent_id TEXT,
    jurisdiction_id TEXT,
    created_at TEXT,
    updated_at TEXT,
    extras TEXT
);

CREATE TABLE bills (
    id TEXT PRIMARY KEY,
    identifier TEXT,
    title TEXT,
    classification TEXT,
    subject TEXT,
    session_identifier TEXT,
    jurisdiction TEXT,
    organization_classification TEXT
);

CREATE TABLE bill_abstracts (
    id TEXT PRIMARY KEY,
    bill_id TEXT REFERENCES bills(id),
    abstract TEXT,
    note TEXT
);

CREATE TABLE bill_actions (
    id TEXT PRIMARY KEY,
    bill_id TEXT REFERENCES bills(id),
    organization_id TEXT,
    description TEXT,
    date TEXT,
    classification TEXT,
    "order" INTEGER
);

CREATE TABLE bill_sponsorships (
    id TEXT PRIMARY KEY,
    name TEXT,
    entity_type TEXT,
    organization_id TEXT,
    person_id TEXT,
    bill_id TEXT REFERENCES bills(id),
    "primary" TEXT,
    classification TEXT
);

CREATE TABLE bill_versions (
    id TEXT PRIMARY KEY,
    bill_id TEXT REFERENCES bills(id),
    note TEXT,
    date TEXT,
    classification TEXT,
    extras TEXT
);

CREATE TABLE bill_version_links (
    id TEXT PRIMARY KEY,
    media_type TEXT,
    url TEXT,
    version_id TEXT REFERENCES bill_versions(id)
);

CREATE TABLE bill_related_bills (
    id TEXT PRIMARY KEY,
    bill_id TEXT REFERENCES bills(id),
    related_bill_id TEXT,
    identifier TEXT,
    legislative_session TEXT,
    relation_type TEXT
);

CREATE TABLE bill_sources (
    id TEXT PRIMARY KEY,
    note TEXT,
    url TEXT,
    bill_id TEXT REFERENCES bills(id)
);
"""

# Map CSV filename patterns to table names
CSV_TO_TABLE = {
    "bills": "bills",
    "bill_abstracts": "bill_abstracts",
    "bill_actions": "bill_actions",
    "bill_sources": "bill_sources",
    "bill_sponsorships": "bill_sponsorships",
    "bill_versions": "bill_versions",
    "bill_version_links": "bill_version_links",
    "bill_related_bills": "bill_related_bills",
    "organizations": "organizations",
}


def get_table_columns(conn, table):
    """Get column names for a table."""
    cursor = conn.execute(f"PRAGMA table_info(\"{table}\")")
    return [row[1] for row in cursor.fetchall()]


def load_csv(conn, csv_path, table):
    """Load a CSV file into the specified table."""
    table_cols = get_table_columns(conn, table)
    row_count = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return 0
        # Only use columns that exist in both the CSV and the table
        csv_cols = [c for c in reader.fieldnames if c in table_cols]
        quoted = [f'"{c}"' for c in csv_cols]
        placeholders = ",".join(["?"] * len(csv_cols))
        sql = f"INSERT OR REPLACE INTO \"{table}\" ({','.join(quoted)}) VALUES ({placeholders})"
        for row in reader:
            values = [row[c] for c in csv_cols]
            conn.execute(sql, values)
            row_count += 1
    return row_count


def find_session_csvs(session_dir):
    """Find CSV files for a session, handling nested directory structure."""
    # The zip extracts with nested MA/<session>/ inside
    session_name = session_dir.name
    nested = session_dir / "MA" / session_name
    if nested.is_dir():
        csvs = list(nested.glob("*.csv"))
        if csvs:
            return csvs
    # Fall back to top-level CSVs
    return list(session_dir.glob("*.csv"))


def csv_to_table(csv_path):
    """Map a CSV filename to its table name (longest suffix match)."""
    name = csv_path.stem  # e.g. MA_194th_bill_actions
    best = None
    best_len = 0
    for pattern, table in CSV_TO_TABLE.items():
        if name.endswith(pattern) and len(pattern) > best_len:
            best = table
            best_len = len(pattern)
    return best


def main():
    conn = sqlite3.connect(DB_PATH)
    # Defer FK checks until after all data is loaded
    conn.execute("PRAGMA foreign_keys = OFF")

    # Drop all tables and recreate
    for line in SCHEMA.split(";"):
        table_match = line.strip()
        if "CREATE TABLE" in table_match:
            table_name = table_match.split("CREATE TABLE")[1].split("(")[0].strip()
            conn.execute(f'DROP TABLE IF EXISTS "{table_name}"')
    conn.executescript(SCHEMA)

    counts = {}

    # Load people
    people_csv = DATA_DIR / "people.csv"
    if people_csv.exists():
        n = load_csv(conn, people_csv, "people")
        counts["people"] = n

    # Load session data
    ma_dir = DATA_DIR / "MA"
    if ma_dir.is_dir():
        for session_dir in sorted(ma_dir.iterdir()):
            if not session_dir.is_dir():
                continue
            csvs = find_session_csvs(session_dir)
            for csv_path in csvs:
                table = csv_to_table(csv_path)
                if table is None:
                    continue
                n = load_csv(conn, csv_path, table)
                counts[table] = counts.get(table, 0) + n

    conn.commit()
    conn.execute("PRAGMA foreign_keys = ON")

    # Print summary
    print(f"Database: {DB_PATH}")
    print(f"{'Table':<25} {'Rows':>10}")
    print("-" * 37)
    for table in ["people", "organizations", "bills", "bill_abstracts",
                   "bill_actions", "bill_sponsorships", "bill_versions",
                   "bill_version_links", "bill_related_bills", "bill_sources"]:
        cursor = conn.execute(f'SELECT COUNT(*) FROM "{table}"')
        n = cursor.fetchone()[0]
        print(f"{table:<25} {n:>10,}")

    conn.close()


if __name__ == "__main__":
    main()
