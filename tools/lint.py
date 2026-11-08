#!/usr/bin/env python3
"""Check lesson files against the vocabulary database (Tsheh-tû's lint, for two accents).

  python3 -I tools/lint.py [lesson.yaml ...]      (default: course/lessons/[0-9]*.yaml, in order)

Per line, for Sixian (sx) and Hailu (hl):
  E  characters and pinyin do not have the same number of syllables (one character = one syllable)
  E  a tone mark that does not exist for that accent, or a syllable unknown to the accent
  E  a character not found with any reading in that accent's lists or the MOE dictionary
  W  a word whose reading differs from the lists (shows the attested readings)
  E  `groups` is not the pinyin with | added; `source:` line not an exact official sentence
Per lesson:
  E  missing fields; a dialogue line without both accents; a review lesson with new words
  E  a new word not in the lists for that accent, or already declared in an earlier lesson
  W  a new word not used in the lesson; a word used before it is taught (names excepted)
  W  new-word count outside the syllabus target, or more Hakka-only / false-friend words than the cap (pacing.md)
Exit code 1 if any E.
"""
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
CJK = re.compile(r"[㐀-鿿豈-﫿\U00020000-\U0003ffff]")
ACC = {"sx": "sixian", "hl": "hailu"}
HARD = {"false-friend", "hakka-only"}
# Particles the lists only contain inside longer entries: 啊 in 動啊着 tungˊ a doˋ / tungˋ a+ doˊ, 睞啊過 (kaga), and
# in the MOE example sentences 嗒看啊, 試看啊, 看看啊 (VV啊 and V看啊, lesson 36).
PARTICLES = {"sixian": {"啊": "a55", "吔": "le24"}, "hailu": {"啊": "a33"}}
# 吔: the 115年度 lists write the sentence-final particle 吔 in Sixian (about 650 sentences, against 6 with 了) but give
# it no reading; the course reads it as MOE's 了 leˊ (le24). Hailu writes 咧 leˋ, which the lists have as a word.


def caps(n):
    return 6 if n <= 27 else 8 if n <= 48 else 10


class Lexicon:
    def __init__(self):
        con = sqlite3.connect(DB)
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
                    self.inv[acc].update(re.sub(r"\d+$", "", s) for s in k.split("-"))
            for hz, k in PARTICLES[acc].items():   # attested only inside listed phrases, never as a headword
                self.words[acc][hz].add(k)
            py.set_inventory(self.inv[acc], acc)
        self.maxlen = max(len(h) for h in self.words["sixian"])
        self.info = {}
        for hz, k, cog, lvl in con.execute("SELECT hanzi, pkey, cognate, level FROM entry WHERE source='kaga115' AND accent='sixian'"):
            self.info.setdefault((hz, k), (cog, lvl))
        self.examples = {h for (h,) in con.execute("SELECT hanzi FROM example UNION SELECT hanzi FROM sentence")}


def hanzi_units(h):
    return CJK.findall(h)


def segment(lex, acc, hanzi, pinyin, names, known=frozenset()):
    """Align characters with syllables and cut into dictionary words. Returns (words, messages).
    words: [(hanzi, key)]; messages: [(level, text)]. Among the possible cuts, prefer words already taught or new in
    this lesson (`known`, Sixian only), then fewer words: 愛去哪位 → 愛 去 哪位 when those are taught, even though the
    lists also contain the phrase."""
    msgs, out = [], []
    chars = hanzi_units(hanzi)
    for latin in re.findall(r"[A-Za-zÀ-ÿ]+", hanzi):   # a name kept in Latin letters (Sam): same token in both lines
        pinyin = re.sub(rf"(?<![A-Za-zÀ-ÿ]){latin}(?![A-Za-zÀ-ÿ])", " ", pinyin, count=1)
    sylls = py.syllables(pinyin, acc)
    if len(chars) != len(sylls):
        return out, [("E", f"{len(chars)} characters but {len(sylls)} syllables: cannot align")]
    for s, v in sylls:
        if v is None:
            msgs.append(("E", f"{s}: tone mark not used in {acc}"))
        if s not in lex.inv[acc]:
            msgs.append(("E", f"{s}: not a {acc} syllable"))
    keys = [f"{s}{v or ''}" for s, v in sylls]
    text = "".join(chars)
    N = len(chars)
    best = [None] * (N + 1); best[0] = (0, [])
    for i in range(N):
        if best[i] is None:
            continue
        cost0, path = best[i]
        opts = []
        name = next((nm for nm in sorted(names, key=len, reverse=True) if text.startswith(nm, i)), None)
        if name:
            opts.append((len(name), 0, None))
        for L in range(1, min(lex.maxlen, N - i) + 1):
            w, k = text[i:i + L], "-".join(keys[i:i + L])
            if k in lex.words[acc].get(w, ()):
                # taught/new word: 1; untaught word: 9 per character + 1 (a whole untaught word still beats its
                # characters one by one, but never beats a cut into taught words)
                opts.append((L, 1 if (w, k) in known or acc != "sixian" else 9 * L + 1, (w, k)))
        # AABB reduplication of a listed AB word (清清楚楚, 歡歡喜喜): counts as a use of AB (lesson 95)
        if N - i >= 4 and text[i] == text[i + 1] and text[i + 2] == text[i + 3] and keys[i] == keys[i + 1] \
                and keys[i + 2] == keys[i + 3]:
            w, k = text[i] + text[i + 2], f"{keys[i]}-{keys[i + 2]}"
            if k in lex.words[acc].get(w, ()):
                opts.append((4, 1 if (w, k) in known or acc != "sixian" else 9 * 4 + 1, (w, k)))
        if not any(L == 1 for L, _, _ in opts):
            opts.append((1, 100, ("?", i)))
        for L, c, item in opts:
            cand = (cost0 + c, path + ([item] if item else []))
            if best[i + L] is None or cand[0] < best[i + L][0]:
                best[i + L] = cand
    for item in best[N][1]:
        if item[0] == "?":
            j = item[1]; c, k = chars[j], keys[j]
            found = lex.words[acc].get(c)
            if not found:
                msgs.append(("E", f"{c} not found in the {acc} lists or the MOE dictionary"))
            else:
                msgs.append(("W", f"{c} {k}: reading not attested alone in {acc} (lists: {', '.join(sorted(found)[:4])})"))
            out.append((c, k))
        else:
            out.append(item)
    return out, msgs


