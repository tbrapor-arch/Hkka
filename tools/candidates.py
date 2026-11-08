#!/usr/bin/env python3
"""Check candidate words for a lesson in one pass (as Tsheh-tû's candidates.py).

  python3 -I tools/candidates.py 飛機場 捷運 擋仔 … [ex=N]

For each word: its Sixian readings and level in the 115年度 / 2013 lists (else the MOE dictionary), the Mandarin and
English glosses, whether a lesson already declares it (and where), how many official Sixian sentences contain it,
and the first N of them (default 1) with their pinyin. Official = kaga115 + kaga (see the counting rule in
course/batches/checklist.md); MOE examples are counted apart.
"""
import glob
import os
import sqlite3
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
con = sqlite3.connect(os.path.join(ROOT, "data/build/hakka.db"))

args = [a for a in sys.argv[1:] if not a.startswith("ex=")]
nex = int(next((a[3:] for a in sys.argv[1:] if a.startswith("ex=")), 1))

declared = {}
for f in (sorted(glob.glob(os.path.join(ROOT, "course/lessons/[0-9]*.yaml")))
          + sorted(glob.glob(os.path.join(ROOT, "course/perfectionnement/[0-9]*.yaml")))):
    d = yaml.safe_load(open(f, encoding="utf-8"))
    tag = ("P" if "perfectionnement" in f else "") + str(d.get("id"))
    for w in d.get("new_words") or []:
        declared.setdefault(w["hanzi"], []).append(f"{tag}:{w.get('pinyin')}")

for w in args:
    rows = con.execute("SELECT source, pinyin, level, mandarin, english, cognate FROM entry WHERE hanzi=? AND accent='sixian' "
                       "AND source IN ('kaga115','kaga') ORDER BY source DESC", (w,)).fetchall()
    if not rows:
        rows = con.execute("SELECT 'moe', group_concat(r.pinyin, ' / '), '', e.mandarin, e.english, e.cognate FROM entry e "
                           "JOIN reading r ON r.entry_id=e.id AND r.accent='sixian' WHERE e.hanzi=? AND e.source='moe' "
                           "GROUP BY e.id", (w,)).fetchall()
    head = "; ".join(f"{s} {p} {l or ''} = {m or ''} | {e or ''} [{c or ''}]" for s, p, l, m, e, c in rows) or "NOT FOUND"
    off = con.execute("SELECT hanzi, pinyin FROM example WHERE source IN ('kaga115','kaga') AND accent='sixian' "
                      "AND hanzi LIKE ? ORDER BY source DESC, length(hanzi)", (f"%{w}%",)).fetchall()
    moe = con.execute("SELECT count(*) FROM example WHERE source='moe' AND hanzi LIKE ?", (f"%{w}%",)).fetchone()[0]
    dec = f"  DECLARED {', '.join(declared[w])}" if w in declared else ""
    print(f"{w}: {head}{dec}\n   official {len(off)}, moe {moe}")
    for h, p in off[:nex]:
        print(f"   · {h}  {p or ''}")
