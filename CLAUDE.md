# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Massachusetts state legislation data collection and analysis project. Data is sourced from [Open States](https://data.openstates.org) and organized into CSV files for loading into a relational database.

## Data Layout

- `data/people.csv` — Current MA legislators (from Open States people endpoint)
- `data/MA/<session>/` — Per-session legislation data (e.g., `data/MA/194th/`)
  - Bills, actions, sponsorships, abstracts, versions, version links, related bills, sources, organizations

## Data Refresh

- People: download from `https://data.openstates.org/people/current/ma.csv` to `data/people.csv`
- Legislation: download zip from Open States, unzip into `data/MA/<session>/`

See README.md for session-specific download URLs.

## Database

- `python3 load_db.py` — Creates/rebuilds `ma_legislation.db` from CSVs (idempotent)
- `sqlite3 ma_legislation.db` — Query the database directly

## Key Relationships in the Data

- Bills link to people via `bill_sponsorships`
- Bills have temporal progression via `bill_actions`
- Bills cross-reference each other via `bill_related_bills`
- `organizations` contains House, Senate, and committee structure
- Bill identifiers: `S` prefix = Senate (upper), `H`/`HD` prefix = House (lower)
