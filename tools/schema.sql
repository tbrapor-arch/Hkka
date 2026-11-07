-- hakka.db — built locally by `make db`; never committed.
-- Romanisation is always the MOE system (臺灣客家語拼音方案). `pkey` is the tone-value key from tools/pinyin.py:
-- 'kon24-bang31-ua55'. Accents: 四縣 sixian, 海陸 hailu, 大埔 dapu, 饒平 raoping, 詔安 zhaoan, 南四縣 south-sixian.

CREATE TABLE source(id TEXT PRIMARY KEY, name TEXT, year TEXT, license TEXT, commercial_ok INT, redistribute TEXT, note TEXT);

-- One row per headword per source (per accent for the certification lists).
CREATE TABLE entry(
  id INTEGER PRIMARY KEY,
  source TEXT REFERENCES source(id),
  src_id TEXT,
  hanzi TEXT,            -- as written by the source (MOE recommended characters)
  accent TEXT,           -- sixian | hailu | ... ; NULL for multi-accent MOE entries (see reading)
  pinyin TEXT,           -- Sixian reading in tone-mark spelling (konˊbangˋua)
  pkey TEXT,             -- Sixian tone-value key
  toneless TEXT,
  level TEXT,            -- certification level. kaga115: 基礎級 初級 中級 中高級 高級; kaga (2013): 初級 | 中級、中高級 | 外來語
  category TEXT,         -- certification theme (人體, 飲食 …) where known
  mandarin TEXT,         -- Mandarin gloss
  english TEXT,
  audio_url TEXT,        -- original government URL (not fetched)
  pos TEXT,
  -- learner layers (enrich step in build_db.py)
  cognate TEXT,          -- for a Mandarin speaker: same | false-friend | partial | hakka-only (enrich step)
  hsk TEXT,              -- HSK level of the same word in Mandarin (new-1 … new-7), if any
  corpus_freq INT,       -- occurrences in the Sixian texts of the Hakka Council corpus (longest-match segmentation)
  glossika_freq INT,     -- occurrences as a word in the Glossika Sixian sentences (private module only)
  core INT               -- 1 if in the core learner list (v_core)
);
CREATE INDEX entry_pkey ON entry(pkey);
CREATE INDEX entry_hanzi ON entry(hanzi);
CREATE INDEX entry_toneless ON entry(toneless);

CREATE TABLE reading(entry_id INT, accent TEXT, pinyin TEXT, pkey TEXT);   -- MOE: one row per accent
CREATE INDEX reading_entry ON reading(entry_id);
CREATE INDEX reading_pkey ON reading(pkey);

CREATE TABLE sense(id INTEGER PRIMARY KEY, entry_id INT, ord INT, pos TEXT, definition_zh TEXT);
CREATE INDEX sense_entry ON sense(entry_id);

CREATE TABLE example(id INTEGER PRIMARY KEY, entry_id INT, sense_id INT, source TEXT, accent TEXT,
  hanzi TEXT, pinyin TEXT, mandarin TEXT, english TEXT, audio_url TEXT);
CREATE INDEX example_entry ON example(entry_id);

CREATE TABLE variant(entry_id INT, hanzi TEXT, pinyin TEXT, pkey TEXT, kind TEXT);   -- kind: hanzi-alt | reading-alt
CREATE TABLE relation(entry_id INT, other TEXT, rel TEXT);                           -- rel: synonym | antonym
-- 臺灣客語語料庫 (data.gov.tw 176307), committed as data/gov/hakka_corpus_176307.csv under the OGDL v1.
CREATE TABLE corpus(id INTEGER PRIMARY KEY, title TEXT, relation TEXT, mode TEXT, accents TEXT, year INT, content TEXT);
CREATE TABLE corpus_freq(hanzi TEXT PRIMARY KEY, count INT, docs INT);   -- Sixian texts only

-- 客語百句 (data.gov.tw 162998, file DTST20230600025), committed as data/gov/hakka_100_sentences_162998.csv.
-- Same sentence in six accents: join on (set_year, num). hanzi_damaged = 1 when the source lost characters ('?', PUA).
CREATE TABLE sentence(id INTEGER PRIMARY KEY, set_year INT, num INT, accent TEXT, hanzi TEXT, hanzi_damaged INT,
  mandarin TEXT, pinyin TEXT, pinyin_raw TEXT, pkey TEXT, audio_url TEXT);
