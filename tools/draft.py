#!/usr/bin/env python3
"""Write a 進修 lesson from a draft that has no pinyin: the pinyin comes from the words already taught and the lists.

  python3 -I tools/draft.py course/drafts/P36.txt        # → course/perfectionnement/36.yaml, then run make lint

The writer types characters and English only. This tool cuts every line into words, takes each word's reading
(the one taught first, else the list's), marks a line that is an exact official sentence with its `source:`, and
builds `new_words`. It prints what it could not decide. lint remains the check: this tool only saves the typing.

Draft format (`|` separates fields; a line starting with # is a comment):

    id: 36
    genre: dialogue
    title: 正月半 | The fifteenth of the first month
    setting: Tuesday 27 February 2029 …
    names: Sam, 阿明=aˊ minˇ, 苗栗=meuˇ lid      # a name that is not a taught word needs its reading
    == lines
    阿婆 | 今晡日正月半。 | Today is the fifteenth.            # speaker | characters | English
    阿婆 | 你[好|hau]食無？ | Do you like it? | check        # [word|reading] forces a reading; flags after the English:
                                                             # check, abridged, ok:rule-id, kaga115 / kaga / moe
     | 一行無人講个話。 | A line of prose. |                   # no speaker in prose genres
    == notes
    0 | culture | The title is …                             # line number | topic | text
    == words
    挼 | roll between the palms                              # new word | English (reading from the plan or the lists)
    落[lau] | come loose and fall                            # reading given when the lists have more than one
    == translate
    用勺嫲舀水。 | Scoop up water with the ladle.
    == fill
    雞嫲___。 | 孵卵 | The hen is sitting on her eggs.          # sentence with ___ | answer | English

Report:
  NEW?     a word that is not taught and not in `== words`: add it there, or change the line
  UNUSED   a word of `== words` that no line uses
  PICK     a word with more than one taught reading: the first was used. Force another with [word|reading]
  SOURCE   the line is an exact official sentence: `source:` was added
"""
import csv
import os
import re
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pinyin as py  # noqa: E402
import packets  # noqa: E402

ROOT = os.path.dirname(HERE)
CJK = packets.CJK
PMAP = {"，": ",", "。": ".", "？": "?", "！": "!", "、": ",", "：": ":", "；": ";", "（": "(", "）": ")"}
DROP = "「」『』《》〈〉"


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


