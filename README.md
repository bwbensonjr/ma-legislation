# Massachusetts Legislation 

Massachusetts legislation data and analysis

Download data about legislators and legislation and put into a
relational database.

## Database

Run `python3 load_db.py` to create (or rebuild) `ma_legislation.db` from the CSV files.

### Schema

```
people                  Current MA legislators
organizations           Chambers and committees (191st+)
bills                   Legislation filed across all sessions
bill_abstracts          Bill summaries
bill_actions            Actions taken on bills (hearings, votes, etc.)
bill_sponsorships       Sponsor/cosponsor relationships between legislators and bills
bill_versions           Text versions of bills
bill_version_links      URLs to bill version documents
bill_related_bills      Cross-references between bills (193rd+)
bill_sources            Source URLs for bill data
```

Key relationships:

- `bill_sponsorships.person_id` → `people.id`
- `bill_sponsorships.bill_id` → `bills.id`
- `bill_actions.bill_id` → `bills.id`
- `bill_versions.bill_id` → `bills.id`
- `bill_version_links.version_id` → `bill_versions.id`
- `bill_related_bills.bill_id` → `bills.id`

### Example Queries

Bills filed per session:

```sql
SELECT session_identifier, COUNT(*) AS bill_count
FROM bills
GROUP BY session_identifier
ORDER BY session_identifier;
```

Primary sponsorships and cosponsorships per legislator for a session:

```sql
SELECT p.name,
       SUM(CASE WHEN s."primary" = 'True' THEN 1 ELSE 0 END) AS primary_sponsor,
       SUM(CASE WHEN s."primary" = 'False' THEN 1 ELSE 0 END) AS cosponsor
FROM bill_sponsorships s
JOIN people p ON s.person_id = p.id
JOIN bills b ON s.bill_id = b.id
WHERE b.session_identifier = '194th'
GROUP BY p.id
ORDER BY primary_sponsor DESC;
```

Bills with the most cosponsors in a session:

```sql
SELECT b.identifier, b.title, COUNT(*) AS cosponsor_count
FROM bill_sponsorships s
JOIN bills b ON s.bill_id = b.id
WHERE s."primary" = 'False'
  AND b.session_identifier = '194th'
GROUP BY b.id
ORDER BY cosponsor_count DESC
LIMIT 10;
```

Timeline of actions on a specific bill:

```sql
SELECT date, description, classification
FROM bill_actions
WHERE bill_id = (SELECT id FROM bills WHERE identifier = 'H 1234' AND session_identifier = '194th')
ORDER BY "order";
```

## Open States

Data source and repository location

- [People](https://data.openstates.org/people/current/ma.csv) - Download to `data/people.csv`
- Legislation - Unzip into `data/MA/<session>/<files>`
  - [Massachusetts 190th Legislature (2017-2018)](https://data.openstates.org/csv/latest/MA_190th_csv_1TFMZb8hJsBomdyU6qXxza.zip)
  - [Massachusetts 191st Legislature (2019-2020)](https://data.openstates.org/csv/latest/MA_191st_csv_4Xtejhb3bVqc0iWiZQ9Thp.zip)
  - [Massachusetts 192nd Legislature (2021-2022)](https://data.openstates.org/csv/latest/MA_192nd_csv_4xpxOsCWrwbRe1S1KGZPJ3.zip)
  - [Massachusetts 193rd Legislature (2023-2024)](https://data.openstates.org/csv/latest/MA_193rd_csv_6sacQoaVre3aZu9LulB2wP.zip)
  - [Massachusetts 194th Legislature (2025-2026)](https://data.openstates.org/csv/latest/MA_194th_csv_1RoyyywZ4qh3xxv7F8SO3Q.zip)

