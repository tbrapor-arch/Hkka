#!/usr/bin/env python3
"""Word plan and lesson packets for 進修 (Part 2). Does the word hunt once, so that writing a lesson starts from one file.

  python3 -I tools/packets.py plan [--force]   # split the untaught words into one packet per lesson → course/packets/plan.tsv
  python3 -I tools/packets.py packet N         # write course/packets/PNN.md for lesson PN (run just before writing PN)
  python3 -I tools/packets.py status           # planned / taught per lesson, words left over
  python3 -I tools/packets.py recycle          # after a batch: drop from course/batches/recycle.tsv the words a 進修 text now uses

plan     Pool = every untaught 初級 and 中級 word, then the most frequent untaught 中高級 words, up to SIZE words for each
         lesson that is not written yet and is not a review (every 7th). Words of the scene themes (居家生活, 人體與醫療 …)
         are cut into packets by theme; words of the non-scene themes (抽象概念, 副詞, 量詞 …) are dealt out evenly, so
         every lesson has both. Easier and more frequent words come first. plan.tsv may be edited by hand.
packet   The packet lists, for lesson N: its words still untaught (reading, level, glosses, flags), words left over from
         earlier packets, every official Sixian sentence for each word with a draft pinyin and the untaught words it
         would drag in, the clean sentences that hold two or more packet words, and a few recycle words.
         A packet is generated from the current lessons: regenerate it rather than edit it.

Flags in a packet:
  POLY   the same characters have another reading in the lists: choose the reading by sense (checklist: 逐, 熟, 歇, 合)
  DECL   the same characters are already declared in a lesson under another reading
  SYL    one syllable for two characters (幾下 giaˊ): lint cannot align it
  f=0    no occurrence in Glossika or the corpus: a rare word, quote its official sentence
Sentence tags:
  [clean]      every word is taught or in this packet: the line can be quoted as it is (`source:` + real audio for kaga115)
  [+ 甲 乙]    quoting it also brings in these untaught words (declare them, or pick another sentence)
The draft pinyin joins the readings of the words; {a|b} marks a word with more than one reading: choose, then let lint check.
"""
import csv
import glob
import os
import re
import sqlite3
import sys
from collections import defaultdict

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pinyin as py  # noqa: E402

ROOT = os.path.dirname(HERE)
DB = os.path.join(ROOT, "data/build/hakka.db")
PDIR = os.path.join(ROOT, "course/packets")
PLAN = os.path.join(PDIR, "plan.tsv")
LAST = 70
SIZE = 45
LEVELS = {"基礎級": 0, "初級": 1, "中級": 2, "中高級": 3}
# Themes that do not give a scene: their words are dealt out over all the lessons.
SPREAD = {"抽象概念與形容", "時空與情狀副詞", "特殊詞類", "數詞量詞", "代詞", "事物狀態與變化", "心理活動與感覺"}
# Neighbouring themes stay next to each other when a packet has to straddle two of them.
THEME_ORDER = ["居家生活", "人體與醫療", "生物", "自然與景觀", "歲時祭儀、習俗與宗教", "藝文與教育", "社會關係與行為",
               "法律、政治與軍事", "職業與經濟", "通訊、建設與交通", "外在活動與動作"]
CJK = re.compile(r"[㐀-鿿豈-﫿\U00020000-\U0003ffff]")
PARTICLES = {"啊": "a", "吔": "leˊ"}


def lesson_paths():
    return (sorted(glob.glob(os.path.join(ROOT, "course/lessons/[0-9]*.yaml")))
            + sorted(glob.glob(os.path.join(ROOT, "course/perfectionnement/[0-9]*.yaml"))))


