#!/usr/bin/env python3
"""Check (hanzi, reading) pairs against the official lists and the MOE dictionary; print a short list of suspects.
Ported from Tsheh-tû's tools/verify_words.py (branch dict-db), for Hakka: two accents, the 115年度 lists first.

  python3 -I tools/verify_words.py                     the course: every lesson's new_words (Sixian and Hailu) and
                                                       course/supplement.yaml   (`make lint` runs this)
  python3 -I tools/verify_words.py pairs.tsv           hanzi <TAB> pinyin [<TAB> label [<TAB> accent]], one per line
  python3 -I tools/verify_words.py --supplement PATH   another supplement file (the private books' one)
  options: --all (every suspect, not the first 40 of each class)
From Python (the private books reader runs it on every word of every chapter):
  import verify_words; V = verify_words.Verifier(); V.add(hanzi, pinyin, label, accent); V.report()

Accepted readings of a word, in order: the 115年度 lists, the 2013 lists, the MOE dictionary (its readings for that
accent, and the variants these sources give). A reading also counts as right when it is a listed reading written with
its spoken tones (tools/sandhi.py: Sixian 陰平 24 → 11 before 24, 55, 5; 仔 → eˇ; Hailu 上聲 → 33, 陰入 → 2), or the
reverse (the lists write some words with sandhi tones: 丈人 congˊ minˊ).

Suspect classes, most serious first:
  course      the course's new_words declare the word with another reading (books and supplement only)
  differs     the sources have the word, none with these syllables (both shown)
  tone        the same syllables as a listed reading, other tones (a typo, or a reading to check by ear)
  no-dict     no source has the word, and a character is read with a syllable no source gives it
Not suspects, only counted (listed with --all): `older`, the 115年度 lists have the word with another reading and
only the 2013 list or MOE agrees (often a second reading: 話 fa / va); `composed`, a word in no source whose
characters all have their reading elsewhere. "Variant" readings (a word the sources list under another spelling)
count with MOE.
Nothing here changes any file.
"""
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pinyin as py  # noqa: E402
import sandhi  # noqa: E402
from cards import ACC, DB, PARTICLES, ROOT, SUPPLEMENT, load_lessons  # noqa: E402

CLASSES = [("course", "the course teaches the word with another reading"),
           ("differs", "reading differs from every source"), ("tone", "only the tones differ"),
           ("no-dict", "in no source, and a character's syllable is unattested")]
# not suspects (a second reading the dictionary gives, often 文白 or an accent's own form): counted, listed with --all
NOTES = [("older", "the 115年度 lists read it otherwise; the 2013 list or MOE agrees")]


def toneless(k):
    return "-".join(re.sub(r"\d+$", "", s) for s in k.split("-"))


def spoken(k, acc):
    sv = [(re.sub(r"\d+$", "", s), (re.search(r"\d+$", s) or [None])[0]) for s in k.split("-")]
    out = sandhi.apply_hailu(sv) if acc == "hailu" else sandhi.apply(sv)
    return "-".join(f"{s}{v or ''}" for s, v in out)


