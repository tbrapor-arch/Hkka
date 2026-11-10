#!/usr/bin/env python3
"""The accent bridge (between lesson 100 and 進修 1): how to get from Sixian to the other accents of Taiwan.

  python3 -I tools/bridge.py report [ACCENT]   # the measured correspondences, to read before editing the notes
  python3 -I tools/bridge.py build             # course/bridge/notes.yaml + the data → course/bridge/B1…B5.md

Everything in a bridge lesson that is a number, a word pair or a sentence is taken from the database by this script.
The hand-written part (what to say about each accent) is in course/bridge/notes.yaml.

Data:
  sounds    hailu, dapu, raoping, zhaoan: the 115年度 certification lists, the same word (same number, same
            characters, same number of syllables) in Sixian and in the accent, syllable by syllable.
            south-sixian: the MOE dictionary, which gives both readings for an entry.
  words     the same list number with other characters = another word. Only words taught in Part 1 are shown.
  sentences 客語百句 (2012 and 2014 sets): the same sentence in six accents, each with a recording.
"""
import glob
import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pinyin as py  # noqa: E402

ROOT = os.path.dirname(HERE)
DB = os.path.join(ROOT, "data/build/hakka.db")
OUT = os.path.join(ROOT, "course/bridge")
ACCENTS = ["hailu", "south-sixian", "dapu", "raoping", "zhaoan"]
NAMES = {"sixian": "Sixian 四縣", "hailu": "Hailu 海陸", "south-sixian": "South Sixian 南四縣", "dapu": "Dapu 大埔",
         "raoping": "Raoping 饒平", "zhaoan": "Zhao'an 詔安"}
INITIALS = ["zh", "ch", "sh", "rh", "ng", "bb", "b", "p", "m", "f", "v", "d", "t", "n", "l", "g", "k", "h", "z", "c",
            "s", "j", "q", "x"]
SX_TONES = [("24", False, "陰平 ˊ 24"), ("11", False, "陽平 ˇ 11"), ("31", False, "上聲 ˋ 31"), ("55", False, "去聲 55"),
            ("2", True, "陰入 ˋ 2"), ("5", True, "陽入 5")]


def short(acc):
    return NAMES[acc].rsplit(" ", 1)[0]


def split(syl):
    """'zhong' → ('zh', 'ong'); a syllabic nasal ('ng', 'm', 'hn') has no initial."""
    for i in INITIALS:
        if syl.startswith(i) and len(syl) > len(i):
            return i, syl[len(i):]
    return "", syl


def taught_part1():
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "course/lessons/[0-9]*.yaml"))):
        d = yaml.safe_load(open(f, encoding="utf-8"))
        for w in d.get("new_words") or []:
            out.setdefault((w["hanzi"], py.key(w.get("pinyin", ""))), (d["id"], w.get("en", "")))
    return out


def pairs(con, acc):
    """[(hanzi_sx, pinyin_sx, hanzi_acc, pinyin_acc, level, freq)] for the same list entry."""
    if acc == "south-sixian":
        q = ("SELECT e.hanzi, a.pinyin, e.hanzi, b.pinyin, '', 0 FROM entry e "
             "JOIN reading a ON a.entry_id = e.id AND a.accent = 'sixian' "
             "JOIN reading b ON b.entry_id = e.id AND b.accent = 'south-sixian' WHERE length(e.hanzi) <= 4")
    else:
        q = ("SELECT s.hanzi, s.pinyin, o.hanzi, o.pinyin, s.level, "
             "coalesce(s.glossika_freq, 0) * 10 + coalesce(s.corpus_freq, 0) FROM entry s "
             "JOIN entry o ON o.source = 'kaga115' AND o.accent = ? AND o.src_id = s.src_id "
             "WHERE s.source = 'kaga115' AND s.accent = 'sixian' AND s.pinyin != '' AND o.pinyin != ''")
    return con.execute(q, () if acc == "south-sixian" else (acc,)).fetchall()


T1 = None


def lesson_of(hz, ps):
    global T1
    if T1 is None:
        T1 = taught_part1()
    hit = T1.get((hz, py.key(ps)))
    return hit[0] if hit else 999


