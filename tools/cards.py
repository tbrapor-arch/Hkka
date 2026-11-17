"""Words and word cards, ONE implementation for every module: the lint (tools/lint.py), the app (tools/build_app.py)
and the private books reader (Hkka-private/tools/build_reader.py). A word is cut and gets its card the same way in a
lesson line, an exercise or a book chapter.

    import cards
    lex = cards.Lexicon()                          # the lists, the MOE dictionary, course/supplement.yaml
    lex.add_supplement(path)                       # optional: another supplement file (the private books' one)
    cards.cut(lex, 'sixian', text, keys, names, known, forced)   # -> [(i, L, kind, (hanzi, key))]
    C = cards.Cards(lex, con, taught)              # taught = cards.taught_words(lesson dicts)
    C.card('sixian', '今晡日', 'gim24-bu24-ngid2', 'gimˊ buˊ ngidˋ')   # -> card id; C.cards[id] is the card

The cut (one rule everywhere): among all cuts of a run of characters into words of the lexicon, the cheapest one.
A name of the line costs 0; a word already taught or new in this lesson (`known`), or a word the text forces
(`forced`: a book's own notes and glossary), or any word when `known` is None, costs 1; any other word 9 per
character + 1 (so a whole word still beats its characters, and never beats a cut into taught words); a character
alone that the lexicon does not have with that reading costs 100. AABB of a listed AB word (清清楚楚) counts as AB.

The card: the 115年度 list (then the 2013 list), else the MOE dictionary (definitions), else the supplement file
(words no list has, with their English); plus the course's English and the lesson that teaches it (`taught`), and one
example sentence. Audio is added by the caller (the app knows where the recordings are; the reader has none).
"""
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
SUPPLEMENT = os.path.join(ROOT, "course/supplement.yaml")
CJK = re.compile(r"[㐀-鿿豈-﫿\U00020000-\U0003ffff]")
ACC = {"sx": "sixian", "hl": "hailu"}
# Particles the lists only contain inside longer entries: 啊 in 動啊着 tungˊ a doˋ / tungˋ a+ doˊ, 睞啊過 (kaga), and
# in the MOE example sentences 嗒看啊, 試看啊, 看看啊 (VV啊 and V看啊, lesson 36).
PARTICLES = {"sixian": {"啊": "a55", "吔": "le24"}, "hailu": {"啊": "a33"}}
# 吔: the 115年度 lists write the sentence-final particle 吔 in Sixian (about 650 sentences, against 6 with 了) but give
# it no reading; the course reads it as MOE's 了 leˊ (le24). Hailu writes 咧 leˋ, which the lists have as a word.


def key(pinyin, acc="sixian"):
    return "-".join(f"{s}{v or ''}" for s, v in py.syllables(pinyin, acc))


