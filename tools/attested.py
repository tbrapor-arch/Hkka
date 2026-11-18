#!/usr/bin/env python3
"""The attested-word list: untaught 中高級 and 高級 words that real Hakka texts use, for the extra stories (外篇).

  python3 -I tools/attested.py            # → course/packets/attested.tsv and course/packets/attested-single.tsv
  python3 -I tools/attested.py --ctx 當當  # show the corpus contexts of one word (to review a SEG? flag)

Why not rank by frequency: the Hakka Council corpus holds 206 Sixian texts (~165k tokens, 68% of them single
characters), and 28% of the texts are certification exam papers, which supply 41–48% of the hits of the untaught
advanced words; Glossika reaches only a few of them. See docs/extra-stories-plan.md.

Rule. A word is attested when it is
  - a kaga115 Sixian entry of level 中高級 or 高級, not taught (taught = (hanzi, pinyin key) in the new_words of
    course/lessons/*.yaml or course/perfectionnement/*.yaml, as in tools/coverage.py), no pattern with …;
  - written with 2+ characters (single characters go to attested-single.tsv: their corpus hits mix senses);
  - R >= 2, where R = the number of distinct non-exam corpus works it appears in (the "Frog, where are you?"
    retellings count as one work; certification exam papers are left out) + 1 if Glossika has it (private module).
Segmentation is the one of tools/build_db.py (longest match on the known words), so corpus_freq agrees with it.

Flags (column `flags`):
  SEG?   maybe a segmentation artefact, not reviewed: a doubled word (日日, 平平), a word made of two taught words
         (在 + 中央), or most hits straddle another word's boundary. Look with --ctx.
  SEG    reviewed by hand (REVIEWED below): the hits are mostly not this word in its listed sense; R is too high.
         A word reviewed "ok" loses the flag.
  POLY   the same characters have another reading in the lists or MOE: check the sense of the hits.
  VAR    the list gives a variant spelling (variant table, hanzi-alt).
"""
import csv
import glob
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
OUT = os.path.join(ROOT, "course/packets/attested.tsv")
OUT1 = os.path.join(ROOT, "course/packets/attested-single.tsv")
HAN = re.compile(r"[㐀-鿿豈-﫿\U00020000-\U0003ffff]+")
LEVELS = ("中高級", "高級")

# Hand review of SEG? words (corpus contexts read with --ctx on 18 Nov 2026). "SEG <why>" confirms an artefact,
# "ok <why>" clears the flag. A word not listed keeps SEG? when the heuristics fire.
REVIEWED = {
    "當當": "ok 當當在該 + verb 'in the middle of doing', as listed",
    "日日": "ok 'every day' (one exam hit is the flower 日日春)",
    "在中央": "ok 'right in the middle'; one hit is 在 + 中央山脈",
    "早早": "ok 早早就 'early on, long since'",
    "毋多知仔": "ok", "濛濛": "ok", "目金金仔": "ok", "一𥍉目": "ok", "來來去去": "ok", "潦潦": "ok",
    "七早八早": "ok", "共樣共樣": "ok", "出出入入": "ok", "各各": "ok", "呸口涎": "ok", "孤栖孤栖": "ok",
    "家家屋屋": "ok", "心肝仔": "ok", "無堵好": "ok", "目汁含等": "ok", "總係會": "ok", "萋萋": "ok", "褲袋仔": "ok",
    "該搭仔": "ok", "食毋得": "ok", "頭犁犁仔": "ok", "平平": "ok both listed senses (flat; equally)",
    "心頭拶拶": "ok", "拶拶": "ok 舂到拶拶 'packed tight'", "礱礱舂舂": "ok", "了了": "ok", "全全": "ok",
    "半山排": "ok", "唸唸唸唸": "ok", "四四散散": "ok", "專專": "ok", "沒沒術術": "ok", "無核卵": "ok",
    "血漬漬仔": "ok", "講花蓼": "ok", "迪迪凸凸": "ok",
    "出頭": "SEG half the hits are 探出 + 頭那 'head'; the others are 三十出頭 'a little over'",
    "講親": "SEG one of two works has 講 + 親像",
    "著著": "SEG the hits are 著 + 著 (catch, V著), not diauˇ diauˇ 'steady'",
    "結結": "SEG the hits are 目結結仔 'stare', not 'firm, sticky'",
    "粒粒": "SEG the hits are 一粒 + 粒 'grain by grain', not 'dry (rice)'",
    "到家": "SEG both works have 到 + 家鄉",
    "打石": "SEG the hits are 打 + 石炭 / 石頭",
    "過水": "SEG the hits are 過 + 水田, 泅過水 'swim across'",
    "亮亮": "SEG? sense unclear in 亮亮个歌聲, 堆到亮亮",
}