CREATE INDEX sentence_set ON sentence(set_year, num);
CREATE VIEW v_sentence_parallel AS
  SELECT set_year, num, max(mandarin) AS mandarin,
    max(CASE accent WHEN 'sixian' THEN hanzi || ' | ' || pinyin END) AS sixian,
    max(CASE accent WHEN 'hailu' THEN hanzi || ' | ' || pinyin END) AS hailu,
    max(CASE accent WHEN 'dapu' THEN hanzi || ' | ' || pinyin END) AS dapu,
    max(CASE accent WHEN 'raoping' THEN hanzi || ' | ' || pinyin END) AS raoping,
    max(CASE accent WHEN 'zhaoan' THEN hanzi || ' | ' || pinyin END) AS zhaoan,
    max(CASE accent WHEN 'south-sixian' THEN hanzi || ' | ' || pinyin END) AS south_sixian
  FROM sentence GROUP BY set_year, num;

-- 115年度 certification question banks (基礎級暨初級), data/gov/115/basic_elementary_bank_*.ods
CREATE TABLE exam_item(id INTEGER PRIMARY KEY, accent TEXT, section TEXT, num INT, question TEXT,
  options TEXT, answer INT, translation TEXT);   -- options: JSON list; answer: 1-based index

CREATE TABLE syllable(syl TEXT PRIMARY KEY, n INT);                                  -- Sixian toneless syllables seen in MOE

-- Private module (only when HAKKA_PRIVATE points at a checkout of Hkka-private). Never published.
CREATE TABLE glossika(id INTEGER PRIMARY KEY, book INT, en TEXT,
  sx_hanzi TEXT, sx_rom TEXT, sx_ipa TEXT, hl_hanzi TEXT, hl_rom TEXT, hl_ipa TEXT, aligned INT);
CREATE TABLE glossika_word(sentence_id INT, pos INT, hanzi TEXT, rom TEXT, entry_id INT);
CREATE INDEX gw_hanzi ON glossika_word(hanzi);

CREATE VIEW v_sixian AS
  SELECT e.*, (SELECT group_concat(definition_zh, '；') FROM sense s WHERE s.entry_id = e.id) AS def_zh
  FROM entry e WHERE e.accent = 'sixian' OR (e.source = 'moe' AND e.pkey IS NOT NULL);

-- Core list: the 115年度 Sixian certification words of 基礎級, 初級 and 中級, by level, then by frequency
-- (Glossika when the private module is loaded, weighted ×10, plus the Hakka corpus).
CREATE VIEW v_core AS
  SELECT id, src_id, hanzi, pinyin, pkey, level, category, pos, mandarin, corpus_freq, glossika_freq
  FROM entry WHERE source = 'kaga115' AND accent = 'sixian' AND core = 1
  ORDER BY CASE level WHEN '基礎級' THEN 1 WHEN '初級' THEN 2 WHEN '中級' THEN 3 WHEN '中高級' THEN 4 ELSE 5 END,
           coalesce(glossika_freq, 0) * 10 + coalesce(corpus_freq, 0) DESC, id;

-- The same certification word in every accent (same level and number in all five lists).
CREATE VIEW v_word_parallel AS
  SELECT src_id, level, max(mandarin) AS mandarin,
    max(CASE accent WHEN 'sixian' THEN hanzi || ' ' || pinyin END) AS sixian,
    max(CASE accent WHEN 'hailu' THEN hanzi || ' ' || pinyin END) AS hailu,
    max(CASE accent WHEN 'dapu' THEN hanzi || ' ' || pinyin END) AS dapu,
    max(CASE accent WHEN 'raoping' THEN hanzi || ' ' || pinyin END) AS raoping,
    max(CASE accent WHEN 'zhaoan' THEN hanzi || ' ' || pinyin END) AS zhaoan
  FROM entry WHERE source = 'kaga115' GROUP BY src_id;