class Lexicon:
    """words[acc][hanzi] = {key}: every attested (hanzi, reading) pair of the lists and the MOE dictionary.
    supp[acc][hanzi] = {key: (pinyin, English, file)}: words no list has, from the supplement file(s). The cut uses
    both; lint reports a supplement word in a lesson, since no list attests it."""

    def __init__(self, db=DB, supplement=SUPPLEMENT):
        con = sqlite3.connect(db)
        self.words = {a: defaultdict(set) for a in ACC.values()}
        self.inv = {a: set() for a in ACC.values()}
        for acc in ACC.values():
            q = ("SELECT hanzi, pkey FROM entry WHERE source IN ('kaga115','kaga') AND accent=? AND pkey != '' "
                 "UNION SELECT e.hanzi, r.pkey FROM entry e JOIN reading r ON r.entry_id = e.id WHERE r.accent=? "
                 "UNION SELECT v.hanzi, e.pkey FROM variant v JOIN entry e ON e.id = v.entry_id WHERE e.accent=? AND v.hanzi IS NOT NULL "
                 "UNION SELECT e.hanzi, v.pkey FROM variant v JOIN entry e ON e.id = v.entry_id WHERE e.accent=? AND v.pkey IS NOT NULL")
            for hz, k in con.execute(q, (acc, acc, acc, acc)):
                if hz and k:
                    self.words[acc][hz].add(k)
                    stem = hz.strip("…").replace("...", "")   # a pattern entry (當在該…, 拜…): its stem is a word too
                    if stem and stem != hz and len(stem) == len(k.split("-")):
                        self.words[acc][stem].add(k)
                    self.inv[acc].update(re.sub(r"\d+$", "", s) for s in k.split("-"))
            for hz, k in PARTICLES[acc].items():   # attested only inside listed phrases, never as a headword
                self.words[acc][hz].add(k)
            py.set_inventory(self.inv[acc], acc)
        self.maxlen = max(len(h) for h in self.words["sixian"])
        self.info = {}
        for hz, k, cog, lvl in con.execute("SELECT hanzi, pkey, cognate, level FROM entry WHERE source='kaga115' AND accent='sixian'"):
            self.info.setdefault((hz, k), (cog, lvl))
        self.examples = {h for (h,) in con.execute("SELECT hanzi FROM example UNION SELECT hanzi FROM sentence")}
        # Official sentences give the southern Sixian (or other accent) variant in brackets: 買豆油轉來（歸來）. A line
        # quoting the sentence without the brackets is still that sentence.
        self.examples |= {re.sub(r"（[^）]*）", "", h) for h in self.examples if "（" in h}
        # per table, for `source:` (the Sixian sentences of the official lists; MOE examples carry no accent)
        self.pool = {t: set() for t in ("kaga115", "kaga", "moe", "sentence")}
        for src, h in con.execute("SELECT source, hanzi FROM example WHERE source = 'moe' OR accent = 'sixian' "
                                  "UNION SELECT 'sentence', hanzi FROM sentence"):
            if src in self.pool and h:
                self.pool[src].update((h, re.sub(r"（[^）]*）", "", h)))
        self.supp = {a: defaultdict(dict) for a in ACC.values()}
        if supplement:
            self.add_supplement(supplement)

    def add_supplement(self, path):
        """A supplement file: words: {hanzi: [pinyin, English]} (Sixian), optional hailu: {hanzi: [pinyin, English]}."""
        if not os.path.exists(path):
            return 0
        d = yaml.safe_load(open(path, encoding="utf-8")) or {}
        n = 0
        for sect, acc in (("words", "sixian"), ("hailu", "hailu")):
            for hz, (p, en) in (d.get(sect) or {}).items():
                k = key(p, acc)
                if k:
                    self.supp[acc][hz][k] = (p, en, os.path.basename(path))
                    self.maxlen = max(self.maxlen, len(hz))
                    n += 1
        return n

    def has(self, acc, w, k):
        return k in self.words[acc].get(w, ()) or k in self.supp[acc].get(w, ())


def cut(lex, acc, text, keys, names=(), known=None, forced=()):
    """text: the characters of one run (no punctuation), keys: one tone-value key per character.
    -> [(i, L, kind, (hanzi, key))], kind 'name' | 'word' | 'char' ('char': no word of the lexicon covers it)."""
    N = len(text)
    names = sorted(names or (), key=len, reverse=True)
    best = [None] * (N + 1)
    best[0] = (0, [])

    def cost(w, k, L):
        return 1 if known is None or (w, k) in known or w in forced else 9 * L + 1

    for i in range(N):
        if best[i] is None:
            continue
        c0, path = best[i]
        opts = []
        nm = next((n for n in names if text.startswith(n, i)), None)
        if nm:
            opts.append((len(nm), 0, "name", (nm, "-".join(keys[i:i + len(nm)]))))
        for L in range(1, min(lex.maxlen, N - i) + 1):
            w, k = text[i:i + L], "-".join(keys[i:i + L])
            if lex.has(acc, w, k) or (w in forced and L > 1):
                opts.append((L, cost(w, k, L), "word", (w, k)))
        # AABB reduplication of a listed AB word (清清楚楚, 歡歡喜喜): counts as a use of AB (lesson 95)
        if N - i >= 4 and text[i] == text[i + 1] and text[i + 2] == text[i + 3] and keys[i] == keys[i + 1] \
                and keys[i + 2] == keys[i + 3]:
            w, k = text[i] + text[i + 2], f"{keys[i]}-{keys[i + 2]}"
            if lex.has(acc, w, k):
                opts.append((4, cost(w, k, 4), "word", (w, k)))
        if not any(o[0] == 1 for o in opts):
            opts.append((1, 100, "char", (text[i], keys[i])))
        for L, c, kind, item in opts:
            cand = (c0 + c, path + [(i, L, kind, item)])
            if best[i + L] is None or cand[0] < best[i + L][0]:
                best[i + L] = cand
    return best[N][1]