def kind(title, relation):
    if "能力認證" in relation:
        return "exam"
    if "青蛙" in title:
        return "frog"
    return "work"


def taught_set():
    taught = set()
    for f in (sorted(glob.glob(os.path.join(ROOT, "course/lessons/[0-9]*.yaml")))
              + sorted(glob.glob(os.path.join(ROOT, "course/perfectionnement/[0-9]*.yaml")))):
        for w in (yaml.safe_load(open(f, encoding="utf-8")) or {}).get("new_words") or []:
            taught.add((w["hanzi"], py.key(w.get("pinyin", ""))))
    return taught


def segment(con):
    """Per word: Counter(text id). Per word: list of (text id, left context, right context). Same cut as build_db.py."""
    words = {hz for (hz,) in con.execute(
        "SELECT hanzi FROM entry WHERE (source='moe' AND pkey IS NOT NULL) OR (source IN ('kaga','kaga115') AND accent='sixian')")}
    longest = max(len(w) for w in words)
    hits, ctx, kinds, ntok = defaultdict(Counter), defaultdict(list), {}, 0
    for tid, title, rel, text in con.execute(
            "SELECT id, title, relation, content FROM corpus WHERE ',' || accents || ',' LIKE '%,sixian,%'"):
        kinds[tid] = kind(title, rel)
        t = re.sub(r"<[^>]+>[^<]*</[^>]+>|<[^>]+>|（[0-9：－:\-]+）|[男女]\d*：", " ", text)
        for run in HAN.findall(t):
            i = 0
            while i < len(run):
                for L in range(min(longest, len(run) - i), 0, -1):
                    w = run[i:i + L]
                    if L == 1 or w in words:
                        hits[w][tid] += 1
                        ntok += 1
                        if L > 1:
                            ctx[w].append((tid, run[max(0, i - 4):i], run[i + L:i + L + 4]))
                        i += L
                        break
    return words, hits, ctx, kinds, ntok


def works(w, hits, kinds):
    ne = [t for t in hits.get(w, {}) if kinds[t] != "exam"]
    return len([t for t in ne if kinds[t] == "work"]) + (1 if any(kinds[t] == "frog" for t in ne) else 0)


