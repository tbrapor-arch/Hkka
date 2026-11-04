#!/usr/bin/env python3
"""Export the Sixian core list (v_core) to CSV: python3 -I tools/export.py data/build/hakka.db data/build/sixian_core.csv"""
import csv, sqlite3, sys
db = sqlite3.connect(sys.argv[1])
cur = db.execute("SELECT * FROM v_core")
with open(sys.argv[2], "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow([d[0] for d in cur.description]); n = 0
    for r in cur:
        w.writerow(r); n += 1
print(f"{n} rows → {sys.argv[2]}")