class Verifier:
    def __init__(self, db=DB):
        con = sqlite3.connect(db)
        self.src = {a: defaultdict(lambda: defaultdict(set)) for a in ACC.values()}   # acc -> hanzi -> source -> {key}
        self.char = {a: defaultdict(set) for a in ACC.values()}                        # acc -> char -> {toneless syllable}
        for acc in ACC.values():
            rows = list(con.execute(
                "SELECT source, hanzi, pkey FROM entry WHERE source IN ('kaga115','kaga') AND accent=? AND pkey != '' "
                "UNION SELECT 'moe', e.hanzi, r.pkey FROM entry e JOIN reading r ON r.entry_id=e.id WHERE r.accent=? "
                "UNION SELECT 'variant', v.hanzi, e.pkey FROM variant v JOIN entry e ON e.id=v.entry_id "
                "  WHERE e.accent=? AND v.hanzi IS NOT NULL AND length(v.hanzi) = length(e.hanzi) "
                "UNION SELECT e.source, e.hanzi, v.pkey FROM variant v JOIN entry e ON e.id=v.entry_id "
                "  WHERE e.accent=? AND v.pkey IS NOT NULL", (acc,) * 4))
            for s, h, k in rows:
                if not (h and k) or (s == "variant" and len(h) != len(k.split("-"))):
                    continue
                self.src[acc][h][s].add(k)
                parts = k.split("-")
                if len(parts) == len(h):
                    for c, p in zip(h, parts):
                        self.char[acc][c].add(re.sub(r"\d+$", "", p))
            for h, k in PARTICLES[acc].items():
                self.src[acc][h]["particle"].add(k)
                self.char[acc][h].add(re.sub(r"\d+$", "", k))
        self.course = {a: defaultdict(dict) for a in ACC.values()}   # acc -> hanzi -> {key: lesson} (new_words)
        for d in load_lessons(ROOT):
            lab = f"P{d['id']}" if d["_p2"] else f"L{d['id']}"
            for w in d.get("new_words") or []:
                for acc, b in (("sixian", w), ("hailu", w.get("hl") or {})):
                    k = py.key(b.get("pinyin", ""), acc)
                    if b.get("hanzi") and k:
                        self.course[acc][b["hanzi"]].setdefault(k, lab)
        self.items = {}          # (acc, hanzi, key) -> [labels]
        self.shown = {}

    def add(self, hanzi, pinyin, label="", accent="sixian"):
        k = py.key(pinyin, accent)
        if not hanzi or not k or len(k.split("-")) != len(re.findall(r"[^\s…]", hanzi)):
            return
        self.items.setdefault((accent, hanzi, k), []).append(label)
        self.shown.setdefault((accent, hanzi, k), pinyin)

    def judge(self, acc, h, k):
        """-> (class or 'ok-…', detail)"""
        S = self.src[acc].get(h, {})
        allk = set().union(*S.values()) if S else set()
        sp = spoken(k, acc)
        def ok(keys):
            return k in keys or sp in keys or any(spoken(x, acc) == k for x in keys)
        if ok(S.get("kaga115", ())) or ok(S.get("particle", ())):
            return "ok-115", ""
        T = self.course[acc].get(h, {})
        if T and not ok(set(T)):
            return "course", "; ".join(f"{T[x]} {py.marked(x, acc)}" for x in T)
        listed = lambda: "; ".join(f"{s} {', '.join(py.marked(x, acc) for x in sorted(v))}" for s, v in S.items())
        if ok(allk):
            if S.get("kaga115"):
                return "older", listed()
            return ("ok-kaga" if ok(S.get("kaga", ())) else "ok-moe"), ""
        if ok(S.get("variant", ())):
            return "ok-moe", ""
        if S:
            if toneless(k) in {toneless(x) for x in allk}:
                return "tone", listed()
            return "differs", listed()
        bad = [f"{c} {s}" for c, s in zip(h, toneless(k).split("-")) if s not in self.char[acc].get(c, ())]
        if bad:
            return "no-dict", "unattested: " + ", ".join(bad)
        return "ok-composed", ""

    def report(self, limit=40, title="verify_words"):
        res = defaultdict(list)
        for (acc, h, k), labels in self.items.items():
            cl, det = self.judge(acc, h, k)
            res[cl].append((acc, h, k, det, labels))
        n = len(self.items)
        okc = Counter({c: len(v) for c, v in res.items() if c.startswith("ok")})
        sus = sum(len(res[c]) for c, _ in CLASSES)
        print(f"{title}: {n} words checked: {okc['ok-115']} as in the 115年度 lists, {okc['ok-kaga']} the 2013 list, "
              f"{okc['ok-moe']} MOE only, {len(res['older'])} another reading than 115年度 (2013 list or MOE agrees), "
              f"{okc['ok-composed']} composed from listed characters; {sus} suspect(s)")
        for c, label in CLASSES + (NOTES if not limit else []):
            rows = sorted(res[c], key=lambda r: (r[0], r[4][0], r[1]))
            if not rows:
                continue
            print(f"  [{c}] {label}: {len(rows)}")
            for acc, h, k, det, labels in rows[:limit if limit else None]:
                where = labels[0] + (f" (+{len(labels) - 1})" if len(labels) > 1 else "")
                print(f"    {h} {self.shown[(acc, h, k)]}{' (Hailu)' if acc == 'hailu' else ''}  {where}  — {det}")
            if limit and len(rows) > limit:
                print(f"    … {len(rows) - limit} more (--all)")
        return sus


def add_supplement(V, path, label=None):
    import yaml
    if not os.path.exists(path):
        return
    d = yaml.safe_load(open(path, encoding="utf-8")) or {}
    for sect, acc in (("words", "sixian"), ("hailu", "hailu")):
        for h, (p, _en) in (d.get(sect) or {}).items():
            V.add(h, p, label or os.path.relpath(path, ROOT), acc)


def add_course(V):
    for d in load_lessons(ROOT):
        lab = f"P{d['id']}" if d["_p2"] else f"L{d['id']}"
        for w in d.get("new_words") or []:
            V.add(w.get("hanzi", ""), w.get("pinyin", ""), lab, "sixian")
            hl = w.get("hl")
            if hl:
                V.add(hl.get("hanzi", ""), hl.get("pinyin", ""), lab, "hailu")
    add_supplement(V, SUPPLEMENT)


def main(argv):
    limit = 0 if "--all" in argv else 40
    argv = [a for a in argv if a != "--all"]
    V = Verifier()
    if not argv:
        add_course(V)
        V.report(limit, "verify_words (course new words + supplement)")
        return 0
    while argv:
        a = argv.pop(0)
        if a == "--supplement":
            add_supplement(V, argv.pop(0))
            continue
        f = sys.stdin if a == "-" else open(a, encoding="utf-8")
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 2 and not line.startswith("#"):
                V.add(p[0], p[1], p[2] if len(p) > 2 else a, p[3] if len(p) > 3 else "sixian")
    V.report(limit)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