def taught_words(lessons):
    """lessons: lesson dicts in course order, each with _p2 (進修) and _lid -> {(acc, hanzi, key): (English, label, lid)}"""
    out = {}
    for d in lessons:
        lab = f"進修 {d['id']}" if d.get("_p2") else f"Lesson {d['id']}"
        for w in d.get("new_words") or []:
            for b, acc in ACC.items():
                blk = w if b == "sx" else w.get("hl")
                if blk and blk.get("pinyin"):
                    out.setdefault((acc, blk["hanzi"], key(blk["pinyin"], acc)), (w.get("en") or "", lab, d["_lid"]))
    return out


def load_lessons(root=ROOT):
    import glob
    part1 = sorted(glob.glob(os.path.join(root, "course/lessons/[0-9]*.yaml")))
    part2 = sorted(glob.glob(os.path.join(root, "course/perfectionnement/[0-9]*.yaml")))
    raw = []
    for f in part1 + part2:
        d = yaml.safe_load(open(f, encoding="utf-8"))
        d["_p2"] = f in part2
        d["_lid"] = 100 + d["id"] if d["_p2"] else d["id"]
        raw.append(d)
    return raw


class Cards:
    """cards[id] = the card of (accent, hanzi, key); id = 'accent|hanzi|key'. meta[id] = (source, src_id) for the
    caller's audio lookup."""

    def __init__(self, lex, con=None, taught=None):
        self.lex = lex
        self.con = con or sqlite3.connect(DB)
        self.taught = taught or {}
        self.cards, self.meta = {}, {}

    def card(self, acc, h, k, shown, strict=False):
        """the card id; None when strict and no list, dictionary or supplement has the word (the reader's rule)"""
        cid = f"{acc}|{h}|{k}"
        if cid in self.cards:
            return cid
        if cid in self.meta and self.meta[cid] is None:
            return None
        c = {"h": h, "p": shown, "a": acc}
        con = self.con
        row = con.execute("SELECT id, source, pinyin, level, mandarin, english, category, cognate, src_id FROM entry "
                          "WHERE hanzi=? AND pkey=? AND accent=? AND source IN ('kaga115','kaga') "
                          "ORDER BY source='kaga115' DESC LIMIT 1", (h, k, acc)).fetchone()
        eid, meta = None, (None, None)
        if row:
            eid, src, p, lvl, mand, en, cat, cog, sid = row
            meta = (src, sid)
            c.update(src=src, p=p or shown)
            for f, v in (("lvl", lvl), ("m", mand), ("en", en), ("cat", cat), ("cog", cog)):
                if v:
                    c[f] = v
        else:
            r = con.execute("SELECT e.id, r.pinyin, e.mandarin FROM entry e JOIN reading r ON r.entry_id=e.id "
                            "WHERE e.source='moe' AND e.hanzi=? AND r.accent=? AND r.pkey=? LIMIT 1", (h, acc, k)).fetchone()
            if r:
                eid, p, mand = r
                meta = ("moe", None)
                c.update(src="moe", p=p or shown)
                if mand:
                    c["m"] = mand
                defs = [s for (s,) in con.execute("SELECT definition_zh FROM sense WHERE entry_id=? ORDER BY ord", (eid,)) if s]
                if defs:
                    c["def"] = defs[:4]
            elif k in self.lex.supp[acc].get(h, {}):
                p, en, f = self.lex.supp[acc][h][k]
                meta = ("supplement", None)
                c.update(src="supplement", p=p or shown, en=en)
        t = self.taught.get((acc, h, k))
        if t:
            c["g"], c["at"], c["atid"] = t
        if strict and meta[0] is None and not t:
            self.meta[cid] = None
            return None
        if eid:
            ex = con.execute("SELECT hanzi, pinyin, mandarin, english FROM example WHERE entry_id=? AND hanzi!='' "
                             "ORDER BY (accent=?) DESC, id LIMIT 1", (eid, acc)).fetchone()
            if ex:
                c["ex"] = {k2: v for k2, v in zip(("h", "p", "m", "en"), ex) if v}
        self.cards[cid] = c
        self.meta[cid] = meta
        return cid