def measure(con, acc):
    tone, ini, fin = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    ex_tone, ex_ini, ex_fin = defaultdict(list), defaultdict(list), defaultdict(list)
    diff, same_word = [], 0
    for hs, ps, ho, po, level, f in pairs(con, acc):
        ps1, po1 = re.split(r"\s*[/／、]\s*", ps)[0], re.split(r"\s*[/／、]\s*", po)[0]
        a, b = py.syllables(ps1, "sixian"), py.syllables(po1, acc)
        if hs != ho:
            diff.append((hs, ps1, ho, po1, level, f))
            continue
        if len(a) != len(b) or not a or any(v is None for _, v in a + b):
            continue
        same_word += 1
        for i, ((s1, v1), (s2, v2)) in enumerate(zip(a, b)):
            ch = hs[i] if len(hs) == len(a) else hs
            if ch == "仔":      # the suffix has its own form in each accent (eˋ / er / none): counted apart
                continue
            k = (v1, py.is_checked(s1))
            tone[k][(v2, py.is_checked(s2))] += 1
            i1, f1 = split(s1)
            i2, f2 = split(s2)
            ini[i1][i2] += 1
            fin[f1][f2] += 1
            for store, key2 in ((ex_tone, (k, (v2, py.is_checked(s2)))), (ex_ini, (i1, i2)), (ex_fin, (f1, f2))):
                L = lesson_of(hs, ps1)
                if L < 999 or len(store[key2]) < 40:
                    store[key2].append((L, hs, ps1, po1, i))
    return {"tone": tone, "ini": ini, "fin": fin, "ex_tone": ex_tone, "ex_ini": ex_ini, "ex_fin": ex_fin,
            "diff": diff, "same": same_word}


def examples(store, key2, n=3, single=True):
    """Short, frequent words that show a correspondence."""
    rows = sorted(store.get(key2, []), key=lambda r: (len(r[1]) > 2, r[0], len(r[1])))
    out, seen = [], set()
    for f, hz, ps, po, i in rows:
        if hz in seen:
            continue
        seen.add(hz)
        out.append(f"{hz} {ps} → {po}")
        if len(out) == n:
            break
    return out


def report(acc):
    con = sqlite3.connect(DB)
    m = measure(con, acc)
    print(f"== {NAMES[acc]}: {m['same']} words with the same characters, {len(m['diff'])} with other characters")
    print("-- tones (Sixian → accent)")
    for v, chk, label in SX_TONES:
        c = m["tone"][(v, chk)]
        tot = sum(c.values())
        if not tot:
            continue
        top = ", ".join(f"{t[0]}{'入' if t[1] else ''} {100 * k // tot}%" for t, k in c.most_common(4))
        print(f"  {label:12} n={tot:5}  {top}")
        for t, k in c.most_common(2):
            print("      ", t, "; ".join(examples(m["ex_tone"], ((v, chk), t))))
    for name, table, store in (("initials", m["ini"], m["ex_ini"]), ("finals", m["fin"], m["ex_fin"])):
        print(f"-- {name} where the accent differs in 10% or more of the syllables (n ≥ 15)")
        for k in sorted(table, key=lambda k: -sum(table[k].values())):
            c = table[k]
            tot = sum(c.values())
            if tot < 15 or c[k] / tot > 0.9:
                continue
            top = ", ".join(f"{t or '∅'} {100 * n // tot}%" for t, n in c.most_common(4))
            print(f"  {k or '∅':6} n={tot:5}  {top}")
            for t, n in c.most_common(3):
                if t != k and n / tot >= 0.08:
                    print("      ", f"{k or '∅'}→{t or '∅'}", "; ".join(examples(store, (k, t))))
    t1 = taught_part1()
    print("-- other word, taught in Part 1 (by lesson)")
    rows = []
    for hs, ps, ho, po, level, f in m["diff"]:
        hit = t1.get((hs, py.key(ps)))
        if hit:
            rows.append((hit[0], hs, ps, ho, po, hit[1]))
    for r in sorted(rows)[:80]:
        print("  ", r)
    print(f"   ({len(rows)} of the Part 1 words)")


MAND_INI = ("zh", "ch", "sh", "r", "z", "c", "s", "j", "q", "x", "g", "k", "h", "f", "b", "p", "m", "d", "t", "n", "l", "w", "y")
PUNCT = "，。？！、,.?!；：:;（）()「」"
SENTENCES = [(2012, 44), (2012, 35), (2012, 21), (2012, 17), (2012, 69), (2014, 61), (2014, 48), (2014, 19)]