class Drafter:
    def __init__(self, new, names, out):
        self.con = sqlite3.connect(packets.DB)
        self.st = packets.State(skip=out)
        self.rd = packets.Reader(self.con, self.st, list(new) + list(names))
        self.names = names                       # hanzi → reading or None (a taught word)
        self.new = new                           # hanzi → reading
        self.multi = {}                          # hanzi → taught readings, when more than one
        for hz, decl in self.st.declared.items():
            keys = {}
            for _, p in decl:
                keys.setdefault(py.key(p), p)
            if len(keys) > 1:
                self.multi[hz] = list(keys.values())
        for hz, p in names.items():
            if p:
                self.rd.read[hz] = [p]
        for hz, p in new.items():
            if hz in self.st.declared:           # a second reading of taught characters: must be forced in the line
                self.multi[hz] = self.rd.read[hz][:1] + [p] + [x for x in self.multi.get(hz, []) if py.key(x) != py.key(p)][1:]
                if p not in self.rd.read[hz]:
                    self.rd.read[hz].append(p)
            else:
                self.rd.read[hz] = [p]
        self.used, self.report = set(), []
        self.pool = {}
        for src in ("kaga", "kaga115"):
            for (h,) in self.con.execute("SELECT hanzi FROM example WHERE source = ? AND accent = 'sixian'", (src,)):
                self.pool[h] = src
                self.pool[re.sub(r"（[^）]*）", "", h)] = src

    def pinyin(self, text, where):
        """Characters → pinyin. [word|reading] forces a reading."""
        forced = {}
        def take(m):
            forced.setdefault(m.group(1), []).append(m.group(2).strip())
            return "\x01" + m.group(1) + "\x02"
        marked = re.sub(r"\[([^|\]]+)\|([^\]]+)\]", take, text)
        plain = marked.replace("\x01", "").replace("\x02", "")
        out = []
        for m in re.finditer(r"\x01[^\x02]*\x02|[㐀-鿿豈-﫿\U00020000-\U0003ffff]+|[A-Za-zÀ-ÿ]+|_+|.", marked, flags=re.S):
            tok = m.group()
            if tok[0] == "\x01":
                w = tok[1:-1]
                out.append(forced[w].pop(0))
                self.used.add(w)
            elif CJK.match(tok):
                for w, kind in self.rd.cut(tok):
                    self.used.add(w)
                    rs = self.rd.read.get(w) or self.rd.listed.get(w) or []
                    if kind != "known":
                        self.report.append(f"NEW?   {where}: {w} ({', '.join(self.rd.listed.get(w, ['not in the lists'])[:3])})")
                    elif w in self.multi and w not in self.names:
                        self.report.append(f"PICK   {where}: {w} → {rs[0]} (also {', '.join(x for x in self.multi[w] if x != rs[0])})")
                    out.append(rs[0] if rs else "?")
            elif tok in PMAP:
                out.append(PMAP[tok])
            elif tok in DROP or tok.isspace():
                continue
            else:
                out.append(tok)
        s = " ".join(out)
        s = re.sub(r"\s+([,.?!:;)])", r"\1", s)
        s = re.sub(r"\(\s+", "(", s)
        return plain, re.sub(r"\s+", " ", s).strip()


def parse(path):
    head, sec, cur = {}, {"lines": [], "notes": [], "words": [], "translate": [], "fill": []}, None
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("== "):
            cur = line[3:].strip()
            continue
        if cur is None:
            k, v = line.split(":", 1)
            head[k.strip()] = v.strip()
        else:
            sec[cur].append([f.strip() for f in line.split("|")] if "[" not in line else split_fields(line))
    return head, sec


def split_fields(line):
    """Split on | outside [word|reading]."""
    out, cur, depth = [], "", 0
    for ch in line:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth = max(0, depth - 1)
        if ch == "|" and not depth:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    return out + [cur.strip()]


