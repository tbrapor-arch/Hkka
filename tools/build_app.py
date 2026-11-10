#!/usr/bin/env python3
"""Build the reader app: course/ + data/build/hakka.db -> app/dist/index.html (one self-contained file).

  python3 -I tools/build_app.py

Adapted from Tsheh-tû's tools/build_app.py. Every dialogue line is cut into dictionary words (the same segmenter as
tools/lint.py, preferring words already taught); each word gets a card from the 115年度 lists (then the 2013 lists,
then the MOE dictionary), with the course's own English gloss when the word is a new word somewhere in the course.
Part 1 lines carry both accents (Sixian sx, Hailu hl); 進修 lines are Sixian only.

Audio comes from a checkout of the public repo tbrapor-arch/Hkka-audio ($HKKA_AUDIO, default ../Hkka-audio):
  clips/index.json + clips/<accent>/<level>/<n>.m4a   客委會 recordings of the list words and their examples
  tts/manifest.json + tts/<accent>/<L>-<nn>.m4a        synthetic voice (VoxHakka) of titles (nn = 00), lines,
                                                       exercises (ex/<L>-f01, -t01) and words without a recording
Only the files the app uses are copied into app/dist/audio/. Without the checkout the app is built silent.
"""
import base64
import datetime
import glob
import io
import json
import os
import re
import sqlite3
import sys
import unicodedata

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pinyin as py  # noqa: E402
import sandhi  # noqa: E402
from lint import CJK, Lexicon  # noqa: E402

ROOT = os.path.dirname(HERE)
DIST = os.path.join(ROOT, "app/dist")
AUDIO = os.path.join(DIST, "audio")
ACC = {"sx": "sixian", "hl": "hailu"}
LEVELS = {"基礎級": 1, "初級": 2, "中級": 3, "中高級": 4, "高級": 5}

lex = Lexicon()
con = sqlite3.connect(os.path.join(ROOT, "data/build/hakka.db"))
AUDIO_SRC = os.environ.get("HKKA_AUDIO") or os.path.join(os.path.dirname(ROOT), "Hkka-audio")
_j = lambda *p: json.load(open(os.path.join(AUDIO_SRC, *p), encoding="utf-8")) if os.path.exists(os.path.join(AUDIO_SRC, *p)) else {}
CLIPS = _j("clips", "index.json")          # "sixian|<src_id>" -> {"w": path, "x": path}
TTS = _j("tts", "manifest.json")
USED = set()


def take(rel):
    """a file of the audio repo the app uses: copied at the end, returned as the app's URL"""
    if not os.path.exists(os.path.join(AUDIO_SRC, rel)):
        return None
    USED.add(rel)
    return "audio/" + rel


def tts_file(rel):
    return take("tts/" + rel)


def pkey(pinyin, acc):
    return "-".join(f"{s}{v or ''}" for s, v in py.syllables(pinyin, acc))


# ---------- lessons (Part 1 then 進修), in course order
part1 = sorted(glob.glob(os.path.join(ROOT, "course/lessons/[0-9]*.yaml")))
part2 = sorted(glob.glob(os.path.join(ROOT, "course/perfectionnement/[0-9]*.yaml")))
raw = []
for f in part1 + part2:
    d = yaml.safe_load(open(f, encoding="utf-8"))
    d["_p2"] = f in part2
    d["_lid"] = 100 + d["id"] if d["_p2"] else d["id"]
    raw.append(d)


def label(d):
    return f"進修 {d['id']}" if d["_p2"] else f"Lesson {d['id']}"


# course glosses and where each word is taught: (acc, hanzi, key) -> (English, lesson label)
taught = {}
for d in raw:
    for w in d.get("new_words") or []:
        for b, acc in ACC.items():
            blk = w if b == "sx" else w.get("hl")
            if not blk or not blk.get("pinyin"):
                continue
            k = pkey(blk["pinyin"], acc)
            taught.setdefault((acc, blk["hanzi"], k), (w.get("en") or "", label(d), d["_lid"]))