class State:
    """What the written lessons teach."""

    def __init__(self):
        self.taught = set()                 # (hanzi, pkey)
        self.declared = defaultdict(list)   # hanzi → [(tag, pinyin)]
        self.written = set()                # 進修 lesson numbers that exist
        for f in lesson_paths():
            d = yaml.safe_load(open(f, encoding="utf-8"))
            p2 = "perfectionnement" in f
            if p2:
                self.written.add(d.get("id"))
            tag = ("P" if p2 else "") + str(d.get("id"))
            for w in d.get("new_words") or []:
                self.taught.add((w["hanzi"], py.key(w.get("pinyin", ""))))
                self.declared[w["hanzi"]].append((tag, w.get("pinyin", "")))

    def covered(self, hz, k):
        """Same rule as tools/coverage.py (pattern entries count when their stem is taught)."""
        if (hz, k) in self.taught:
            return True
        stem = hz.replace("...", "…").strip("…")
        if not stem or stem == hz:
            return False
        if (stem, k) in self.taught:
            return True
        n = len(k.split("-"))
        if hz.startswith("…"):
            return any(t.endswith(stem) and tk.split("-")[-n:] == k.split("-") for t, tk in self.taught)
        return any(t.startswith(stem) and tk.split("-")[:n] == k.split("-") for t, tk in self.taught)


def todo_lessons(st):
    return [n for n in range(1, LAST + 1) if n % 7 and n not in st.written]


def untaught(con, st):
    rows = con.execute(
        "SELECT id, hanzi, pinyin, pkey, level, category, mandarin, english, cognate, "
        "coalesce(glossika_freq, 0) * 10 + coalesce(corpus_freq, 0) AS f FROM entry "
        "WHERE source = 'kaga115' AND accent = 'sixian' AND level IN ('初級', '中級', '中高級') AND pkey != ''").fetchall()
    seen, out = set(), []
    for r in rows:
        if (r[1], r[3]) in seen or st.covered(r[1], r[3]):
            continue
        seen.add((r[1], r[3]))
        out.append(dict(zip(("id", "hanzi", "pinyin", "pkey", "level", "category", "mandarin", "english", "cognate", "f"), r)))
    return out


def rank(w):
    return (LEVELS[w["level"]], -w["f"], w["id"])


