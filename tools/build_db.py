#!/usr/bin/env python3
"""Build data/build/hakka.db from the open sources in data/raw (see data/fetch.sh).

  python3 -I tools/build_db.py data/raw data/build/hakka.db
Set HAKKA_PRIVATE=/path/to/Hkka-private to also load the private Glossika sentences (local build only).
"""
import csv, json, os, re, sqlite3, sys, unicodedata
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pinyin as py  # noqa: E402

ACCENTS = {"四": "sixian", "海": "hailu", "大": "dapu", "平": "raoping", "安": "zhaoan", "南": "south-sixian"}
KAGA_ACCENTS = {"四縣": "sixian", "海陸": "hailu", "大埔": "dapu", "饒平": "raoping", "詔安": "zhaoan"}
SOURCES = [
    ("moe", "教育部臺灣客家語常用詞辭典 (via g0v/moedict-data-hakka)", "2023 data", "CC BY-ND 3.0 TW", 1, "unaltered only",
     "Headwords, six-accent readings, definitions, examples. Mandarin comparison table is not under the licence."),
    ("kaga", "客家委員會 客語能力認證基本詞彙 (102年版, via Taiwanese-Corpus/hakka_elearning)", "2013", "Government work; same lists now published under 政府資料開放授權條款-第1版 on data.gov.tw", 1, "with attribution",
     "Certification vocabulary per accent and level, English glosses, example sentences."),
    ("kaga115", "客家委員會 客語能力認證詞彙 115年度 (基礎級 to 高級) and 基礎級暨初級題庫", "2026",
     "政府資料開放授權條款-第1版 (data.gov.tw 176002)", 1, "with attribution",
     "Committed in data/gov/115/. Five accents, parallel numbering. The core source of the course."),
    ("glossika", "Glossika Mass Sentences — Hakka Sixian/Hailu, Fluency 1-3 (private)", "2015", "All rights reserved", 0, "never",
     "Loaded only from a local Hkka-private checkout. Do not publish anything derived verbatim."),
]


def nfc(s):
    return unicodedata.normalize("NFC", s or "").strip()


def load_moe(db, raw):
    data = json.load(open(raw / "moedict-data-hakka" / "dict-hakka.json", encoding="utf-8"))
    sylls = Counter()
    for e in data:
        for h in e["heteronyms"]:
            for m in re.finditer(r"([四海大平安南])⃞(\S+)", h.get("pinyin", "")):
                if m.group(1) == "四":
                    sylls.update(a for a, _ in py.syllables(m.group(2)))
    py.set_inventory(set(sylls))
    db.executemany("INSERT INTO syllable VALUES (?,?)", sylls.items())

    n = 0
    for e in data:
        title = nfc(e["title"])
        for h in e["heteronyms"]:
            reads = {ACCENTS[m.group(1)]: m.group(2) for m in re.finditer(r"([四海大平安南])⃞(\S+)", h.get("pinyin", ""))}
            sx = reads.get("sixian")
            cur = db.execute(
                "INSERT INTO entry(source, src_id, hanzi, pinyin, pkey, toneless, pos) VALUES ('moe',?,?,?,?,?,?)",
                (h.get("audio_id"), title, py.marked(sx) if sx else None, py.key(sx) if sx else None,
                 py.toneless(sx) if sx else None, None))
            eid = cur.lastrowid; n += 1
            for acc, p in reads.items():
                db.execute("INSERT INTO reading VALUES (?,?,?,?)", (eid, acc, p, py.key(p)))
            for i, d in enumerate(h.get("definitions", [])):
                sid = db.execute("INSERT INTO sense(entry_id, ord, pos, definition_zh) VALUES (?,?,?,?)",
                                 (eid, i, d.get("type"), nfc(d.get("def")))).lastrowid
                for ex in d.get("example", []):
                    m = re.match(r"￹(.*?)(?:￺(.*?))?￻(.*)", ex)
                    if m:
                        db.execute("INSERT INTO example(entry_id, sense_id, source, accent, hanzi, pinyin, mandarin) "
                                   "VALUES (?,?,?,?,?,?,?)", (eid, sid, "moe", "sixian", nfc(m.group(1)), nfc(m.group(2)), nfc(m.group(3))))
            for rel, key in (("synonym", "synonyms"), ("antonym", "antonyms")):
                for o in re.split(r"[、,，]", h.get(key, "") or ""):
                    if o.strip():
                        db.execute("INSERT INTO relation VALUES (?,?,?)", (eid, nfc(o), rel))
    print(f"moe: {n} entries, {len(sylls)} Sixian syllables")


