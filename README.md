# Hkka

A Hakka course in English for people who already speak Mandarin, with an open vocabulary database behind it.
Accent: **Sixian 四縣腔** (Taiwan). Romanisation: **MOE Hakka pinyin** (臺灣客家語拼音方案). Sister project of
[Tsheh-tû 冊櫥](https://github.com/tbrapor-arch/tsehtu) (Taigi), with the same layout and the same public/private split.

## Layout
```
course/        lesson 0, syllabus, pacing, grammar inventory, lesson template — CC BY-SA 4.0
docs/          sources.yaml / sources.md: catalogue of documentation and data, with licences
tools/         database build + lookup scripts — MIT
data/fetch.sh  downloads open data sources at pinned commits (nothing committed)
data/build/    generated: hakka.db, sixian_core.csv (git-ignored)
reference/     your local, git-ignored reference material
```

## Build the database
Needs Python 3.9+, git, and `pip install -r requirements.txt` (PyYAML, pandas, odfpy).
```sh
make db                   # → data/build/hakka.db, data/build/sixian_core.csv
make lookup W=今晡日       # Hakka characters, or a Mandarin gloss (今天)
make lookup W=gimˊbuˊngidˋ # MOE pinyin, tone marks or numbers (gim24bu24ngid2); no tone = any tone
make test                 # romanisation and sandhi tests
make lint                 # check the lessons (both accents)
make coverage             # what the lessons cover, what to teach next
make sources              # docs/sources.yaml → docs/sources.md
sh data/fetch_gov.sh      # on your own machine: 115年度 certification tables into reference/gov/115/
# Windows: powershell -ExecutionPolicy Bypass -File data\fetch_gov.ps1   (→ hakka-gov-115.zip)
HAKKA_PRIVATE=../Hkka-private make db   # also load the private Glossika sentences (local only)
```

## The app
`make app` builds the reader app into one file, `app/dist/index.html` (open it in a browser, no server needed);
`make site` adds the manifest, icons and offline service worker in `_site/`. On every push to `main`, the workflow
`.github/workflows/pages.yml` builds it from the open sources and publishes it on GitHub Pages
(https://tbrapor-arch.github.io/Hkka/), where it can be installed on a phone's home screen.
Lessons (Part 1 in Sixian and Hailu, 進修 in Sixian), tap-a-word cards from the lists and the MOE dictionary,
notes, exercises, a Leitner word-card practice, progress saved in the browser. Audio is not in the public build yet:
the 客委會 clips and the synthetic lesson voice live in Hkka-private (`tools/build_app.py` picks them up from
`app/dist/audio/` when present).

## What the database gives you
- 15,456 MOE dictionary readings with all six Taiwanese accents, definitions, part of speech, example sentences
- the 2026 (115年度) certification vocabulary: 7,892 Sixian words from 基礎級 to 高級 with Mandarin meaning, part of
  speech, theme and 7,729 example sentences; the same lists, numbered in parallel, for 海陸, 大埔, 饒平 and 詔安
- 5,055 exam-style items from the official question banks (listening, reading, speaking, repeat-after)
- the older 2013 lists (with English glosses)
- the Hakka Council corpus (755 texts, 206 in Sixian) with word frequencies
- 客語百句: 195 everyday sentences side by side in all six accents (`v_sentence_parallel`), with audio links
- one tone-value key for both spellings (`konˊbangˋua` = `kon24-bang31-ua55`), so sources can be joined
- `v_core`: 3,030 Sixian words (基礎級 + 初級 + 中級), by level and frequency

Start with `docs/handover.md`. See `tools/schema.sql` for tables, `ATTRIBUTION.md` for sources and licences, `docs/sources.md` for everything else
that exists (textbooks, the romanisation manual, the speech database, newer open data still to import).

## Licences
Code: MIT (`LICENSE`). Course content: CC BY-SA 4.0 (`LICENSE-CONTENT.md`). Data sources keep their own licences
(`ATTRIBUTION.md`); they are downloaded, not redistributed.