def mand_initials():
    """Traditional character → Mandarin initial, from the HSK list (single characters first, then words)."""
    path = os.path.join(ROOT, "data/raw/complete-hsk-vocabulary/complete.json")
    out = {}
    if not os.path.exists(path):
        return out
    data = json.load(open(path, encoding="utf-8"))
    for single in (True, False):
        for w in data:
            for f in w.get("forms", []):
                t = f.get("traditional") or w["simplified"]
                syl = f["transcriptions"]["numeric"].lower().split()
                if (len(t) == 1) != single or len(t) != len(syl):
                    continue
                for ch, sy in zip(t, syl):
                    out.setdefault(ch, next((i for i in MAND_INI if sy.startswith(i)), ""))
    return out


def show(p):
    """Pinyin as printed in the lessons: one space between syllables, ˆ for the lists' ASCII ^."""
    p = re.split(r"\s*[/／]\s*", p.replace("^", "ˆ").replace("\xa0", " "))[0]
    p = re.sub(r"([ˊˋˇˆ+])(?=[a-z])", r"\1 ", p)
    return re.sub(r"\s+", " ", p).strip()


def syllable_rows(con, acc):
    """One row per aligned syllable of a same-character word: dict(ch, hz, ps, po, L, i1, f1, t1, i2, f2, t2)."""
    rows, diff, same = [], [], 0
    for hs, ps, ho, po, level, f in pairs(con, acc):
        ps1, po1 = re.split(r"\s*[/／、]\s*", ps)[0], re.split(r"\s*[/／、]\s*", po)[0]
        if hs != ho:
            diff.append((hs, ps1, ho, po1))
            continue
        a, b = py.syllables(ps1, "sixian"), py.syllables(po1, acc)
        if len(a) != len(b) or not a or any(v is None for _, v in a + b):
            continue
        same += 1
        L = lesson_of(hs, ps1)
        for i, ((s1, v1), (s2, v2)) in enumerate(zip(a, b)):
            ch = hs[i] if len(hs) == len(a) else ""
            if ch == "仔":
                continue
            i1, f1 = split(s1)
            i2, f2 = split(s2)
            rows.append({"ch": ch, "hz": hs, "ps": ps1, "po": po1, "L": L, "i1": i1, "f1": f1,
                         "t1": (v1, py.is_checked(s1)), "i2": i2, "f2": f2, "t2": (v2, py.is_checked(s2))})
    return rows, diff, same


def pick(rows, n=3):
    """Example words for a set of syllable rows: Part 1 words first (by lesson), short ones first."""
    out, seen = [], set()
    for r in sorted(rows, key=lambda r: (r["L"] == 999, len(r["hz"]) > 2, r["L"], len(r["hz"]))):
        if r["hz"] in seen or (r["ch"] and r["ch"] in seen):
            continue
        seen.update((r["hz"], r["ch"]))
        out.append(f"{r['hz']} {show(r['ps'])} → {show(r['po'])}")
        if len(out) == n:
            break
    return " · ".join(out)


def pct(a, b):
    return f"{100 * a / b:.0f}%" if b else "–"


def tone_label(acc, t):
    marks = py.mark_of_value(acc)
    if acc == "dapu":
        marks = dict(marks, **{"53": "ˋ"})      # as the 115年度 lists print it
    v, chk = t
    m = marks.get(v, "")
    return f"{m or '(no mark)'} {v}" + (" (short)" if chk else "")


def section_tones(acc, rows):
    L = ["| Sixian | " + short(acc) + " | How regular | Examples (Sixian → " + short(acc) + ") |", "|---|---|---|---|"]
    for v, chk, label in SX_TONES:
        mine = [r for r in rows if r["t1"] == (v, chk)]
        c = Counter(r["t2"] for r in mine)
        if not mine:
            continue
        (top, k), rest = c.most_common(1)[0], c.most_common(3)[1:]
        other = "; ".join(f"{tone_label(acc, t)} {pct(n, len(mine))}" for t, n in rest if n / len(mine) >= 0.05)
        L.append(f"| {label} | **{tone_label(acc, top)}** | {pct(k, len(mine))} of {len(mine):,}" + (f" (also {other})" if other else "")
                 + f" | {pick([r for r in mine if r['t2'] == top and len(r['hz']) <= 2])} |")
    return L