def _expand_slashes(text):
    """'gimˊ/ginˊ buˊ ngidˋ' → ['gimˊ buˊ ngidˋ', 'ginˊ buˊ ngidˋ']: a slash offers alternatives for one token."""
    tokens = text.split()
    if not any("/" in t for t in tokens):
        return [text] if text else []
    out = []
    width = max(len(t.split("/")) for t in tokens)
    for k in range(width):
        out.append(" ".join(t.split("/")[min(k, len(t.split("/")) - 1)] for t in tokens))
    return [nfc(x) for x in dict.fromkeys(out)]


def _take_groups(s, open_, close):
    """Remove top-level groups delimited by open_/close (nesting allowed); return (rest, [group contents])."""
    rest, groups, depth, cur = [], [], 0, []
    for ch in s:
        if ch in open_:
            if depth: cur.append(ch)
            depth += 1
        elif ch in close and depth:
            depth -= 1
            if depth: cur.append(ch)
            else: groups.append("".join(cur)); cur = []
        elif depth:
            cur.append(ch)
        else:
            rest.append(ch)
    return "".join(rest), groups


def split_alts(s):
    """'窗框(窗門框、窗斗)' → ('窗框', ['窗門框','窗斗']); 'gimˊ/ginˊ buˊ ngidˋ' → ('gimˊ buˊ ngidˋ', ['ginˊ buˊ ngidˋ']);
    'nai vi【nai eˋ (lai/nai eˊ)】' → ('nai vi', ['nai eˋ', 'lai eˊ', 'nai eˊ'])."""
    s = nfc(s)
    rest, groups = _take_groups(s, "【[", "】]")
    rest, paren = _take_groups(rest, "(（", ")）")
    groups += paren
    mains = _expand_slashes(nfc(rest))
    alts = mains[1:]
    for g in groups:
        for part in re.split(r"[、，,]", g):
            sub_main, sub_alts = split_alts(part) if part.strip() else ("", [])
            alts += [a for a in [sub_main] + sub_alts if a]
    return (mains[0] if mains else ""), [a for a in dict.fromkeys(alts) if a and a != (mains[0] if mains else "")]