# ---------- word cards
cards = {}
TTS_WORDS = {}
for v in TTS.values():
    if v.get("kind") == "word" and v.get("file"):
        acc = v["file"].split("/")[0]
        TTS_WORDS.setdefault((acc, v["hanzi"], pkey(v["pinyin"], acc)), v["file"])


def card(acc, h, k, shown):
    cid = f"{acc}|{h}|{k}"
    if cid in cards:
        return cid
    c = {"h": h, "p": shown, "a": acc}
    row = con.execute("SELECT id, source, pinyin, level, mandarin, english, category, cognate, src_id FROM entry "
                      "WHERE hanzi=? AND pkey=? AND accent=? AND source IN ('kaga115','kaga') "
                      "ORDER BY source='kaga115' DESC LIMIT 1", (h, k, acc)).fetchone()
    eid = None
    if row:
        eid, src, p, lvl, mand, en, cat, cog, sid = row
        clip = CLIPS.get(f"{acc}|{sid}") if src == "kaga115" else None
        if clip:
            for kk, fld in (("w", "clip"), ("x", "exclip")):
                f = clip.get(kk) and take("clips/" + clip[kk])
                if f:
                    c[fld] = f
        c.update(src=src, p=p or shown)
        if lvl:
            c["lvl"] = lvl
        if mand:
            c["m"] = mand
        if en:
            c["en"] = en
        if cat:
            c["cat"] = cat
        if cog:
            c["cog"] = cog
    else:
        r = con.execute("SELECT e.id, r.pinyin, e.mandarin FROM entry e JOIN reading r ON r.entry_id=e.id "
                        "WHERE e.source='moe' AND e.hanzi=? AND r.accent=? AND r.pkey=? LIMIT 1", (h, acc, k)).fetchone()
        if r:
            eid, p, mand = r
            c.update(src="moe", p=p or shown)
            if mand:
                c["m"] = mand
            defs = [s for (s,) in con.execute("SELECT definition_zh FROM sense WHERE entry_id=? ORDER BY ord", (eid,)) if s]
            if defs:
                c["def"] = defs[:4]
    t = taught.get((acc, h, k))
    if t:
        c["g"], c["at"], c["atid"] = t
    if eid:
        ex = con.execute("SELECT hanzi, pinyin, mandarin, english FROM example WHERE entry_id=? AND hanzi!='' "
                         "ORDER BY (accent=?) DESC, id LIMIT 1", (eid, acc)).fetchone()
        if ex:
            c["ex"] = {k2: v for k2, v in zip(("h", "p", "m", "en"), ex) if v}
    if not c.get("clip") and (acc, h, k) in TTS_WORDS:      # no recording: the synthetic voice of the new word
        f = take("tts/" + TTS_WORDS[(acc, h, k)])
        if f:
            c["clip"], c["synth"] = f, 1
    cards[cid] = c
    return cid


# ---------- cutting a line into tokens
PUN = {"，": ", ", "。": ". ", "！": "! ", "？": "? ", "：": ": ", "、": ", ", "；": "; ", "「": "“", "」": "”", "……": "… "}
LATIN = re.compile(r"[A-Za-zÀ-ÿ'’]+(?:[ -][A-Z][a-zÀ-ÿ]+)*")