def make_plan(force=False):
    if os.path.exists(PLAN) and not force:
        sys.exit(f"{os.path.relpath(PLAN, ROOT)} exists; use --force to redo it (lessons already written keep their words)")
    con, st = sqlite3.connect(DB), State()
    lessons = todo_lessons(st)
    words = untaught(con, st)
    must = [w for w in words if w["level"] != "中高級"]
    extra = sorted((w for w in words if w["level"] == "中高級"), key=rank)
    room = len(lessons) * SIZE - len(must)
    pool = must + extra[:max(0, room)]
    spread = sorted((w for w in pool if w["category"] in SPREAD), key=rank)
    scene = [w for w in pool if w["category"] not in SPREAD]
    # scene words: by theme, easier first, cut into as many packets as there are lessons
    order = {c: i for i, c in enumerate(THEME_ORDER)}
    scene.sort(key=lambda w: (order.get(w["category"], 99),) + rank(w))
    per = len(scene) / len(lessons)
    chunks = [scene[round(i * per):round((i + 1) * per)] for i in range(len(lessons))]
    # schedule: a theme's first (easiest) packet early, its last one late, themes alternating
    pos = defaultdict(list)
    for c in chunks:
        pos[c[0]["category"]].append(c)
    sched = sorted(((i + 0.5) / len(cs), order.get(cat, 99), c) for cat, cs in pos.items() for i, c in enumerate(cs))
    packets = [list(c) for _, _, c in sched]
    for i, w in enumerate(spread):       # easier function words to the earlier lessons, evenly
        packets[i * len(lessons) // len(spread)].append(w)
    os.makedirs(PDIR, exist_ok=True)
    with open(PLAN, "w", encoding="utf-8", newline="") as f:
        out = csv.writer(f, delimiter="\t", lineterminator="\n")
        out.writerow(["lesson", "hanzi", "pinyin", "level", "category"])
        for n, p in zip(lessons, packets):
            for w in sorted(p, key=lambda w: (w["category"] in SPREAD, order.get(w["category"], 99)) + rank(w)):
                out.writerow([n, w["hanzi"], w["pinyin"], w["level"], w["category"]])
    by = defaultdict(int)
    for w in pool:
        by[w["level"]] += 1
    print(f"{len(pool)} words in {len(lessons)} lessons (P{lessons[0]}–P{lessons[-1]}): "
          + ", ".join(f"{l} {by[l]}" for l in LEVELS if by[l])
          + f"; 中高級 left out: {max(0, len(extra) - room)}")
    for n, p in zip(lessons, packets):
        cats = defaultdict(int)
        for w in p:
            if w["category"] not in SPREAD:
                cats[w["category"]] += 1
        print(f"  P{n}: {len(p)} words · " + ", ".join(f"{c} {k}" for c, k in sorted(cats.items(), key=lambda x: -x[1])))


def read_plan():
    if not os.path.exists(PLAN):
        sys.exit("no plan yet: python3 -I tools/packets.py plan")
    return list(csv.DictReader(open(PLAN, encoding="utf-8"), delimiter="\t"))


class Reader:
    """Cuts an official sentence (characters only: the lists give examples no pinyin) into words and drafts its pinyin."""

    def __init__(self, con, st, packet_hanzi):
        self.read = defaultdict(list)       # hanzi → readings, taught ones first
        for hz, decl in st.declared.items():
            for _, p in decl:
                if p and p not in self.read[hz]:
                    self.read[hz].append(p)
        self.known = set(self.read) | set(packet_hanzi) | set(PARTICLES)
        for hz, p in PARTICLES.items():
            self.read[hz].append(p)
        self.listed = defaultdict(list)
        q = ("SELECT hanzi, pinyin, 0 FROM entry WHERE source = 'kaga115' AND accent = 'sixian' AND pinyin != '' "
             "UNION ALL SELECT hanzi, pinyin, 1 FROM entry WHERE source = 'kaga' AND accent = 'sixian' AND pinyin != '' "
             "UNION ALL SELECT e.hanzi, r.pinyin, 2 FROM entry e JOIN reading r ON r.entry_id = e.id "
             "WHERE r.accent = 'sixian' AND r.pinyin != '' ORDER BY 3")
        for hz, p, _ in con.execute(q):
            if hz and p:
                for one in re.split(r"\s*[/／、]\s*", p):
                    one = one.strip()
                    if one and py.key(one) not in {py.key(x) for x in self.listed[hz]}:
                        self.listed[hz].append(one)
        self.maxlen = max(map(len, self.listed))

    def cut(self, text):
        """→ [(piece, kind)], kind: known | untaught | unknown | other (punctuation)."""
        n = len(text)
        best = [None] * (n + 1)
        best[0] = (0, [])
        for i in range(n):
            if best[i] is None:
                continue
            c0, path = best[i]
            opts = []
            if not CJK.match(text[i]):
                opts.append((1, 0, "other"))
            else:
                for L in range(1, min(self.maxlen, n - i) + 1):
                    w = text[i:i + L]
                    if w in self.known:
                        opts.append((L, 1, "known"))
                    elif w in self.listed:
                        opts.append((L, 9 * L + 1, "untaught"))
                if not any(L == 1 for L, _, _ in opts):
                    opts.append((1, 100, "unknown"))
            for L, c, kind in opts:
                cand = (c0 + c, path + [(text[i:i + L], kind)])
                if best[i + L] is None or cand[0] < best[i + L][0]:
                    best[i + L] = cand
        return best[n][1]

    def draft(self, text):
        pieces, extras, out = self.cut(text), [], []
        for w, kind in pieces:
            if kind == "other":
                if w.strip() and w not in "「」『』（）()":
                    out.append({"，": ",", "。": ".", "？": "?", "！": "!", "、": ",", "：": ":", "；": ";"}.get(w, w))
                continue
            if kind != "known":
                extras.append(w)
            rs = self.read.get(w) or self.listed.get(w) or []
            out.append("?" if not rs else rs[0] if len(rs) == 1 else "{" + "|".join(rs[:4]) + "}")
        s = re.sub(r" ([,.?!:;])", r"\1", " ".join(out))
        return s, list(dict.fromkeys(extras))


def make_packet(n):
    con, st = sqlite3.connect(DB), State()
    plan = read_plan()
    info = {(w["hanzi"], w["pinyin"]): w for w in untaught(con, st)}
    mine = [info[(r["hanzi"], r["pinyin"])] for r in plan if int(r["lesson"]) == n and (r["hanzi"], r["pinyin"]) in info]
    cats = {w["category"] for w in mine}
    left = [info[(r["hanzi"], r["pinyin"])] for r in plan
            if int(r["lesson"]) < n and int(r["lesson"]) in st.written and (r["hanzi"], r["pinyin"]) in info]
    left.sort(key=lambda w: (w["category"] not in cats,) + rank(w))
    rd = Reader(con, st, [w["hanzi"] for w in mine + left])
    clips = {e for (e,) in con.execute("SELECT entry_id FROM audio_clip WHERE accent = 'sixian' AND kind = 'ex'")}
    has_audio_table = bool(con.execute("SELECT count(*) FROM audio_clip").fetchone()[0])
    nex = dict(con.execute("SELECT entry_id, count(*) FROM example WHERE source = 'kaga115' AND accent = 'sixian' GROUP BY 1"))

    def flags(w):
        fl = []
        flat = lambda p: re.sub(r"\s+", "", p)
        others = [p for p in rd.listed.get(w["hanzi"], []) if py.key(p) != w["pkey"] and flat(p) != flat(w["pinyin"])]
        if len(CJK.findall(w["hanzi"])) != len(w["pkey"].split("-")):
            fl.append("SYL characters and syllables differ (a contraction): lint cannot align it, see how the lists write it")
        if others:
            fl.append("POLY " + ", ".join(others[:3]))
        decl = [f"{t} {p}" for t, p in st.declared.get(w["hanzi"], [])]
        if decl:
            fl.append("DECL " + ", ".join(decl))
        if not w["f"]:
            fl.append("f=0")
        return "; ".join(fl)

    def sentences(w):
        rows = con.execute(
            "SELECT x.hanzi, x.source, x.entry_id, x.mandarin FROM example x WHERE x.accent = 'sixian' "
            "AND x.source IN ('kaga115', 'kaga') AND x.hanzi LIKE ? ORDER BY x.source DESC", (f"%{w['hanzi'].strip('…')}%",)).fetchall()
        seen, out = set(), []
        for hz, src, eid, zh in rows:
            bare = re.sub(r"（[^）]*）", "", hz)     # brackets hold the southern Sixian variant
            if bare in seen:
                continue
            seen.add(bare)
            pin, extras = rd.draft(bare)
            audio = ""
            if src == "kaga115" and has_audio_table:
                audio = "audio" if eid in clips and nex.get(eid, 0) == 1 else "audio (clip shared)" if eid in clips else "no clip"
            out.append({"hanzi": bare, "src": src, "pin": pin, "extras": extras, "zh": zh or "", "audio": audio,
                        "own": eid == w["id"], "words": {x for x, k in rd.cut(bare) if k == "known"}})
        out.sort(key=lambda s: (len(s["extras"]), s["src"] != "kaga115", not s["own"], len(s["hanzi"])))
        return out

    L = [f"# Packet P{n} (generated by tools/packets.py: regenerate, do not edit)", ""]
    by = defaultdict(int)
    for w in mine:
        by[w["category"]] += 1
    L += [f"{len(mine)} words planned and still untaught · themes: "
          + ", ".join(f"{c} {k}" for c, k in sorted(by.items(), key=lambda x: -x[1])),
          "Aim: 40 or more new words in 20–30 lines. Start from the clean sentences, then write the links. "
          "Rules: `course/batches/card.md`; story: `course/batches/state.md`.", ""]
    allsent = {}
    for title, group in (("Words", mine), ("Left over from earlier packets (use what fits)", left[:20])):
        if not group:
            continue
        L += [f"## {title}", "", "| word | pinyin | level | Mandarin | English | type | flags |", "|---|---|---|---|---|---|---|"]
        for w in group:
            L.append(f"| {w['hanzi']} | {w['pinyin']} | {w['level']} | {w['mandarin'] or ''} | {w['english'] or ''} | "
                     f"{w['cognate'] or ''} | {flags(w)} |")
        L.append("")
    L += ["## Official sentences per word", ""]
    for w in mine + left[:20]:
        ss = sentences(w)
        moe = con.execute("SELECT count(*) FROM example WHERE source = 'moe' AND hanzi LIKE ?", (f"%{w['hanzi'].strip('…')}%",)).fetchone()[0]
        L.append(f"**{w['hanzi']}** {w['pinyin']} = {w['mandarin'] or ''} · official {len(ss)}, MOE {moe}")
        for s in ss[:3]:
            tag = "[clean]" if not s["extras"] else "[+ " + " ".join(s["extras"]) + "]"
            L.append(f"- {tag} {s['hanzi']} · {s['src']}{', ' + s['audio'] if s['audio'] else ''}")
            L.append(f"  - {s['pin']}")
            L.append(f"  - {s['zh']}")
            if not s["extras"]:
                allsent.setdefault(s["hanzi"], s)
        if not ss:
            L.append("- no official sentence: write the line, mark it `check: true`")
        L.append("")
    hz = {w["hanzi"].strip("…") for w in mine + left[:20]}
    multi = sorted(((len(hz & allsent[s]["words"]), s) for s in allsent if len(hz & allsent[s]["words"]) >= 2), reverse=True)
    L += ["## Clean sentences with two or more packet words", ""]
    L += [f"- ({k}) {s} · {allsent[s]['src']}" for k, s in multi] or ["- none"]
    L.append("")
    rp = os.path.join(ROOT, "course/batches/recycle.tsv")
    if os.path.exists(rp):
        rec = list(csv.DictReader(open(rp, encoding="utf-8"), delimiter="\t"))
        todo = todo_lessons(st)
        if rec and n in todo:
            i = todo.index(n)
            share = rec[i * len(rec) // len(todo):(i + 1) * len(rec) // len(todo)]
            L += ["## Recycle (Part 1 words no dialogue uses: not new words, use them in the text)", ""]
            L += [f"- {r['hanzi']} {r['pinyin']} = {r['en']} (lesson {r['lesson']})" for r in share] + [""]
    os.makedirs(PDIR, exist_ok=True)
    path = os.path.join(PDIR, f"P{n:02d}.md")
    open(path, "w", encoding="utf-8").write("\n".join(L))
    print(f"{os.path.relpath(path, ROOT)}: {len(mine)} words, {len(left)} left over, {len(allsent)} clean sentences, "
          f"{len(multi)} with 2+ packet words")


def status():
    con, st = sqlite3.connect(DB), State()
    plan = read_plan()
    un = {(w["hanzi"], w["pinyin"]) for w in untaught(con, st)}
    per = defaultdict(lambda: [0, 0])
    for r in plan:
        per[int(r["lesson"])][0] += 1
        per[int(r["lesson"])][1] += (r["hanzi"], r["pinyin"]) not in un
    for n in sorted(per):
        a, b = per[n]
        print(f"  P{n}: planned {a}, taught {b}" + ("" if n not in st.written else f", left over {a - b}"))
    print(f"untaught words outside the plan: {len(un - {(r['hanzi'], r['pinyin']) for r in plan})}")


def recycle():
    import lint
    rp = os.path.join(ROOT, "course/batches/recycle.tsv")
    rows = list(csv.DictReader(open(rp, encoding="utf-8"), delimiter="\t"))
    lines = []
    for f in sorted(glob.glob(os.path.join(ROOT, "course/perfectionnement/[0-9]*.yaml"))):
        for line in yaml.safe_load(open(f, encoding="utf-8")).get("dialogue") or []:
            b = line.get("sx") or {}
            ck = lint.char_keys(b, "sixian")
            if ck:
                lines.append(("".join(lint.hanzi_units(b.get("hanzi", ""))), ck))
    keep = []
    for r in rows:
        kk = py.key(r["pinyin"]).split("-")
        hit = any(t.find(r["hanzi"]) >= 0 and k[t.find(r["hanzi"]):t.find(r["hanzi"]) + len(kk)] == kk for t, k in lines)
        if not hit:
            keep.append(r)
    with open(rp, "w", encoding="utf-8", newline="") as f:
        out = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(keep)
    print(f"recycle.tsv: {len(rows)} → {len(keep)} words still unused")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["plan"]:
        make_plan("--force" in a)
    elif a[:1] == ["packet"] and len(a) == 2:
        make_packet(int(a[1].lstrip("Pp")))
    elif a[:1] == ["status"]:
        status()
    elif a[:1] == ["recycle"]:
        recycle()
    else:
        sys.exit(__doc__)