def load_kaga(db, raw):
    base = raw / "hakka_elearning" / "合併"
    cats = {}
    with open(base / "原始.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cats[(nfc(r["客家語言"]), r["腔調"])] = nfc(r.get("類別"))
    n = 0
    with open(base / "網站詞目補造字.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            acc = KAGA_ACCENTS.get(r["腔調"])
            if not acc:
                continue
            hz, hz_alts = split_alts(r["客家語言"])
            p, p_alts = split_alts(r["客語音標"])
            sixian = acc == "sixian"
            eid = db.execute(
                "INSERT INTO entry(source, src_id, hanzi, accent, pinyin, pkey, toneless, level, category, mandarin, english, audio_url) "
                "VALUES ('kaga',?,?,?,?,?,?,?,?,?,?,?)",
                (r["編號"], hz, acc, p, py.key(p) if sixian else None, py.toneless(p) if sixian else None, r["等級"],
                 cats.get((nfc(r["客家語言"]), r["腔調"])), nfc(r["華語辭義(限100字)"]), nfc(r["英語詞義(限200字)"]),
                 r["客語音檔網址"])).lastrowid
            n += 1
            for a in hz_alts:
                db.execute("INSERT INTO variant VALUES (?,?,?,?,?)", (eid, a, None, None, "hanzi-alt"))
            for a in p_alts:
                db.execute("INSERT INTO variant VALUES (?,?,?,?,?)", (eid, None, a, py.key(a) if sixian else None, "reading-alt"))
            if r["客語例句"].strip():
                db.execute("INSERT INTO example(entry_id, source, accent, hanzi, mandarin, audio_url) VALUES (?,?,?,?,?,?)",
                           (eid, "kaga", acc, nfc(r["客語例句"]), nfc(r["華語翻譯"]), r["客語例句網址"]))
    print(f"kaga: {n} entries (all accents)")


def load_glossika(db, private):
    path = Path(private) / "data" / "glossika" / "sentences.jsonl"
    if not path.exists():
        print(f"glossika: {path} not found, skipped"); return
    lookup = {}
    for eid, hz in db.execute("SELECT id, hanzi FROM entry WHERE source IN ('kaga','kaga115') AND accent='sixian' ORDER BY source='kaga115', id DESC"):
        lookup[hz] = eid
    for eid, hz in db.execute("SELECT id, hanzi FROM entry WHERE source='moe' AND pkey IS NOT NULL ORDER BY id DESC"):
        lookup.setdefault(hz, eid)
    n = 0
    for line in open(path, encoding="utf-8"):
        r = json.loads(line); sx, hl = r["sx"], r["hl"]
        db.execute("INSERT INTO glossika VALUES (?,?,?,?,?,?,?,?,?,?)",
                   (r["id"], r["book"], r["en"], sx["hanzi"], sx["rom"], sx["ipa"], hl["hanzi"], hl["rom"], hl["ipa"],
                    int(sx["aligned"] and hl["aligned"])))
        hz = re.sub(r"[，。？！、：；,.?!:;「」『』（）()…—–\-“”\"]", " ", sx["hanzi"]).split()
        rom = [w for w in re.split(r"\s+", re.sub(r"[,.?!:;—–()…“”\"]", " ", sx["rom"])) if w]
        for i, w in enumerate(hz):
            db.execute("INSERT INTO glossika_word VALUES (?,?,?,?,?)",
                       (r["id"], i, w, rom[i] if sx["aligned"] and i < len(rom) else None, lookup.get(w)))
        n += 1
    print(f"glossika: {n} sentences (private)")


ACC_ZH = {"四縣腔": "sixian", "海陸腔": "hailu", "大埔腔": "dapu", "饒平腔": "raoping", "詔安腔": "zhaoan", "南四縣腔": "south-sixian"}
HAN = re.compile(r"[\u3400-\u9fff\uf900-\ufaff\U00020000-\U0003ffff]+")


def load_corpus(db, path):
    """臺灣客語語料庫 CSV → corpus table, then word counts over the Sixian texts by longest match on known words."""
    if not path.exists():
        print(f"corpus: {path} not found, skipped"); return
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    for r in rows:
        accs = ",".join(ACC_ZH.get(a.strip(), a.strip()) for a in r["Accent"].split("、"))
        db.execute("INSERT INTO corpus(title, relation, mode, accents, year, content) VALUES (?,?,?,?,?,?)",
                   (nfc(r["Title"]), nfc(r["Relation"]), nfc(r["Mode"]), accs, int(r["Date"].strip() or 0), nfc(r["Content"])))
    words = {hz for (hz,) in db.execute("SELECT hanzi FROM entry WHERE (source='moe' AND pkey IS NOT NULL) OR (source IN ('kaga','kaga115') AND accent='sixian')")}
    longest = max(len(w) for w in words)
    count, docs = Counter(), Counter()
    texts = [c for (c,) in db.execute("SELECT content FROM corpus WHERE ',' || accents || ',' LIKE '%,sixian,%'")]
    for t in texts:
        t = re.sub(r"<[^>]+>[^<]*</[^>]+>|<[^>]+>|（[0-9：－:\-]+）|[男女]\d*：", " ", t)
        seen = set()
        for run in HAN.findall(t):
            i = 0
            while i < len(run):
                for L in range(min(longest, len(run) - i), 0, -1):
                    w = run[i:i + L]
                    if L == 1 or w in words:
                        count[w] += 1; seen.add(w); i += L
                        break
        docs.update(seen)
    db.executemany("INSERT INTO corpus_freq VALUES (?,?,?)", [(w, n, docs[w]) for w, n in count.items()])
    db.execute("UPDATE entry SET corpus_freq = (SELECT count FROM corpus_freq f WHERE f.hanzi = entry.hanzi)")
    print(f"corpus: {len(rows)} texts, {len(texts)} Sixian, {sum(count.values())} Sixian word tokens")


S100_ACC = {"si": "sixian", "ha": "hailu", "da": "dapu", "ra": "raoping", "zh": "zhaoan", "nsi": "south-sixian"}
# The file types tone marks with look-alike punctuation; checked against the MOE readings for Sixian (’=ˊ ‘=ˋ).
S100_MARKS = str.maketrans({"’": "ˊ", "‘": "ˋ", "＋": "+", "^": "ˆ", "？": "?"})


def load_sentences100(db, path):
    if not path.exists():
        print(f"sentences100: {path} not found, skipped"); return
    n = dmg = 0
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        r = {k: (v or "").strip() for k, v in r.items()}
        acc = S100_ACC.get(r["accent"])
        u = r["URL"].replace("hakka.v.tw", "hakka.gov.tw")
        y = re.search(r"/public/(?:20)?(12|14)/", u)
        num = re.search(r"(\d+)\.mp3$", u)
        hz = nfc(r["hakka"])
        # a '?' inside the sentence (not the final question mark) is a character lost in an encoding conversion
        damaged = int(bool(re.search(r"\?(?!\s*$)", hz) or re.search("[\ue000-\uf8ff]", hz)))
        p = re.sub(r"\s+", " ", nfc(r["phonetic"]).translate(S100_MARKS)).strip()
        db.execute("INSERT INTO sentence(set_year, num, accent, hanzi, hanzi_damaged, mandarin, pinyin, pinyin_raw, pkey, audio_url) "
                   "VALUES (?,?,?,?,?,?,?,?,?,?)",
                   (2000 + int(y.group(1)) if y else None, int(num.group(1)) if num else None, acc, hz, damaged,
                    nfc(r["chinese"]), p, r["phonetic"], py.key(p) if acc == "sixian" else None, u))
        n += 1; dmg += damaged
    print(f"sentences100: {n} sentences, {dmg} with lost characters")


LEVELS = {"basic_vocab": "基礎級", "elementary_vocab": "初級", "intermediate_vocab": "中級",
          "upper_intermediate_vocab": "中高級", "advanced_vocab": "高級"}


def _cell(v):
    return "" if v is None or (isinstance(v, float) and v != v) else nfc(str(v))


def load_kaga115(db, folder):
    """115年度 certification vocabulary (.ods, one file per level and accent) and the 基礎級暨初級 question banks."""
    files = sorted(folder.glob("*.ods")) if folder.exists() else []
    if not files:
        print(f"kaga115: {folder} has no .ods files, skipped"); return
    import pandas as pd
    n = nq = 0
    for f in files:
        stem, acc = f.stem.rsplit("_", 1)
        sheets = pd.read_excel(f, engine="odf", sheet_name=None, header=None, dtype=object)
        if stem in LEVELS:
            level = LEVELS[stem]
            for df in sheets.values():
                head = [re.sub("四縣|海陸|大埔|饒平|詔安|腔", "", _cell(c)) for c in df.iloc[0]]
                col = lambda *names: next(i for i, h in enumerate(head) if any(nm in h for nm in names))
                c_id, c_hz, c_py = col("編號", "編碼"), col("客家語", "客語詞彙"), col("標音", "音標")
                c_def = col("華語詞義")
                c_ex = next((i for i, h in enumerate(head) if h in ("例句",)), None)
                c_tr = col("翻譯", "華譯")
                c_note, c_p1, c_p2, c_cat = col("備註"), col("詞性1"), col("詞性2"), col("分類")
                for row in df.iloc[1:].itertuples(index=False):
                    row = [_cell(v) for v in row]
                    if not row[c_hz] or "無此詞條" in row[c_hz]:     # 此腔無此詞條: word absent in this accent
                        continue
                    hz, hz_alts = split_alts(row[c_hz]); p, p_alts = split_alts(row[c_py])
                    if not hz:
                        continue
                    definition, ex = row[c_def], row[c_ex] if c_ex is not None else ""
                    if c_ex is None and "例如：" in definition:          # 中高級 / 高級: definition + 例如：example
                        definition, ex = definition.split("例如：", 1)
                    sixian = acc == "sixian"
                    pos = "、".join(x for x in (row[c_p1], row[c_p2]) if x)
                    eid = db.execute(
                        "INSERT INTO entry(source, src_id, hanzi, accent, pinyin, pkey, toneless, level, category, mandarin, pos) "
                        "VALUES ('kaga115',?,?,?,?,?,?,?,?,?,?)",
                        (f"{level}:{row[c_id]}", hz, acc, p, py.key(p) if sixian else None, py.toneless(p) if sixian else None,
                         level, re.sub(r"^\d+", "", row[c_cat]), nfc(definition.strip("\n ")), pos)).lastrowid
                    n += 1
                    for a in hz_alts:
                        db.execute("INSERT INTO variant VALUES (?,?,?,?,?)", (eid, a, None, None, "hanzi-alt"))
                    for a in p_alts:
                        db.execute("INSERT INTO variant VALUES (?,?,?,?,?)", (eid, None, a, py.key(a) if sixian else None, "reading-alt"))
                    exs = [x.strip() for x in ex.split("\n") if x.strip()]
                    trs = [x.strip() for x in row[c_tr].split("\n") if x.strip()]
                    for i, x in enumerate(exs):
                        db.execute("INSERT INTO example(entry_id, source, accent, hanzi, mandarin) VALUES (?,?,?,?,?)",
                                   (eid, "kaga115", acc, x, trs[i] if i < len(trs) and len(trs) == len(exs) else
                                    ("\n".join(trs) if i == 0 else None)))
        elif stem == "basic_elementary_bank":
            for section, df in sheets.items():
                head = [_cell(c) for c in df.iloc[0]]
                for row in df.iloc[1:].itertuples(index=False):
                    row = [_cell(v) for v in row]
                    if not row[1]:
                        continue
                    opts = [row[i] for i, h in enumerate(head) if h in ("1", "2", "3", "4")]
                    ans = next((row[i] for i, h in enumerate(head) if h == "答案"), "")
                    tr = next((row[i] for i, h in enumerate(head) if h == "華譯"), None)
                    db.execute("INSERT INTO exam_item(accent, section, num, question, options, answer, translation) VALUES (?,?,?,?,?,?,?)",
                               (acc, nfc(section), int(float(row[0])) if row[0] else None, row[1],
                                json.dumps(opts, ensure_ascii=False) if opts else None,
                                int(float(ans)) if re.match(r"^\d+(\.0)?$", ans) else None, tr))
                    nq += 1
    print(f"kaga115: {n} entries (all accents), {nq} exam items")


def enrich(db):
    db.execute("""UPDATE entry SET glossika_freq = (SELECT count(*) FROM glossika_word g WHERE g.hanzi = entry.hanzi)
                  WHERE source IN ('kaga', 'kaga115') AND accent='sixian' OR source='moe'""")
    db.execute("UPDATE entry SET core = 1 WHERE source='kaga115' AND accent='sixian' AND level IN ('基礎級','初級','中級')")
    # MOE definitions for certification words: same characters, same Sixian reading
    db.execute("""UPDATE entry SET pos = (SELECT s.pos FROM entry m JOIN sense s ON s.entry_id = m.id
                  WHERE m.source='moe' AND m.hanzi = entry.hanzi AND m.pkey = entry.pkey ORDER BY s.ord LIMIT 1)
                  WHERE source='kaga' AND accent='sixian'""")


def main(raw, out):
    raw, out = Path(raw), Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    db = sqlite3.connect(out)
    db.executescript((Path(__file__).parent / "schema.sql").read_text())
    db.executemany("INSERT INTO source VALUES (?,?,?,?,?,?,?)", SOURCES)
    load_moe(db, raw)
    load_kaga(db, raw)
    load_kaga115(db, Path(__file__).resolve().parent.parent / "data" / "gov" / "115")
    load_corpus(db, Path(__file__).resolve().parent.parent / "data" / "gov" / "hakka_corpus_176307.csv")
    load_sentences100(db, Path(__file__).resolve().parent.parent / "data" / "gov" / "hakka_100_sentences_162998.csv")
    if os.environ.get("HAKKA_PRIVATE"):
        load_glossika(db, os.environ["HAKKA_PRIVATE"])
    enrich(db)
    db.commit()
    for (k, v) in db.execute("SELECT source || coalesce('/' || accent, ''), count(*) FROM entry GROUP BY 1"):
        print(f"  {k:16} {v}")
    print(f"core (v_core): {db.execute('SELECT count(*) FROM v_core').fetchone()[0]}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
