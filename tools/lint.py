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
進修 (Part 2) only, added 10 Nov 2026 so that reviews no longer have to look for these by hand:
  E  `source:` (dialogue and exercises) names a table that does not hold the sentence; `abridged: true` = part of one
  W  a pattern from course/batches/rules.yaml (checklist rules a script can check); `ok: [rule-id]` on the line silences it
  W  a new word used only in the exercises; a new word whose characters were already used in an earlier lesson
  W  a new word whose characters are already declared under another reading
  W  a review lesson that reuses fewer than 3 new words from one of the six lessons before it
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


def load_rules():
    p = os.path.join(ROOT, "course/batches/rules.yaml")
    if not os.path.exists(p):
        return []
    rules = (yaml.safe_load(open(p, encoding="utf-8")) or {}).get("rules", [])
    for r in rules:
        r["re"] = re.compile(r["hanzi"])
    return rules


def check_source(lex, src, hanzi, abridged):
    """None if `source: src` is right for this sentence, else the message."""
    if src not in lex.pool:
        return f"source: {src} is not a table (kaga115, kaga, moe, sentence)"
    if hanzi in lex.pool[src]:
        return None
    if abridged:
        if any(hanzi.rstrip("。！？") in h for h in lex.pool[src]):
            return None
        return f"abridged: true, but no {src} sentence contains it"
    other = [t for t in lex.pool if hanzi in lex.pool[t]]
    if other:
        return f"marked source: {src} but the sentence is in {', '.join(other)}"
    return f"marked source: {src} but not an exact official sentence"


def char_keys(block, acc):
    """Tone-value key of each character of a block, or None when characters and syllables do not align."""
    hanzi, pinyin = block.get("hanzi", ""), block.get("pinyin", "")
    for latin in re.findall(r"[A-Za-zÀ-ÿ]+", hanzi):
        pinyin = re.sub(rf"(?<![A-Za-zÀ-ÿ]){latin}(?![A-Za-zÀ-ÿ])", " ", pinyin, count=1)
    sylls = py.syllables(pinyin, acc)
    if len(sylls) != len(hanzi_units(hanzi)):
        return None
    return [f"{s}{v or ''}" for s, v in sylls]


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
    return args or (sorted(glob.glob(os.path.join(ROOT, "course/lessons/[0-9]*.yaml")))
                    + sorted(glob.glob(os.path.join(ROOT, "course/perfectionnement/[0-9]*.yaml"))))


def is_part2(path):
    """進修 (Perfectionnement) lessons: Sixian only, id N stands for internal id 100 + N."""
    return os.path.basename(os.path.dirname(os.path.abspath(path))) == "perfectionnement"


# The checks on new words added on 10 Nov 2026 start with the lessons written after them: P1–P35 were reviewed by hand
# and their findings of these kinds (幾久 used in lesson 96 before P1 declares it, 逐 dagˋ / giugˋ) were accepted.
CHECK_FROM = 36
NEW_FROM = 36         # checks added after batch 9: exercises repeating the text, 'from lesson N' notes

GENRES = {"dialogue", "article", "letter", "interview", "tale", "speech", "essay", "document", "song", "news",
          "play", "diary", "debate", "story", "review"}


def load_syllabus():
    p = os.path.join(ROOT, "course/syllabus.yaml")
    if not os.path.exists(p):
        return {}
    return {l["n"]: l for l in (yaml.safe_load(open(p, encoding="utf-8")) or {}).get("lessons", [])}