def departing_split(acc, rows):
    """Sixian 去聲 has two outcomes in some accents (the old 陰去 / 陽去). The Sixian initial tells which, most of the time."""
    mine = [r for r in rows if r["t1"] == ("55", False)]
    c = Counter(r["t2"] for r in mine).most_common(2)
    if len(c) < 2 or c[1][1] / len(mine) < 0.2:
        return []
    plain = [r for r in mine if r["i1"] in ("b", "d", "g", "z", "j")]
    asp = [r for r in mine if r["i1"] in ("p", "t", "k", "c", "q", "m", "n", "ng", "l")]
    out = []
    for group, name in ((plain, "b, d, g, z, j"), (asp, "p, t, k, c, q or m, n, ng, l")):
        if not group:
            continue
        t, k = Counter(r["t2"] for r in group).most_common(1)[0]
        out.append((name, t, k, len(group), pick([r for r in group if r["t2"] == t and len(r["hz"]) == 1], 3)))
    if len(out) < 2 or out[0][2] / out[0][3] < 0.8:
        return []
    (n1, t1_, k1, g1, e1), (n2, t2_, k2, g2, e2) = out
    return [f"**Which 去聲?** After {n1}, it is {tone_label(acc, t1_)} in {pct(k1, g1)} of {g1:,} syllables ({e1}). "
            f"After other consonants both tones occur and the word has to be learned: after {n2}, "
            f"{tone_label(acc, t2_)} has {pct(k2, g2)} of {g2:,} ({e2}).", ""]


def section_table(acc, rows, part, min_n, max_rows):
    a, b = ("i1", "i2") if part == "ini" else ("f1", "f2")
    groups = defaultdict(list)
    for r in rows:
        groups[r[a]].append(r)
    out = []
    for k, mine in groups.items():
        c = Counter(r[b] for r in mine)
        changed = len(mine) - c[k]
        if len(mine) < min_n or changed / len(mine) < 0.10:
            continue
        cells = []
        for t, n in c.most_common(3):
            if n / len(mine) >= 0.08:
                cells.append(f"**{t or '(none)'}** {pct(n, len(mine))}" if t != k else f"{t or '(none)'} {pct(n, len(mine))}")
        tops = [t for t, n in c.most_common(3) if t != k and n / len(mine) >= 0.08]
        if not tops:
            continue
        ex = pick([r for r in mine if r[b] in tops[:1]], 3)
        out.append((changed, f"| {k or '(no initial)'} | {', '.join(cells)} | {len(mine):,} | {ex} |"))
    head = ["| Sixian | " + short(acc) + " | Syllables | Examples |", "|---|---|---|---|"]
    return head + [line for _, line in sorted(out, reverse=True)[:max_rows]]


