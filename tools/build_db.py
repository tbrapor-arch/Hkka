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


def split_alts(s):
    """'窗框(窗門框、窗斗)' → ('窗框', ['窗門框','窗斗']); 'ngiabˋ lang 【ngiabˋ nang】' → ('ngiabˋ lang', ['ngiabˋ nang'])"""
    s = nfc(s)
    alts = [a for grp in re.findall(r"[(（【\[](.*?)[)）】\]]", s) for a in re.split(r"[、/，,]", grp) if a.strip()]
    main = nfc(re.sub(r"[(（【\[].*?[)）】\]]", "", s))
    main, *slash = [nfc(x) for x in main.split("/")]     # 'gimˊ buˊ ngidˋ/ginˊ buˊ ngidˋ'
    return main, slash + [nfc(a) for a in alts]


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
    for eid, hz in db.execute("SELECT id, hanzi FROM entry WHERE source='kaga' AND accent='sixian' ORDER BY id DESC"):
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
    words = {hz for (hz,) in db.execute("SELECT hanzi FROM entry WHERE (source='moe' AND pkey IS NOT NULL) OR (source='kaga' AND accent='sixian')")}
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


def enrich(db):
    db.execute("""UPDATE entry SET glossika_freq = (SELECT count(*) FROM glossika_word g WHERE g.hanzi = entry.hanzi)
                  WHERE source='kaga' AND accent='sixian' OR source='moe'""")
    db.execute("UPDATE entry SET core = 1 WHERE source='kaga' AND accent='sixian' AND level IN ('初級','中級、中高級')")
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
    load_corpus(db, Path(__file__).resolve().parent.parent / "data" / "gov" / "hakka_corpus_176307.csv")
    if os.environ.get("HAKKA_PRIVATE"):
        load_glossika(db, os.environ["HAKKA_PRIVATE"])
    enrich(db)
    db.commit()
    for (k, v) in db.execute("SELECT source || coalesce('/' || accent, ''), count(*) FROM entry GROUP BY 1"):
        print(f"  {k:16} {v}")
    print(f"core (v_core): {db.execute('SELECT count(*) FROM v_core').fetchone()[0]}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