def tokens(hanzi, pinyin, acc, names, known, groups=None):
    """[{w: {h, p, id}} | {x: text}]. Falls back to one token for the whole line if characters and syllables
    cannot be aligned."""
    pin = pinyin
    for latin in re.findall(r"[A-Za-zÀ-ÿ]+", hanzi):
        pin = re.sub(rf"(?<![A-Za-zÀ-ÿ]){latin}(?![A-Za-zÀ-ÿ])", " ", pin, count=1)
    pin = pin.replace("___", " ")
    sylls = py.syllables(pin, acc)
    shown = re.findall(r"[A-Za-z]+[ˊˇˋ^+]?", pin)
    chars = CJK.findall(hanzi)
    if len(sylls) != len(chars) or len(shown) != len(chars):
        return [{"x": hanzi, "p": pinyin}]
    keys = [f"{s}{v or ''}" for s, v in sylls]
    # spoken tones: sandhi inside tone groups; a group ends at punctuation, a name, or a '|' of the `groups` field
    brk = set()
    if groups:
        n = 0
        for part in re.split(r"(\|)", groups):
            if part == "|":
                brk.add(n - 1)
            else:
                n += len(py.syllables(re.sub(r"[A-Za-zÀ-ÿ]+(?=\s|$)", lambda m: m.group(0) if py.syllables(m.group(0), acc) else "", part), acc))
    ci = -1
    for m in re.finditer(r"[㐀-鿿豈-﫿\U00020000-\U0003ffff]|[^㐀-鿿豈-﫿\U00020000-\U0003ffff]+", hanzi):
        if CJK.fullmatch(m.group(0)):
            ci += 1
        elif m.group(0).strip() and ci >= 0:
            brk.add(ci)
    rule = sandhi.apply_hailu if acc == "hailu" else sandhi.apply
    spoken, grp = [], []
    for i, sv in enumerate(sylls):
        grp.append(sv)
        if i in brk or i == len(sylls) - 1:
            spoken += rule(grp)
            grp = []
    vals = [v or "" for _, v in sylls]
    svals = [v or "" for _, v in spoken]
    # units: CJK chars (with their syllable index) and the text between them
    units, ci = [], 0
    for m in re.finditer(r"[㐀-鿿豈-﫿\U00020000-\U0003ffff]|[^㐀-鿿豈-﫿\U00020000-\U0003ffff]+", hanzi):
        s = m.group(0)
        if CJK.fullmatch(s):
            units.append(ci)
            ci += 1
        else:
            units.append(s)
    out, run = [], []

    def flush():
        if not run:
            return
        text = "".join(chars[i] for i in run)
        N = len(run)
        best = [None] * (N + 1)
        best[0] = (0, [])
        for i in range(N):
            if best[i] is None:
                continue
            c0, path = best[i]
            opts = []
            nm = next((n for n in sorted(names, key=len, reverse=True) if text.startswith(n, i)), None)
            if nm:
                opts.append((len(nm), 0, "name"))
            for L in range(1, min(lex.maxlen, N - i) + 1):
                w, k = text[i:i + L], "-".join(keys[run[i]:run[i] + L])
                if k in lex.words[acc].get(w, ()):
                    opts.append((L, 1 if (w, k) in known else 9 * L + 1, "word"))
            if not any(L == 1 for L, _, _ in opts):
                opts.append((1, 100, "char"))
            for L, c, kind in opts:
                cand = (c0 + c, path + [(i, L, kind)])
                if best[i + L] is None or cand[0] < best[i + L][0]:
                    best[i + L] = cand
        for i, L, kind in best[N][1]:
            idx = run[i:i + L]
            h = "".join(chars[j] for j in idx)
            p = " ".join(shown[j] for j in idx)
            w = {"h": h, "p": p, "v": "-".join(vals[j] for j in idx)}
            sv = "-".join(svals[j] for j in idx)
            if sv != w["v"]:
                w["s"] = sv
            if kind == "word":
                w["id"] = card(acc, h, "-".join(keys[j] for j in idx), p)
            out.append({"w": w})
        run.clear()

    for u in units:
        if isinstance(u, int):
            run.append(u)
        else:
            flush()
            for part in re.findall(r"……|[A-Za-zÀ-ÿ'’]+|.", u, re.S):
                if part.strip():
                    out.append({"x": part, **({"name": 1} if LATIN.fullmatch(part) else {})})
                elif part == " " and out:
                    pass
    flush()
    return out


def block(b, acc, names, known, extra=()):
    if not b or not b.get("hanzi"):
        return None
    o = {"h": b["hanzi"], "p": b.get("pinyin", ""), "t": tokens(b["hanzi"], b.get("pinyin", ""), acc, names, known, b.get("groups"))}
    for k in extra:
        if b.get(k):
            o[k] = b[k]
    return o


