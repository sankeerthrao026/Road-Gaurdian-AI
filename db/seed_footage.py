"""
db/seed_footage.py
------------------
Populates the cctv_footage PostgreSQL table from the existing car_accidents/ folder.
Run once:
    python db/seed_footage.py
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

import psycopg2

DB_URL = os.getenv("DATABASE_URL", "")
if not DB_URL:
    print("ERROR: DATABASE_URL is not set in .env")
    sys.exit(1)

VIDEOS_DIR = BASE_DIR / "car_accidents"
SUPPORTED   = {".mp4", ".avi", ".mov", ".mkv"}

conn = psycopg2.connect(DB_URL, connect_timeout=10)
conn.autocommit = True
cur  = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS cctv_footage (
    id           SERIAL PRIMARY KEY,
    filename     TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    storage_key  TEXT NOT NULL,
    size_mb      NUMERIC(10,2),
    created_at   TIMESTAMPTZ DEFAULT now()
);
""")
print("Table cctv_footage: OK")

inserted = 0
for f in sorted(VIDEOS_DIR.iterdir()):
    if not (f.is_file() and f.suffix.lower() in SUPPORTED):
        continue

    filename     = f.name
    display_name = f.stem
    storage_key  = f"car_accidents/{filename}"
    size_mb      = round(f.stat().st_size / (1024 * 1024), 2)

    cur.execute("""
        INSERT INTO cctv_footage (filename, display_name, storage_key, size_mb)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (filename) DO UPDATE
            SET display_name = EXCLUDED.display_name,
                storage_key  = EXCLUDED.storage_key,
                size_mb      = EXCLUDED.size_mb;
    """, (filename, display_name, storage_key, size_mb))

    print(f"  >> {filename}  ({size_mb} MB)  key={storage_key}")
    inserted += 1

cur.execute("SELECT COUNT(*) FROM cctv_footage")
total = cur.fetchone()[0]

conn.close()
print(f"\nDone. {inserted} rows upserted. Total rows in cctv_footage: {total}")
