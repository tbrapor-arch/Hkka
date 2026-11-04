#!/usr/bin/env python3
"""Look a word up in data/build/hakka.db.
  make lookup W=今晡日       characters (Hakka or Mandarin gloss)
  make lookup W=gimˊbuˊ     MOE pinyin with tone marks, or numbers (gim24bu24); no tone = any tone
"""
import re, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pinyin as py  # noqa: E402


def main(dbp, w):
    db = sqlite3.connect(dbp)
    py.set_inventory({r[0] for r in db.execute("SELECT syl FROM syllable")})
    if re.search(r"[a-z]", w.lower()):
        has_tone = bool(re.search(r"[ˊˇˋ\d¹²³⁴⁵]", w))
        col, val = ("pkey", py.key(w)) if has_tone else ("toneless", py.toneless(w))
        rows = db.execute(f"SELECT id FROM entry WHERE {col} = ? UNION SELECT entry_id FROM reading WHERE pkey = ? AND accent='sixian'", (val, val)).fetchall()
    else:
        rows = db.execute("SELECT id FROM entry WHERE hanzi = ? OR mandarin = ? OR mandarin LIKE ? LIMIT 40",
                          (w, w, f"%{w}%")).fetchall()
    ids = [r[0] for r in rows]
    if not ids:
        print("not found"); return
    for (eid,) in rows:
        e = db.execute("SELECT source, hanzi, accent, pinyin, pkey, level, category, mandarin, english, glossika_freq FROM entry WHERE id=?", (eid,)).fetchone()
        src, hz, acc, pin, key, lvl, cat, man, en, gf = e
        if src == "kaga" and acc != "sixian":
            continue
        print(f"\n{hz}  {pin or ''}   [{src}{' ' + lvl if lvl else ''}{' · ' + cat if cat else ''}]  {key or ''}")
        if man or en:
            print(f"   華 {man or ''}   EN {en or ''}")
        for acc2, p in db.execute("SELECT accent, pinyin FROM reading WHERE entry_id=?", (eid,)):
            print(f"   {acc2:13} {p}")
        for pos, d in db.execute("SELECT pos, definition_zh FROM sense WHERE entry_id=? ORDER BY ord", (eid,)):
            print(f"   ({pos or '-'}) {d}")
        for hzx, man2 in db.execute("SELECT hanzi, mandarin FROM example WHERE entry_id=? LIMIT 3", (eid,)):
            print(f"   例 {hzx}  —  {man2}")
        if gf:
            print(f"   Glossika: {gf}×")
    try:
        sent = db.execute("SELECT g.id, g.sx_hanzi, g.en FROM glossika g JOIN glossika_word w ON w.sentence_id=g.id "
                          "WHERE w.hanzi=? GROUP BY g.id LIMIT 3", (w,)).fetchall()
        for sid, hzx, en in sent:
            print(f"   G#{sid} {hzx}  —  {en}")
    except sqlite3.OperationalError:
        pass


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
