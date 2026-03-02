#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$SCRIPT_DIR/data"

PEOPLE_URL="https://data.openstates.org/people/current/ma.csv"

SESSIONS="
190th https://data.openstates.org/csv/latest/MA_190th_csv_1TFMZb8hJsBomdyU6qXxza.zip
191st https://data.openstates.org/csv/latest/MA_191st_csv_4Xtejhb3bVqc0iWiZQ9Thp.zip
192nd https://data.openstates.org/csv/latest/MA_192nd_csv_4xpxOsCWrwbRe1S1KGZPJ3.zip
193rd https://data.openstates.org/csv/latest/MA_193rd_csv_6sacQoaVre3aZu9LulB2wP.zip
194th https://data.openstates.org/csv/latest/MA_194th_csv_1RoyyywZ4qh3xxv7F8SO3Q.zip
"

# Download people.csv
echo "Downloading people.csv..."
curl -fSL "$PEOPLE_URL" -o "$DATA_DIR/people.csv"
echo "  -> $DATA_DIR/people.csv"

# Download and extract each legislative session
echo "$SESSIONS" | while read -r session url; do
    [ -z "$session" ] && continue
    dest="$DATA_DIR/MA/$session"
    tmp_zip="$DATA_DIR/MA/${session}.zip"

    echo "Downloading $session session..."
    mkdir -p "$dest"
    curl -fSL "$url" -o "$tmp_zip"
    unzip -o "$tmp_zip" -d "$dest"
    rm "$tmp_zip"
    echo "  -> $dest/"
done

echo "Done."