def lid_str(d):
    return f"P{d['id']:02d}" if d["_p2"] else f"{d['id']:03d}"


lessons = []
known = set()
for d in raw:
    names = set(d.get("names") or [])
    for w in d.get("new_words") or []:
        known.add((w["hanzi"], pkey(w["pinyin"], "sixian")))
    lines = []
    for ln in d["dialogue"]:
        o = {"n": ln["n"], "sp": ln.get("speaker") or "", "en": ln["en"]}
        for b, acc in ACC.items():
            blk = block(ln.get(b), acc, names, known if b == "sx" else set())
            if blk:
                o[b] = blk
                a = tts_file(f"{acc}/{lid_str(d)}-{ln['n']:02d}.m4a")
                if a:
                    blk["audio"] = a
        if ln.get("check"):
            o["check"] = 1
        if ln.get("source"):
            o["src"] = ln["source"]
        lines.append(o)
    nw = []
    for w in d.get("new_words") or []:
        o = {"en": w.get("en", "")}
        for b, acc in ACC.items():
            blk = w if b == "sx" else w.get("hl")
            if blk and blk.get("hanzi") and blk.get("pinyin"):
                o[b] = {"h": blk["hanzi"], "p": blk["pinyin"],
                        "id": card(acc, blk["hanzi"], pkey(blk["pinyin"], acc), blk["pinyin"])}
        nw.append(o)
    ex = []
    for kind, items in (d.get("exercises") or {}).items():
        for j, it in enumerate(items or [], 1):
            o = {"kind": kind, "en": it.get("en", "")}
            for b, acc in ACC.items():
                blk = block(it.get(b), acc, names, known if b == "sx" else set(), ("answer", "answer_hanzi"))
                if blk:
                    a = tts_file(f"{acc}/ex/{lid_str(d)}-{kind[0]}{j:02d}.m4a")
                    if a:
                        blk["audio"] = a
                    o[b] = blk
            ex.append(o)
    t = d["title"]
    title = {"en": t.get("en", "")}
    for b, acc in ACC.items():
        if t.get(b):
            title[b] = {"h": t[b]["hanzi"], "p": t[b]["pinyin"]}
            a = tts_file(f"{acc}/{lid_str(d)}-00.m4a")
            if a:
                title[b]["audio"] = a
    lessons.append({"id": d["_lid"], "p2": d["_p2"], "title": title, "review": bool(d.get("review")),
                    "genre": d.get("genre", "dialogue"), "setting": d.get("setting", ""), "lines": lines,
                    "notes": [{"ref": n.get("ref", 0), "topic": n.get("topic", ""), "text": n.get("text", "")}
                              for n in d.get("notes") or []],
                    "words": nw, "ex": ex})


# ---------- lesson 0 (Markdown)
def md(text):
    try:
        import markdown
        return markdown.markdown(text, extensions=["tables", "fenced_code"])
    except ImportError:   # plain fallback: paragraphs and headings only
        out = []
        for para in re.split(r"\n\s*\n", text):
            p = para.strip()
            m = re.match(r"(#+)\s*(.*)", p)
            out.append(f"<h{len(m.group(1))}>{m.group(2)}</h{len(m.group(1))}>" if m else f"<p>{p}</p>")
        return "\n".join(out)


lesson0 = md(open(os.path.join(ROOT, "course/lessons/000-reading-pinyin.md"), encoding="utf-8").read())


# ---------- rare characters: glyphs from Plangothic (SIL OFL), only those the app uses
def _in_big5(ch):
    try:
        ch.encode("cp950")
        return True
    except UnicodeEncodeError:
        return False