def main():
    con = sqlite3.connect(DB)
    private = con.execute("SELECT count(*) FROM glossika").fetchone()[0] > 0
    words, hits, ctx, kinds, ntok = segment(con)
    if "--ctx" in sys.argv:
        w = sys.argv[sys.argv.index("--ctx") + 1]
        for tid, left, right in ctx.get(w, []):
            print(f"{tid:4} {kinds[tid]:5} {left:>4}[{w}]{right}")
        return
    taught = taught_set()
    multi = {w for w in words if len(w) > 1}
    lex = {hz for hz, _ in taught} | multi

    # other readings (POLY), variants (VAR), official examples
    readings = defaultdict(set)
    for hz, p in con.execute(
            "SELECT hanzi, pinyin FROM entry WHERE source IN ('kaga115', 'kaga') AND accent = 'sixian' AND pinyin != '' "
            "UNION ALL SELECT e.hanzi, r.pinyin FROM entry e JOIN reading r ON r.entry_id = e.id "
            "WHERE r.accent = 'sixian' AND r.pinyin != ''"):
        for one in re.split(r"\s*[/／、]\s*", p or ""):
            if one.strip():
                readings[hz].add(py.key(one.strip()))
    var = defaultdict(set)
    for eid, hz in con.execute("SELECT entry_id, hanzi FROM variant WHERE kind = 'hanzi-alt' AND hanzi IS NOT NULL"):
        var[eid].add(hz)
    has_ex = {e for (e,) in con.execute("SELECT DISTINCT entry_id FROM example WHERE source = 'kaga115' AND accent = 'sixian'")}

    rows = defaultdict(lambda: {"ids": [], "cat": [], "zh": []})
    for eid, hz, pin, pk, lv, cat, zh, gl in con.execute(
            "SELECT id, hanzi, pinyin, pkey, level, category, mandarin, coalesce(glossika_freq, 0) FROM entry "
            "WHERE source = 'kaga115' AND accent = 'sixian' AND level IN ('中高級', '高級') AND pkey != '' ORDER BY id"):
        if (hz, pk) in taught or "…" in hz or "..." in hz:
            continue
        r = rows[(hz, pk)]
        lv = min(lv, r.get("level", lv), key=LEVELS.index)    # 平平 is listed at both levels: keep the lower
        r.update(hanzi=hz, pinyin=pin, pkey=pk, level=lv, glossika=max(r.get("glossika", 0), gl))
        r["ids"].append(eid)
        for k, v in (("cat", cat), ("zh", zh)):
            if v and v not in r[k]:
                r[k].append(v)

    def seg_flag(w):
        if w in REVIEWED:
            v = REVIEWED[w]
            return v.split()[0] if v.startswith("SEG") else ""
        n = len(w)
        doubled = (n == 2 and w[0] == w[1]) or (n == 4 and (w[:2] == w[2:] or (w[0] == w[1] and w[2] == w[3])))
        split = n >= 3 and any(w[:i] in lex and w[i:] in lex and max(i, n - i) >= 2 for i in range(1, n))
        cs = [c for c in ctx.get(w, []) if kinds[c[0]] != "exam"]
        straddle = sum(1 for _, left, right in cs
                       if any(left[-k:] + w[:j] in lex for k in (1, 2) for j in range(1, n) if len(left) >= k)
                       or any(w[-j:] + right[:k] in lex for k in (1, 2) for j in range(1, n) if len(right) >= k))
        return "SEG?" if doubled or split or (cs and straddle * 2 >= len(cs)) else ""

    out, single = [], []
    for (hz, pk), r in rows.items():
        g = 1 if r["glossika"] > 0 else 0
        nw = works(hz, hits, kinds)
        R = nw + g
        if R < 2:
            continue
        fl = []
        if len(hz) > 1:
            s = seg_flag(hz)
            if s:
                fl.append(s)
        if readings.get(hz, set()) - {pk}:
            fl.append("POLY")
        if any(var[e] - {hz} for e in r["ids"]):
            fl.append("VAR")
        row = [hz, r["pinyin"], r["level"], "；".join(r["cat"]), " / ".join(r["zh"]), R, nw, g,
               1 if any(e in has_ex for e in r["ids"]) else 0, " ".join(fl)]
        (out if len(hz) > 1 else single).append(row)
    key = lambda x: (LEVELS.index(x[2]), -x[5], -x[6], x[0])
    out.sort(key=key)
    single.sort(key=key)
    head = ["hanzi", "pinyin", "level", "category", "mandarin", "R", "works", "glossika", "example", "flags"]
    note = ("# Generated by tools/attested.py (regenerate, do not edit). Rule and flags: see the tool's docstring and "
            "docs/extra-stories-plan.md." + ("" if private else " Built WITHOUT the private module: glossika = 0."))
    for path, data, extra in ((OUT, out, ""), (OUT1, single, " Single characters: check the sense by hand.")):
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(note + extra + "\n")
            wr = csv.writer(f, delimiter="\t", lineterminator="\n")
            wr.writerow(head)
            wr.writerows(data)
    print(f"corpus: {len(kinds)} Sixian texts, {ntok} tokens, {sum(k == 'exam' for k in kinds.values())} exam papers")
    if not private:
        print("private module not loaded: glossika = 0 for every word (HAKKA_PRIVATE=../Hkka-private make db)")
    for lv in LEVELS:
        part = [x for x in out if x[2] == lv]
        fc = Counter(f for x in part for f in x[9].split())
        print(f"  {lv}: {len(part)} words; glossika {sum(x[7] for x in part)}; no example {sum(not x[8] for x in part)}; "
              + ", ".join(f"{k} {v}" for k, v in sorted(fc.items())))
    print(f"  single characters (check by hand): {len(single)} → {os.path.relpath(OUT1, ROOT)}")
    print(f"→ {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
