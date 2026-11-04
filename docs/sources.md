# Sources and documentation

Generated from `docs/sources.yaml` by `tools/sources_md.py`; edit the YAML, not this file.

Licences were checked on 2026-11-04. Check again before importing anything new.

## In the database (`make db`)

| Resource | Accents | Use | Licence |
|---|---|---|---|
| [教育部臺灣客家語常用詞辭典 (g0v JSON)](https://github.com/g0v/moedict-data-hakka) — 教育部; data by g0v/moedict-data-hakka (Audrey Tang, Pierre Magistry) | sixian, hailu, dapu, raoping, zhaoan, south-sixian | dictionary, sentences | CC BY-ND 3.0 TW (dictionary text); conversion CC0; 華語對照表 not under the licence |
| [客語能力認證基本詞彙 102年版 (certification vocabulary, 2013 edition)](https://github.com/Taiwanese-Corpus/hakka_elearning) — 客家委員會 Hakka Affairs Council; merged by Taiwanese-Corpus/hakka_elearning | sixian, hailu, dapu, raoping, zhaoan | vocab, sentences, audio | government work; the same lists are now open data (政府資料開放授權條款-第1版) |

**教育部臺灣客家語常用詞辭典 (g0v JSON)** (`moe-dict-2023`, JSON, 14,712 headwords / 15,456 readings). Six-accent readings, definitions, part of speech, example sentences with Mandarin, synonyms/antonyms.

**客語能力認證基本詞彙 102年版 (certification vocabulary, 2013 edition)** (`kaga-vocab-102`, CSV, Sixian 1,678 初級 + 4,959 中級/中高級 + 604 loanwords). Level, theme (類別), Mandarin and English gloss, one example sentence per word with Mandarin. The audio URLs (wiki.hakka.gov.tw) are from 2013 and probably dead. This is the course's core list (v_core).

## Open licence, importer still to write

| Resource | Accents | Use | Licence |
|---|---|---|---|
| [客家委員會各年度認證教材詞彙及音檔 (certification vocabulary and audio, by year)](https://data.gov.tw/dataset/176002) — 客家委員會 | sixian, hailu, dapu, raoping, zhaoan, south-sixian | vocab, sentences, audio | 政府資料開放授權條款-第1版 (Open Government Data License v1, compatible with CC BY 4.0) |
| [臺灣客語語料庫：客委會出版品或採錄品 (Taiwan Hakka Corpus)](https://data.gov.tw/dataset/176307) — 客家委員會 | sixian, hailu, dapu, raoping, zhaoan | corpus, sentences | 政府資料開放授權條款-第1版 |
| [客家委員會客語百句](https://data.gov.tw/) — 客家委員會 | sixian, hailu, dapu, raoping, zhaoan | sentences, audio | 政府資料開放授權條款-第1版 |

**客家委員會各年度認證教材詞彙及音檔 (certification vocabulary and audio, by year)** (`kaga-vocab-current`, data.gov.tw dataset of links (CSV/JSON/XML list → files per year)). Newer than kaga-vocab-102, with audio, and redistributable with attribution. data.gov.tw is not reachable from the cloud build machine: download the list on your own machine into reference/gov/ and the importer will be written from the real files. Also: 基礎級 level (new since 2023) and 南四縣.

**臺灣客語語料庫：客委會出版品或採錄品 (Taiwan Hakka Corpus)** (`hakka-corpus`, CSV/JSON/XML — title, relation, mode (written/spoken), accent, date, full text). Written and spoken texts tagged by accent. For word frequency (the equivalent of Tsheh-tû's 2009 corpus) and graded reading texts. Same download note as kaga-vocab-current.

**客家委員會客語百句** (`hakka-100-sentences`, data.gov.tw dataset). 100 everyday sentences. Search "客語百句" on data.gov.tw. Good for lesson 1-10 dialogues.

## Reference only (read, cite, do not copy)

| Resource | Accents | Use | Licence |
|---|---|---|---|
| [客家語拼音方案使用手冊 (Hakka romanisation, user manual, 2012 revision)](https://hakkadict.moe.edu.tw/static/resource/客語資源下載/其他資源/hakka_pinyin3.pdf) — 教育部 Ministry of Education | sixian, hailu, dapu, raoping, zhaoan, south-sixian | spec | government publication, no open licence stated |
| [客家語拼音學習手冊（四縣腔）](https://language.moe.gov.tw/files/people_files/%E5%AE%A2%E5%AE%B6%E8%AA%9E%E6%8B%BC%E9%9F%B3%E5%AD%B8%E7%BF%92%E6%89%8B%E5%86%8A_%E5%9B%9B%E7%B8%A3%E8%85%94.pdf) — 教育部 | sixian | pronunciation, textbook | government publication, no open licence stated |
| [教育部《臺灣客語辭典》(current site)](https://hakkadict.moe.edu.tw/) — 教育部 | sixian, hailu, dapu, raoping, zhaoan, south-sixian | dictionary, audio | not confirmed (the MOE Mandarin dictionaries are CC BY-ND 3.0 TW) |
| [臺灣客家語書寫推薦用字 (recommended characters, batches 1-2)](https://language.moe.gov.tw/) — 教育部 | all | spec | government publication |
| [客語能力認證簡章 + 分級制度及能力指標 (certification handbook and level descriptors)](https://www.dtjh.ptc.edu.tw/uploads/1645754974576CCMtR8v2.pdf) — 客家委員會 / 國立臺灣師範大學 總試務中心 | all | test, spec | government publication |
| [中級暨中高級 樣卷 A/B 卷 and 線上試考 (sample papers, online mock test)](https://hakkaexam.hakka.gov.tw) — 客家委員會 | sixian, hailu, dapu, raoping, zhaoan | test | government publication |
| [哈客網路學院 (Hakka e-learning college)](https://elearning.hakka.gov.tw/) — 客家委員會 | all | textbook, audio, test | all rights reserved (site) |
| [部編版 客語分級教材 (graded school textbooks, levels 1-9 + senior high)](https://cirn.moe.edu.tw/WebContent/index.aspx?sid=1107&mid=14481) — 教育部 / 國立臺南大學 本土語文教育資源中心 | sixian, hailu, dapu, raoping, zhaoan, south-sixian | textbook | 著作權所有，僅供教育使用 (all rights reserved, educational use) |
| [客家語拼音學習網](https://happyhakka.moe.edu.tw/) — 教育部 | all | pronunciation, audio | site, no open licence stated |
| [臺灣客語語音資料庫 HAT (Hakka Across Taiwan)](https://www.aclclp.org.tw/doc/hat_brief_c.pdf) — 客家委員會, distributed by ACLCLP 中華民國計算語言學學會 | sixian, south-sixian, hailu | audio, corpus | non-exclusive licence by signed agreement (individual or organisation form) |
| [國立教育廣播電臺 Channel+ 本土語言學習專區](https://channelplus.ner.gov.tw/channel-language/85) — 國立教育廣播電臺 | sixian, hailu | audio | all rights reserved |
| [客家電視台 Hakka TV](https://en.wikipedia.org/wiki/Hakka_TV) — 公共電視 / 客家電視台 | sixian, hailu | audio | all rights reserved |
| [萌典 客語 (moedict.tw)](https://www.moedict.tw/:) — g0v | sixian, hailu, dapu, raoping, zhaoan, south-sixian | dictionary | same data as moe-dict-2023 |

**客家語拼音方案使用手冊 (Hakka romanisation, user manual, 2012 revision)** (`moe-pinyin-manual`, PDF, 155 pp.). The romanisation spec for the course. Initials, finals, tone marks per accent, and the full Sixian syllable table (672 syllables). Sixian tones ˊ24 ˇ11 ˋ31 ∅55, checked ˋ2 ∅5. tools/pinyin.py implements it.

**客家語拼音學習手冊（四縣腔）** (`moe-pinyin-workbook-sixian`, PDF). Zero-start pronunciation course, initial+final by lesson, ends with tone sandhi. Example sentences are written with sandhi tones (麻油炒豬肝 zuˊ → zuˇ). Model for the course's reading lesson 000. Same series exists for the other five accents (南四縣腔, 海陸腔 … same URL pattern).

**教育部《臺灣客語辭典》(current site)** (`moe-dict-new`, website, 22,000+ entries with audio). Successor of moe-dict-2023, larger. Check its 授權 page and 客語資源下載 section for a bulk download before scraping anything. Headword audio would be the course's word audio, as in Tsheh-tû.

**臺灣客家語書寫推薦用字 (recommended characters, batches 1-2)** (`moe-recommended-chars`, PDF). Which characters to write (𠊎, 佢, 毋, 吂, 恁…). Old URL edu.tw/files/download/MANDR/hakka-words.pdf is dead; find it on 語文成果網.

**客語能力認證簡章 + 分級制度及能力指標 (certification handbook and level descriptors)** (`kaga-test-specs`, PDF). Levels 基礎級 / 初級 / 中級 / 中高級 / 高級 with can-do descriptors (1-L-1 … 3-L-2). Use them to set what each course part reaches, the way Tsheh-tû maps to its exam. Registration and sample papers: https://hakkaexam.hakka.gov.tw

**中級暨中高級 樣卷 A/B 卷 and 線上試考 (sample papers, online mock test)** (`kaga-sample-papers`, PDF + web). Exercise formats (listening, repeat-after, picture description, reading, writing).

**哈客網路學院 (Hakka e-learning college)** (`hakka-elearning`, website, video courses, 認證 vocabulary by theme with audio). Course 認證考題分析 a000000551; 認證詞彙 by theme. Watch and learn from; do not copy.

**部編版 客語分級教材 (graded school textbooks, levels 1-9 + senior high)** (`moe-graded-textbooks`, PDF e-books). Theme order and grammar progression for children/teens. Senior high: sid=1195&mid=14533. Also on https://market.cloud.edu.tw (教育雲). Copies go in hakka-private/reference/, never here.

**客家語拼音學習網** (`happyhakka`, website). Syllable-by-syllable audio; the companion of moe-pinyin-workbook-sixian.

**臺灣客語語音資料庫 HAT (Hakka Across Taiwan)** (`hat-speech-db`, on application — Sixian ASR 396 h, Sixian TTS 60 h, broadcast 280 h, Hakka–Mandarin lexicon 50,000 words). The 60 h Sixian TTS set could voice every sentence the course writes. Read the agreement before applying: agreement forms hat_agr_per_c.pdf (personal) / hat_agr_inst_c.pdf at aclclp.org.tw/doc/.

**國立教育廣播電臺 Channel+ 本土語言學習專區** (`channel-plus`, radio programmes, podcasts). Natural listening material, like the Tsheh-tû podcast tab (link out, do not re-host).

**客家電視台 Hakka TV** (`hakka-tv`, video (YouTube channel)). Dramas and news in Sixian with subtitles; candidate for a transcription tab like 市井豪門 in Tsheh-tû. Official site/channel not yet checked (link is Wikipedia).

**萌典 客語 (moedict.tw)** (`moedict-ui`, website / app). Quick lookups while writing lessons.

## Private (hakka-private only)

| Resource | Accents | Use | Licence |
|---|---|---|---|
| [Glossika Mass Sentences — Hakka Sixian/Hailu, Fluency 1-3](https://ai.glossika.com/) — Glossika (Michael Campbell; credited Can Qi, Shau Zu Ciin Min) | sixian, hailu | sentences | all rights reserved |

**Glossika Mass Sentences — Hakka Sixian/Hailu, Fluency 1-3** (`glossika-sx-hl`, 3 PDFs, 3,000 sentences (EN, 四縣 characters + Glossika romanisation + IPA, 海陸 the same), 1,521-character index). Parsed into hakka-private/data/glossika/sentences.jsonl (tools/parse_glossika.py). Glossika's romanisation is its own "Universal Pinyin", with surface (sandhi) tones and -p/-t/-k, not MOE pinyin. Use it to see which words everyday sentences need (glossika_freq in the database) and to check that lesson sentences sound natural; write the course's own sentences. Book 1 is mostly A1-A2, book 3 B1.