def main(path):
    head, sec = parse(path)
    n = int(head["id"])
    names = {}
    for item in filter(None, (x.strip() for x in head.get("names", "").split(","))):
        hz, _, p = item.partition("=")
        names[hz.strip()] = p.strip() or None
    plan = {}
    pp = os.path.join(ROOT, "course/packets/plan.tsv")
    if os.path.exists(pp):
        for r in csv.DictReader(open(pp, encoding="utf-8"), delimiter="\t"):
            plan.setdefault(r["hanzi"], r["pinyin"])
    con = sqlite3.connect(packets.DB)
    new, glosses, problems = {}, {}, []
    for f in sec["words"]:
        m = re.match(r"(.+?)\[(.+)\]$", f[0])
        hz, p = (m.group(1), m.group(2)) if m else (f[0], None)
        if not p:
            p = plan.get(hz)
        if not p:
            rs = [r for (r,) in con.execute("SELECT DISTINCT pinyin FROM entry WHERE hanzi = ? AND accent = 'sixian' "
                                            "AND pinyin != '' ORDER BY source DESC", (hz,))]
            if len(rs) != 1:
                problems.append(f"WORD   {hz}: {len(rs)} list readings ({', '.join(rs[:4])}): write {hz}[reading]")
                continue
            p = rs[0]
        new[hz] = packets.re.sub(r"\s+", " ", p.replace("\xa0", " ")).strip()
        glosses[hz] = f[1]
    out = os.path.join(ROOT, f"course/perfectionnement/{n:02d}.yaml")
    d = Drafter(new, names, out)
    L = [f"id: {n}", f"genre: {head['genre']}", "title:"]
    th, _, te = head["title"].partition("|")
    hz, pin = d.pinyin(th.strip(), "title")
    L += [f"  en: {q(te.strip())}", f"  sx: {{hanzi: {q(hz)}, pinyin: {q(pin)}}}", f"review: {'true' if head['genre'] == 'review' else 'false'}",
          "setting: >-"]
    words, cur = head["setting"].split(), "  "
    for w in words:
        if len(cur) + len(w) > 116:
            L.append(cur.rstrip())
            cur = "  "
        cur += w + " "
    L += [cur.rstrip(), f"names: [{', '.join(names)}]", "", "dialogue:"]
    sources = 0
    for i, f in enumerate(sec["lines"], 1):
        f += [""] * (4 - len(f))
        hz, pin = d.pinyin(f[1], f"line {i}")
        flags = f[3].split()
        L.append(f"  - n: {i}")
        if f[0]:
            L.append(f"    speaker: {f[0]}")
        L.append(f"    en: {q(f[2])}")
        src = next((x for x in flags if x in ("kaga115", "kaga", "moe", "sentence")), None) or d.pool.get(hz)
        if src:
            L.append(f"    source: {src}")
            sources += 1
            if src == d.pool.get(hz) and src not in flags:
                d.report.append(f"SOURCE line {i}: {src}")
        L.append(f"    sx: {{hanzi: {q(hz)}, pinyin: {q(pin)}}}")
        if "abridged" in flags:
            L.append("    abridged: true")
        if "check" in flags and not src:
            L.append("    check: true")
        ok = [x[3:] for x in flags if x.startswith("ok:")]
        if ok:
            L.append(f"    ok: [{', '.join(ok)}]")
    L += ["", "notes:"]
    for f in sec["notes"]:
        L += [f"  - ref: {int(f[0])}", f"    topic: {f[1]}", "    text: >"]
        cur = "      "
        for w in " | ".join(f[2:]).split():
            if len(cur) + len(w) > 116:
                L.append(cur.rstrip())
                cur = "      "
            cur += w + " "
        L.append(cur.rstrip())
    L += ["", "new_words:"]
    for hz, p in new.items():
        L.append(f"  - {{hanzi: {q(hz)}, pinyin: {q(p)}, en: {q(glosses[hz])}}}")
    L += ["", "exercises:", "  translate:"]
    for i, f in enumerate(sec["translate"], 1):
        hz, pin = d.pinyin(f[0], f"translate {i}")
        L.append(f"    - en: {q(f[1])}")
        if d.pool.get(hz):
            L.append(f"      source: {d.pool[hz]}")
        L.append(f"      sx: {{hanzi: {q(hz)}, pinyin: {q(pin)}}}")
    L.append("  fill:")
    for i, f in enumerate(sec["fill"], 1):
        a, b = f[0].split("___")
        (h1, p1), (h2, p2), (ha, pa) = d.pinyin(a, f"fill {i}"), d.pinyin(b, f"fill {i}"), d.pinyin(f[1], f"fill {i}")
        pin = re.sub(r"\s+([,.?!:;])", r"\1", f"{p1} ___ {p2}".strip())
        L.append(f"    - en: {q(f[2])}")
        L.append(f"      sx: {{hanzi: {q(h1 + '___' + h2)}, pinyin: {q(pin)}, answer_hanzi: {q(ha)}, answer: {q(pa)}}}")
    L += ["", "audio: []", ""]
    open(out, "w", encoding="utf-8").write("\n".join(L))
    used_in_lines = d.used
    for hz in new:
        if hz not in used_in_lines:
            problems.append(f"UNUSED {hz}")
    for r in problems + sorted(set(d.report), key=lambda r: (r.split()[0] != "NEW?", r)):
        print(r)
    print(f"{os.path.relpath(out, ROOT)}: {len(sec['lines'])} lines, {len(new)} new words, {sources} official sentences, "
          f"{sum(r.startswith('NEW?') for r in set(d.report))} undeclared, {len(problems)} problems")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
