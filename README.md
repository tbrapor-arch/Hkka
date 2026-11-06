# Hkka

A Hakka course in English for people who already speak Mandarin, with an open vocabulary database behind it.
Accent: **Sixian 四縣腔** (Taiwan). Romanisation: **MOE Hakka pinyin** (臺灣客家語拼音方案). Sister project of
[Tsheh-tû 冊櫥](https://github.com/tbrapor-arch/tsehtu) (Taigi), with the same layout and the same public/private split.

## Layout
```
course/        lessons, syllabus (YAML), original content — CC BY-SA 4.0 (not started)
docs/          sources.yaml / sources.md: catalogue of documentation and data, with licences
tools/         database build + lookup scripts — MIT
data/fetch.sh  downloads open data sources at pinned commits (nothing committed)
data/build/    generated: hakka.db, sixian_core.csv (git-ignored)
reference/     your local, git-ignored reference material
```

## Build the database
Needs Python 3.9+, PyYAML and git.
```sh
make db                   # → data/build/hakka.db, data/build/sixian_core.csv
make lookup W=今晡日       # Hakka characters, or a Mandarin gloss (今天)
make lookup W=gimˊbuˊngidˋ # MOE pinyin, tone marks or numbers (gim24bu24ngid2); no tone = any tone
make test                 # romanisation parser tests
make sources              # docs/sources.yaml → docs/sources.md
sh data/fetch_gov.sh      # on your own machine: 115年度 certification tables into reference/gov/115/
# Windows: powershell -ExecutionPolicy Bypass -File data\fetch_gov.ps1   (→ hakka-gov-115.zip)
HAKKA_PRIVATE=../Hkka-private make db   # also load the private Glossika sentences (local only)
```

## What the database gives you
- 15,456 MOE dictionary readings with all six Taiwanese accents, definitions, part of speech, example sentences
- 7,241 Sixian certification words (1,678 初級, 4,959 中級/中高級, 604 loanwords) with level, theme,
  English and Mandarin glosses and an example sentence each; the same lists for 海陸, 大埔, 饒平 and 詔安
- the Hakka Council corpus (755 texts, 206 in Sixian) with word frequencies
- one tone-value key for both spellings (`konˊbangˋua` = `kon24-bang31-ua55`), so sources can be joined
- `v_core`: the 6,637 certification words, basic level first; with the private module, ranked by how often they
  occur in 3,000 everyday sentences

Start with `docs/handover.md`. See `tools/schema.sql` for tables, `ATTRIBUTION.md` for sources and licences, `docs/sources.md` for everything else
that exists (textbooks, the romanisation manual, the speech database, newer open data still to import).

## Licences
Code: MIT (`LICENSE`). Course content: CC BY-SA 4.0 (`LICENSE-CONTENT.md`). Data sources keep their own licences
(`ATTRIBUTION.md`); they are downloaded, not redistributed.