def ext_font_css(text):
    fdir = os.path.join(ROOT, "data/raw/plangothic/package/fonts")
    if not os.path.isdir(fdir):
        print("no Plangothic in data/raw (make data): rare characters use the device's fonts")
        return ""
    from fontTools import subset
    from fontTools.ttLib import TTFont
    rare = sorted({ch for ch in text if (0x3400 <= ord(ch) <= 0x9fff or ord(ch) >= 0x20000 or 0xf900 <= ord(ch) <= 0xfaff)
                   and not _in_big5(ch)})
    chunks = {}
    for ch in rare:
        base = ord(ch) & ~0xff
        for plane in ("P1", "P2"):
            p = os.path.join(fdir, f"Plangothic{plane}-400-{base:06x}.woff2")
            if os.path.exists(p):
                chunks.setdefault(p, []).append(ord(ch))
                break
    css = []
    for p, cps in chunks.items():
        font = TTFont(p)
        have = [c for c in cps if c in font.getBestCmap()]
        if not have:
            continue
        sub = subset.Subsetter(subset.Options(flavor="woff2", layout_features=[], name_IDs=["*"]))
        sub.populate(unicodes=have)
        sub.subset(font)
        font.flavor = "woff2"
        buf = io.BytesIO()
        font.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        rng = ",".join(f"U+{c:X}" for c in have)
        css.append(f"@font-face{{font-family:'HakkaExt';font-display:swap;src:url(data:font/woff2;base64,{b64}) "
                   f"format('woff2');unicode-range:{rng};}}")
    print(f"embedded {sum(len(c) for c in chunks.values())} rare characters in {len(css)} font chunks")
    return "\n".join(css)


def rom_font_css():
    """Noto Sans (OFL) embedded so pinyin looks the same on every device: Latin, plus the three Hakka tone letters
    ˊ ˇ ˋ (U+02CA, U+02C7, U+02CB) that the Latin subsets of web fonts leave out."""
    css = []
    for f, rng in (("noto-sans-latin.woff2", None), ("noto-sans-tones.woff2", "U+02C7,U+02CA,U+02CB,U+02D9")):
        b64 = base64.b64encode(open(os.path.join(ROOT, "app/fonts", f), "rb").read()).decode()
        css.append("@font-face{font-family:'HakkaRom';font-weight:100 900;font-display:swap;"
                   f"src:url(data:font/woff2;base64,{b64}) format('woff2');{f'unicode-range:{rng};' if rng else ''}}}")
    return "\n".join(css)


data = {"lessons": lessons, "dict": cards, "lesson0": lesson0, "built": datetime.date.today().isoformat()}
payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
tpl = open(os.path.join(ROOT, "app/index.template.html"), encoding="utf-8").read()
tpl = tpl.replace("/*__FONTS__*/", rom_font_css() + "\n" + ext_font_css(payload))
os.makedirs(DIST, exist_ok=True)
out = os.path.join(DIST, "index.html")
html = tpl.replace("/*__DATA__*/null", payload.replace("<", "\\u003c"))
open(out, "w", encoding="utf-8").write(unicodedata.normalize("NFC", html))
# ---------- copy the audio the app uses
import shutil  # noqa: E402
for rel in sorted(USED):
    dst = os.path.join(AUDIO, rel)
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(AUDIO_SRC, rel), dst)
n_lines = sum(1 for L in lessons for ln in L["lines"] for b in ACC if ln.get(b, {}).get("audio"))
print(f"audio: {len(USED)} files from {AUDIO_SRC if USED else 'nowhere (no Hkka-audio checkout)'}, {n_lines} lines voiced")
n_tok = sum(1 for L in lessons for ln in L["lines"] for b in ACC if b in ln for t in ln[b]["t"] if "w" in t)
n_card = sum(1 for L in lessons for ln in L["lines"] for b in ACC if b in ln for t in ln[b]["t"] if t.get("w", {}).get("id"))
n_whole = sum(1 for L in lessons for ln in L["lines"] for b in ACC if b in ln if len(ln[b]["t"]) == 1 and "x" in ln[b]["t"][0])
n_clip = sum(1 for c in cards.values() if c.get("clip"))
print(f"{os.path.relpath(out, ROOT)}: {len(lessons)} lessons, {len(cards)} cards ({n_clip} with a clip), "
      f"{n_card}/{n_tok} word tokens with a card, {n_whole} lines not split, {os.path.getsize(out) // 1024} KB")