def lesson_files(args):
    return args or sorted(glob.glob(os.path.join(ROOT, "course/lessons/[0-9]*.yaml")))


def load_syllabus():
    p = os.path.join(ROOT, "course/syllabus.yaml")
    if not os.path.exists(p):
        return {}
    return {l["n"]: l for l in (yaml.safe_load(open(p, encoding="utf-8")) or {}).get("lessons", [])}


def main():
    files = lesson_files(sys.argv[1:])
    lex = Lexicon()
    syl = load_syllabus()
    taught = {}          # (hanzi, key) → lesson id, Sixian
    errors = 0

    def say(path, where, level, text):
        nonlocal errors
        print(f"{os.path.relpath(path, ROOT)}:{where}: {level} {text}")
        errors += level == "E"

    for path in files:
        d = yaml.safe_load(open(path, encoding="utf-8"))
        n = d.get("id", 0)
        names = set(d.get("names") or [])
        for f in ("id", "title", "dialogue", "notes", "new_words"):
            if f not in d:
                say(path, 0, "E", f"missing field: {f}")
        new = d.get("new_words") or []
        if d.get("review") and new:
            say(path, "new_words", "E", "a review lesson adds no new words")
        new_keys = set()
        for w in new:
            k = py.key(w.get("pinyin", ""))
            hz = w.get("hanzi", "")
            if k not in lex.words["sixian"].get(hz, ()):
                say(path, "new_words", "E", f"{hz} {w.get('pinyin')}: not in the Sixian lists with this reading "
                    f"(lists: {', '.join(sorted(lex.words['sixian'].get(hz, ()))) or 'none'})")
            if (hz, k) in taught:
                say(path, "new_words", "E", f"{hz} {w.get('pinyin')}: already new in lesson {taught[(hz, k)]}")
            hl = w.get("hl")
            if hl:
                hk = py.key(hl.get("pinyin", ""), "hailu")
                if hk not in lex.words["hailu"].get(hl.get("hanzi", ""), ()):
                    say(path, "new_words", "W", f"hl {hl.get('hanzi')} {hl.get('pinyin')}: not in the Hailu lists with this reading")
            new_keys.add((hz, k))

        used = set()

        def check(where, block, acc_key):
            if not block:
                return
            acc = ACC[acc_key]
            words, msgs = segment(lex, acc, block.get("hanzi", ""), block.get("pinyin", ""), names,
                                  frozenset(taught) | new_keys)
            for lv, t in msgs:
                say(path, where, lv, f"{acc_key} {t}")
            g = block.get("groups")
            if g and re.sub(r"\s*\|\s*", " ", g).strip() != (block.get("pinyin") or "").strip():
                say(path, where, "E", f"{acc_key} groups must equal pinyin with | added between tone groups")
            if acc == "sixian":
                used.update(words)

        for line in d.get("dialogue") or []:
            where = f"line {line.get('n', '?')}"
            if not line.get("en"):
                say(path, where, "E", "missing en")
            for a in ("sx", "hl"):
                if not (line.get(a) or {}).get("hanzi") or not (line.get(a) or {}).get("pinyin"):
                    say(path, where, "E", f"missing {a} hanzi/pinyin (both accents are written alongside)")
                check(where, line.get(a), a)
            src = line.get("source")
            if src and (line.get("sx") or {}).get("hanzi") not in lex.examples:
                say(path, where, "E", f"marked source: {src} but not an exact official sentence")
        for kind, items in (d.get("exercises") or {}).items():
            for j, it in enumerate(items or []):
                for a in ("sx", "hl"):
                    b = dict(it.get(a) or {})
                    if not b:
                        continue
                    b["hanzi"] = b.get("hanzi", "").replace("___", b.get("answer_hanzi", ""))
                    b["pinyin"] = b.get("pinyin", "").replace("___", b.get("answer", ""))
                    check(f"exercises.{kind}[{j}]", b, a)

        for hz, k in sorted(new_keys - used):
            say(path, "new_words", "W", f"{hz}: declared new but not used in the lesson")
        for hz, k in sorted(used - new_keys - set(taught)):
            say(path, "words", "W", f"{hz} {k}: used before it is taught (add to new_words, or teach it earlier)")
        for k in new_keys:
            taught.setdefault(k, n)

        plan = syl.get(n)
        if plan and not d.get("review"):
            target = plan.get("new")
            if target and not (target - 3 <= len(new) <= target + 3):
                say(path, "new_words", "W", f"{len(new)} new words; the syllabus target is {target} (±3)")
            hard = [hz for hz, k in new_keys if lex.info.get((hz, k), ("?",))[0] in HARD]
            if len(hard) > caps(n):
                say(path, "new_words", "W", f"{len(hard)} Hakka-only / false-friend words (cap {caps(n)}): {' '.join(hard)}")
    print(f"{len(files)} file(s), {errors} error(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