def conditioned(acc, rows, mand):
    """Sentences for the rules that Mandarin lets the learner predict."""
    out = []
    zcs = [r for r in rows if r["i1"] in ("z", "c", "s") and r["ch"] in mand]
    retro = [r for r in zcs if mand[r["ch"]] in ("zh", "ch", "sh", "r")]
    flat = [r for r in zcs if mand[r["ch"]] in ("z", "c", "s", "j", "q", "x")]
    hit = [r for r in retro if r["i2"] in ("zh", "ch", "sh")]
    stay = [r for r in flat if r["i2"] in ("z", "c", "s")]
    if retro and len(hit) / len(retro) >= 0.5:
        out.append(f"- **z, c, s: Mandarin tells you.** Where Mandarin has zh, ch, sh or r, Sixian z, c, s is zh, ch, sh in "
                   f"{pct(len(hit), len(retro))} of {len(retro):,} syllables ({pick(hit, 3)}). Where Mandarin has z, c, s, "
                   f"j, q or x, it stays z, c, s in {pct(len(stay), len(flat))} of {len(flat):,}.")
    jqx = [r for r in rows if r["i1"] in ("j", "q", "x")]
    hit = [r for r in jqx if r["i2"] in ("z", "c", "s")]
    if jqx and len(hit) / len(jqx) >= 0.5:
        out.append(f"- **j, q, x are written z, c, s** ({pct(len(hit), len(jqx))} of {len(jqx):,}): {pick(hit, 3)}. "
                   "The sound before i is close; the spelling changes.")
    zi = [r for r in rows if r["i1"] == "" and r["f1"].startswith("i")]
    for tgt, name in (("rh", "rh"), ("v", "v"), ("bb", "bb")):
        hit = [r for r in zi if r["i2"] == tgt]
        if zi and len(hit) / len(zi) >= 0.08:
            out.append(f"- **A Sixian syllable that starts with i** starts with **{name}** in {pct(len(hit), len(zi))} of "
                       f"{len(zi):,} syllables: {pick(hit, 3)}.")
    hk = [r for r in rows if r["i1"] in ("h", "f") and mand.get(r["ch"]) in ("k", "q")]
    hit = [r for r in hk if r["i2"] == "k"]
    if hk and len(hit) / len(hk) >= 0.3:
        out.append(f"- **Sixian h or f where Mandarin has k or q** is **k** in {pct(len(hit), len(hk))} of {len(hk):,} "
                   f"syllables: {pick(hit, 3)}.")
    for src, tgt in (("v", "bb"), ("ng", "n")):
        mine = [r for r in rows if r["i1"] == src]
        hit = [r for r in mine if r["i2"] == tgt]
        if mine and len(hit) / len(mine) >= 0.08:
            out.append(f"- **{src} → {tgt}** in {pct(len(hit), len(mine))} of {len(mine):,} syllables: {pick(hit, 3)}.")
    sf = [r for r in rows if r["i1"] == "s" and r["i2"] == "f"]
    if len(sf) >= 20:
        out.append(f"- **s → f** in {len(sf)} syllables: {pick(sf, 3)}.")
    return out


def section_suffix(con, acc):
    """What the accent does with a Sixian word in 仔."""
    c, ex = Counter(), defaultdict(list)
    for hs, ps, ho, po, level, f in pairs(con, acc):
        if not hs.endswith("仔") or len(hs) < 2:
            continue
        if ho.endswith("仔"):
            k = "keeps 仔"
        elif ho.endswith("子"):
            k = "has 子"
        elif ho == hs[:-1]:
            k = "drops it"
        else:
            k = "another word"
        c[k] += 1
        ex[k].append((lesson_of(hs, re.split(r"\s*[/／、]\s*", ps)[0]), f"{hs} {show(ps)} → {ho} {show(po)}"))
    tot = sum(c.values())
    L = [f"Of the {tot:,} Sixian list words that end in 仔:", ""]
    for k, n in c.most_common():
        if n / tot >= 0.01:
            L.append(f"- **{k}**: {n:,} ({pct(n, tot)}). " + " · ".join(e for _, e in sorted(ex[k])[:3]))
    if acc == "dapu":       # the small tone: the word drops 仔 and its last syllable rises
        drop = [(hs, ps, po) for hs, ps, ho, po, lv, f in pairs(con, acc) if hs.endswith("仔") and ho == hs[:-1]]
        rise = [(hs, ps, po) for hs, ps, po in drop if (py.syllables(po, acc) or [("", "")])[-1][1] == "35"]
        ex35 = " · ".join(f"{hs} {show(ps)} → {hs[:-1]} {show(po)}" for hs, ps, po in sorted(rise, key=lambda r: lesson_of(r[0], r[1]))[:4])
        L += ["", f"Of the {len(drop):,} words that drop 仔, {len(rise):,} ({pct(len(rise), len(drop))}) end in the rising tone ˊ 35, "
              f"which no plain word has: {ex35}."]
    return L


