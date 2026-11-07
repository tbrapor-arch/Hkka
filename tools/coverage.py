#!/usr/bin/env python3
"""How much of the core vocabulary the written lessons cover, and what to teach next.

  python3 -I tools/coverage.py [N]     # summary, pacing per lesson, then the next N words to teach (default 40)

Next words are chosen like the syllabus: lowest certification level first (基礎級 → 初級 → 中級), and within a
level by frequency; Hakka-only words and false friends are listed first because they are the ones that need notes.
"""
import glob
import os
import sqlite3
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pinyin as py  # noqa: E402

ROOT = os.path.dirname(HERE)
con = sqlite3.connect(os.path.join(ROOT, "data/build/hakka.db"))
syl = {}
sp = os.path.join(ROOT, "course/syllabus.yaml")
if os.path.exists(sp):
    syl = {l["n"]: l for l in (yaml.safe_load(open(sp, encoding="utf-8")) or {}).get("lessons", [])}

taught, per_lesson = set(), []
for f in sorted(glob.glob(os.path.join(ROOT, "course/lessons/[0-9]*.yaml"))):
    d = yaml.safe_load(open(f, encoding="utf-8"))
    ks = {(w["hanzi"], py.key(w.get("pinyin", ""))) for w in d.get("new_words") or []}
    taught |= ks
    per_lesson.append((d.get("id"), len(ks), (syl.get(d.get("id")) or {}).get("new")))

core = con.execute("SELECT v.hanzi, v.pinyin, v.pkey, v.level, v.mandarin, e.cognate, e.english, "
                   "coalesce(e.glossika_freq, 0) * 10 + coalesce(e.corpus_freq, 0) AS f "
                   "FROM v_core v JOIN entry e USING(id) ORDER BY f DESC").fetchall()
print(f"lessons written: {len(per_lesson)}; words taught: {len(taught)}")
for lvl in ("基礎級", "初級", "中級"):
    part = [r for r in core if r[3] == lvl]
    got = sum((r[0], r[2]) in taught for r in part)
    print(f"  {lvl}: {got}/{len(part)} ({100 * got // max(1, len(part))}%)")
if per_lesson:
    print("\npacing (new words / target):")
    print("  " + "  ".join(f"{n}:{c}/{t or '-'}" for n, c, t in per_lesson))

want = int(sys.argv[1]) if len(sys.argv) > 1 else 40
order = {"基礎級": 0, "初級": 1, "中級": 2}
todo = [r for r in core if (r[0], r[2]) not in taught]
todo.sort(key=lambda r: (order.get(r[3], 9), r[5] not in ("hakka-only", "false-friend")))
print(f"\nnext {want} core words (level, then Hakka-only / false friends first, then frequency):")
for r in todo[:want]:
    print(f"  {r[3]} {r[0]} {r[1]}  = {r[4]}  [{r[5]}]  {r[6] or ''}")