def main():
    files = lesson_files(sys.argv[1:])
    lex = Lexicon()
    syl = load_syllabus()
    rules = load_rules()
    earlier = []         # (lesson tag, where, characters, keys) of every Sixian line so far
    new_by_lesson = {}   # 進修 id → set of (hanzi, key)
    read_as = defaultdict(dict)   # hanzi → {key: lesson tag}
    taught = {}          # (hanzi, key) → lesson id, Sixian
    errors = 0

    def say(path, where, level, text):
        nonlocal errors
        print(f"{os.path.relpath(path, ROOT)}:{where}: {level} {text}")
        errors += level == "E"

    for path in files:
        d = yaml.safe_load(open(path, encoding="utf-8"))
        part2 = is_part2(path)
        n = d.get("id", 0) + (100 if part2 else 0)
        accents = ("sx",) if part2 else ("sx", "hl")
        if part2:
            if d.get("genre", "dialogue") not in GENRES:
                say(path, "genre", "E", f"unknown genre {d.get('genre')!r} (one of {', '.join(sorted(GENRES))})")
            nl = len(d.get("dialogue") or [])
            if not 20 <= nl <= 30:
                say(path, "dialogue", "W", f"{nl} lines; 進修 lessons have 20–30")
            ex = d.get("exercises") or {}
            for kind in ("translate", "fill"):
                if len(ex.get(kind) or []) != 5:
                    say(path, f"exercises.{kind}", "W", f"{len(ex.get(kind) or [])} items; 進修 has 5")
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
            if part2 and d.get("id", 0) >= CHECK_FROM:
                for k0, tag0 in read_as[hz].items():
                    if k0 != k:
                        say(path, "new_words", "W", f"{hz} {w.get('pinyin')}: same characters already declared as {k0} "
                            f"in lesson {tag0}: check that the gloss says which sense this is")
                if len(hz) > 1 and (hz, k) not in taught:
                    kk = k.split("-")
                    for tag0, where0, text0, keys0 in earlier:
                        i = text0.find(hz)
                        if i >= 0 and keys0[i:i + len(kk)] == kk:
                            say(path, "new_words", "W", f"{hz}: already used in lesson {tag0} ({where0}) before it is taught here")
                            break
            read_as[hz].setdefault(k, ("P" if part2 else "") + str(d.get("id")))

        used = set()
        used_dialogue = set()
        lines_here = []

        def check_rules(where, item, block, quoted):
            text = block.get("hanzi", "")
            keys = None
            for r in rules:
                if (quoted and not r.get("quotes")) or r["id"] in (item.get("ok") or []):
                    continue
                for m in r["re"].finditer(text):
                    if r.get("key"):
                        keys = keys or char_keys(block, "sixian")
                        a = len(hanzi_units(text[:m.start()]))
                        b = a + len(hanzi_units(m.group()))
                        if not keys or r["key"] not in "-".join(keys[a:b]):
                            continue
                    say(path, where, "W", f"rule {r['id']}: {m.group()} — {r['msg']}")
                    break

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
                ck = char_keys(block, "sixian")
                if ck:
                    lines_here.append((where, "".join(hanzi_units(block.get("hanzi", ""))), ck))
            return words

        for line in d.get("dialogue") or []:
            where = f"line {line.get('n', '?')}"
            if not line.get("en"):
                say(path, where, "E", "missing en")
            for a in accents:
                if not (line.get(a) or {}).get("hanzi") or not (line.get(a) or {}).get("pinyin"):
                    say(path, where, "E", f"missing {a} hanzi/pinyin" + ("" if part2 else " (both accents are written alongside)"))
                ws = check(where, line.get(a), a)
                if a == "sx":
                    used_dialogue.update(ws or ())
            if part2 and line.get("sx"):
                check_rules(where, line, line["sx"], bool(line.get("source")))
            if part2 and line.get("hl"):
                say(path, where, "W", "進修 is Sixian only: hl block ignored")
            src = line.get("source")
            if src and part2:
                msg = check_source(lex, src, (line.get("sx") or {}).get("hanzi", ""), line.get("abridged"))
                if msg:
                    say(path, where, "E", msg)
            elif src and (line.get("sx") or {}).get("hanzi") not in lex.examples:
                say(path, where, "E", f"marked source: {src} but not an exact official sentence")
        for kind, items in (d.get("exercises") or {}).items():
            for j, it in enumerate(items or []):
                for a in accents:
                    b = dict(it.get(a) or {})
                    if not b:
                        continue
                    b["hanzi"] = b.get("hanzi", "").replace("___", b.get("answer_hanzi", ""))
                    b["pinyin"] = b.get("pinyin", "").replace("___", b.get("answer", ""))
                    check(f"exercises.{kind}[{j}]", b, a)
                    if part2 and a == "sx":
                        check_rules(f"exercises.{kind}[{j}]", it, b, bool(it.get("source")))
                        if it.get("source"):
                            msg = check_source(lex, it["source"], b["hanzi"], it.get("abridged"))
                            if msg:
                                say(path, f"exercises.{kind}[{j}]", "E", msg)

        for hz, k in sorted(new_keys - used):
            say(path, "new_words", "W", f"{hz}: declared new but not used in the lesson")
        for hz, k in sorted(used - new_keys - set(taught)):
            say(path, "words", "W", f"{hz} {k}: used before it is taught (add to new_words, or teach it earlier)")
        for k in new_keys:
            taught.setdefault(k, n)
        if part2:
            for hz, k in sorted(new_keys & used - used_dialogue) if d.get("id", 0) >= CHECK_FROM else ():
                say(path, "new_words", "W", f"{hz}: new word used only in the exercises (進修: every new word is in the text)")
            new_by_lesson[d.get("id")] = set(new_keys)
            if d.get("id", 0) >= NEW_FROM:
                strip = lambda t: re.sub(r"[\s，。！？、：；「」『』…—,.!?:;\"]", "", t or "")
                text = [strip((l.get("sx") or {}).get("hanzi")) for l in d.get("dialogue") or []]
                for kind, items in (d.get("exercises") or {}).items():
                    for j, it in enumerate(items or []):
                        sx = it.get("sx") or {}
                        full = strip(sx.get("hanzi", "").replace("___", sx.get("answer_hanzi", "")))
                        if len(full) >= 5 and any(full == t or (len(full) >= 7 and full in t) for t in text):
                            say(path, f"exercises.{kind}[{j}]", "W", "repeats a line of the lesson's own text: write a new sentence")
                where_taught = {}
                for (hz, _k), m in taught.items():
                    where_taught.setdefault(hz, m)
                for note in d.get("notes") or []:
                    for hz, part, num in re.findall(r"([\u3400-\u9fff\U00020000-\U0002ffff]+)[^.;:()\u3400-\u9fff]*?\b(?:is|are) from (進修|lesson) (\d+)", note.get("text", "")):
                        want = int(num) + (100 if part == "進修" else 0)
                        got = where_taught.get(hz)
                        if got is not None and got != want:
                            name = f"進修 {got - 100}" if got > 100 else f"lesson {got}"
                            say(path, f"notes[{note.get('ref')}]", "W", f"{hz} is taught in {name}, not in {part} {num}")
            if d.get("review"):
                for m in range(d.get("id") - 6, d.get("id")):
                    got = len(new_by_lesson.get(m, set()) & used_dialogue)
                    if m in new_by_lesson and new_by_lesson[m] and got < 3:
                        say(path, "dialogue", "W", f"review reuses {got} new word(s) of 進修 {m}; at least 3 from each of the six lessons before")
        tag = ("P" if part2 else "") + str(d.get("id"))
        earlier.extend((tag, w0, t0, k0) for w0, t0, k0 in lines_here)

        if part2 and not d.get("review") and not 32 <= len(new) <= 55:
            say(path, "new_words", "W", f"{len(new)} new words; 進修 aims at about 40")
        plan = None if part2 else syl.get(n)
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