def build():
    con = sqlite3.connect(DB)
    notes = yaml.safe_load(open(os.path.join(OUT, "notes.yaml"), encoding="utf-8"))
    mand = mand_initials()
    t1 = taught_part1()
    p = parallel(con)
    missing = [k for k in SENTENCES if k not in p]
    if missing:
        sys.exit(f"sentences not in six accents: {missing}")
    en = notes["sentences_en"]
    glance = []
    for n, acc in enumerate(ACCENTS, 1):
        N = notes[acc]
        rows, diff, same = syllable_rows(con, acc)
        name = short(acc)
        L = [f"# Bridge {n} · From Sixian to {NAMES[acc]}", "", N["intro"].strip(), ""]
        # distance on the Part 1 words
        if acc != "south-sixian":
            both = [(hs, ps, ho) for hs, ps, ho, po, lv, f in pairs(con, acc)
                    if (hs, py.key(re.split(r"\s*[/／、]\s*", ps)[0])) in t1]
            words = {(hs, ps) for hs, ps, ho in both}
            other = {(hs, ps) for hs, ps, ho in both if hs != ho} - {(hs, ps) for hs, ps, ho in both if hs == ho}
            dist = f"{len(words) - len(other):,} of the {len(words):,} Part 1 words in the lists are written with the same characters ({pct(len(words) - len(other), len(words))}); {len(other):,} are another word"
        else:
            tot = con.execute("SELECT count(*) FROM reading WHERE accent = 'south-sixian'").fetchone()[0]
            df = con.execute("SELECT count(*) FROM reading a JOIN reading b ON a.entry_id = b.entry_id AND a.accent = 'sixian' "
                             "AND b.accent = 'south-sixian' WHERE a.pkey != b.pkey").fetchone()[0]
            dist = f"{tot - df:,} of the {tot:,} MOE dictionary entries with a southern reading are read exactly as in the north ({pct(tot - df, tot)})"
        L += [f"**Measured.** {dist[0].upper() + dist[1:]}.", ""]
        L += ["## 1. Tones", ""] + section_tones(acc, rows) + [""] + departing_split(acc, rows) + [N["tones"].strip(), ""]
        ini = section_table(acc, rows, "ini", 30, 12)
        L += ["## 2. Consonants", ""]
        if len(ini) > 2:
            L += ini + [""]
        cond = conditioned(acc, rows, mand)
        L += cond + ([""] if cond else []) + [N["consonants"].strip(), ""]
        fin = section_table(acc, rows, "fin", 40, 12)
        L += ["## 3. Vowels and endings", ""] + (fin + [""] if len(fin) > 2 else []) + [N["vowels"].strip(), ""]
        if acc != "south-sixian":
            L += ["## 4. The suffix 仔", ""] + section_suffix(con, acc) + ["", N["suffix"].strip(), ""]
        else:
            L += ["## 4. The suffix 仔", "", N["suffix"].strip(), ""]
        # words: chosen by hand in notes.yaml, forms taken from the data
        L += ["## 5. Words that change", "", f"| Sixian | {name} | |", "|---|---|---|"]
        if acc == "south-sixian":
            cjk = re.compile(r"[㐀-鿿豈-﫿\U00020000-\U0003ffff]")
            sents = []       # southern sentences whose characters and syllables line up
            for h, pin in con.execute("SELECT hanzi, pinyin FROM sentence WHERE accent = 'south-sixian'"):
                chars = "".join(cjk.findall(h))
                syl = py.syllables(re.sub(f"[{re.escape(PUNCT)}]", " ", pin), acc)
                if len(chars) == len(syl):
                    sents.append((chars, [f"{a}{b}" for a, b in syl]))
            for w in N["words"]:
                hz, pin = w["south"].split(" ", 1)
                want = [f"{a}{b}" for a, b in py.syllables(pin, acc)]
                k = sum(any(chars[i:i + len(hz)] == hz and syl[i:i + len(hz)] == want for i in range(len(chars)))
                        for chars, syl in sents)
                moe = con.execute("SELECT count(*) FROM reading r JOIN entry e ON e.id = r.entry_id "
                                  "JOIN reading n ON n.entry_id = e.id AND n.accent = 'sixian' WHERE r.accent = 'south-sixian' "
                                  "AND e.hanzi = ? AND r.pkey = ? AND n.pkey != r.pkey", (hz, py.key(pin, acc))).fetchone()[0]
                if not k and not moe:
                    sys.exit(f"south-sixian: {w['south']} is in no parallel sentence and is not an MOE southern reading")
                src = (f"{k} of the {len(sents)} sentences" if k else "") + (" · " if k and moe else "") + ("MOE" if moe else "")
                L.append(f"| {w['sx']} | {w['south']} | {w['en']} ({src}) |")
        else:
            by = defaultdict(list)
            for hs, ps, ho, po in diff:
                by[hs].append((ps, ho, po))
            for w in N["words"]:
                hz, want = (w.split("→") + [None])[:2]
                cands = [c for c in by.get(hz, []) if want is None or c[1] == want]
                if not cands:
                    sys.exit(f"{acc}: no list pair for {w}")
                ps, ho, po = cands[0]
                hit = t1.get((hz, py.key(ps)))
                L.append(f"| {hz} {show(ps)} | {ho} {show(po)} | {(hit[1] if hit else '').replace(' (Sixian)', '')} |")
        L += ["", N["words_note"].strip(), ""]
        L += ["## 6. The same eight sentences", "", "From 客語百句 (客家委員會), where every sentence is recorded in six accents.", ""]
        for i, key in enumerate(SENTENCES, 1):
            v = p[key]
            L += [f"**{i}. {en[i - 1]}**", "", f"- Sixian: {v['sixian'][0]} · {show(v['sixian'][1])}",
                  f"- {name}: {v[acc][0]} · {show(v[acc][1])}", ""]
        L += [N["sentences"].strip(), ""]
        # try it: Sixian words from Part 1, the accent form hidden
        same_words = {}
        for hs, ps, ho, po, lv, f in pairs(con, acc):
            if hs == ho:
                same_words.setdefault(hs, (ps, po))
        L += ["## 7. Try it", "", f"Say each word in {name} before you open the answer.", ""]
        for hz in N["try"]:
            if hz not in same_words:
                sys.exit(f"{acc}: try-it word {hz} has no same-character pair")
            ps, po = same_words[hz]
            L.append(f"<details><summary>{hz} {show(ps)}</summary>{show(po)}</details>")
            L.append("")
        open(os.path.join(OUT, f"{n}-{acc}.md"), "w", encoding="utf-8").write("\n".join(L).rstrip() + "\n")
        tones = []
        for v, chk, label in SX_TONES:
            mine = [r for r in rows if r["t1"] == (v, chk)]
            top, k = Counter(r["t2"] for r in mine).most_common(1)[0]
            tones.append(f"{tone_label(acc, top)}")
        glance.append((acc, dist, tones))
        print(f"{n}-{acc}.md: {len(rows):,} syllables compared, {len(L)} lines")
    # the overview
    L = ["# Bridge · The other accents, starting from Sixian", "", notes["overview"]["intro"].strip(), ""]
    L += ["## How far each accent is", ""] + [f"- **{NAMES[a]}**: {d}." for a, d, _ in glance] + ["", notes["overview"]["distance"].strip(), ""]
    L += ["## The tones at a glance", "", "| Sixian | " + " | ".join(short(a) for a, _, _ in glance) + " |",
          "|---|" + "---|" * len(glance)]
    for i, (v, chk, label) in enumerate(SX_TONES):
        L.append(f"| {label} | " + " | ".join(t[i] for _, _, t in glance) + " |")
    L += ["", notes["overview"]["tones"].strip(), "", "## One sentence, six accents", ""]
    for i, key in enumerate(SENTENCES, 1):
        v = p[key]
        L += [f"**{i}. {en[i - 1]}**", "", "| | | |", "|---|---|---|"]
        L += [f"| {short(a)} | {v[a][0]} | {show(v[a][1])} |" for a in ["sixian"] + ACCENTS] + [""]
    L += [notes["overview"]["after"].strip(), ""]
    open(os.path.join(OUT, "0-overview.md"), "w", encoding="utf-8").write("\n".join(L).rstrip() + "\n")
    print(f"0-overview.md: {len(L)} lines")


def parallel(con):
    """客語百句 rows that exist in all six accents."""
    rows = defaultdict(dict)
    for y, n, acc, hz, pin, zh, url in con.execute(
            "SELECT set_year, num, accent, hanzi, pinyin, mandarin, audio_url FROM sentence WHERE hanzi_damaged = 0 "
            "OR hanzi_damaged IS NULL"):
        rows[(y, n)][acc] = (hz, pin, zh, url)
    return {k: v for k, v in rows.items() if len(v) == 6}


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["report"]:
        for acc in (a[1:] or ACCENTS):
            report(acc)
    elif a[:1] == ["sentences"]:
        con = sqlite3.connect(DB)
        p = parallel(con)
        print(len(p), "sentences in six accents")
        for k in sorted(p)[:int(a[1]) if len(a) > 1 else 10]:
            print(k, p[k]["sixian"][2])
            for acc in ["sixian"] + ACCENTS:
                print(f"   {acc:13} {p[k][acc][0]} | {p[k][acc][1]}")
    elif a[:1] == ["build"]:
        build()
    else:
        sys.exit(__doc__)
