# Handover (updated 2026-11-07)

Where the Hakka course stands, what was decided, and what to do next. Read with `PROJECT_NOTES.md` and
`docs/sources.md`.

## Repos
| Repo | Visibility | Holds |
|---|---|---|
| [Hkka](https://github.com/tbrapor-arch/Hkka) | public | catalogue of sources, database build, (later) course and app |
| [Hkka-private](https://github.com/tbrapor-arch/Hkka-private) | **private** | copyrighted references and data parsed from them; see its README |

Same split as Tsheh-tû (`tsehtu` / `tsehtu-private`). Keep `Hkka-private` private: it holds the Glossika PDFs.

## Resume in five minutes
```sh
git clone https://github.com/tbrapor-arch/Hkka && git clone https://github.com/tbrapor-arch/Hkka-private
cd Hkka
make test                                  # romanisation parser
HAKKA_PRIVATE=../Hkka-private make db      # → data/build/hakka.db, data/build/sixian_core.csv
make lookup W=今晡日
```
`make db` alone (without `HAKKA_PRIVATE`) builds the open part only; that is what CI and the published app may use.

## Done
- **Catalogue** `docs/sources.yaml` → `docs/sources.md` (`make sources`): 19 resources, each with URL, accents, use,
  licence and status (`in-db`, `to-import`, `reference`, `private`). A copy is in the claude.ai project "Hakka APP".
- **Romanisation** `tools/pinyin.py`: MOE Hakka pinyin, Sixian only. Tone marks (`konˊbangˋua`) and tone values
  (`kon²⁴bang³¹ua⁵⁵`) map to one key `kon24-bang31-ua55`. Unmarked runs are split with the syllable list
  taken from the MOE dictionary (659 Sixian syllables).
- **Database** `tools/build_db.py`, schema `tools/schema.sql`:
  - `moe`: 15,456 readings with all six accents (`reading` table), definitions, examples, synonyms;
  - `kaga115`: **core source**, certification vocabulary 115年度 (2026) in `data/gov/115/`, five accents with parallel
    numbering (`v_word_parallel`); Sixian 7,892 words 基礎級→高級, 7,729 examples; `exam_item`: 5,055 question-bank items;
  - `kaga`: the older 102年版 (2013) lists, kept for English glosses and comparison;
  - `corpus`: 臺灣客語語料庫 (data.gov.tw 176307, committed in `data/gov/`): 755 texts, 206 Sixian; word counts
    `corpus_freq` (169,092 Sixian tokens, longest-match segmentation);
  - `sentence`: 客語百句 (data.gov.tw 162998, in `data/gov/`): 195 sentences × six accents, view
    `v_sentence_parallel`; tone marks normalised; 225 of 1,053 rows lost a character (`hanzi_damaged`);
  - private: 3,000 Glossika sentences + word segmentation (`glossika`, `glossika_word`, `entry.glossika_freq`);
  - `v_core`: 3,030 Sixian words (115年度 基礎級 + 初級 + 中級), by level, then by Glossika and corpus frequency.
- **Checks**: 93% of Sixian certification words shared with the MOE dictionary have the same reading key (the rest are
  real variants or sandhi spellings); 78% of Glossika word tokens link to an entry. A fresh clone builds with
  `make db`.

## Decisions
- Accent: **Sixian 四縣** first. Romanisation: **MOE pinyin**, tone marks in the text, keys with tone values.
- Lessons will be Assimil-style YAML in `course/`, as in Tsheh-tû (dialogue, translation, notes, exercises).
- Course content CC BY-SA 4.0, code MIT, sources downloaded at pinned commits and never committed.
- **Accent switch: planned.** Every word and sentence carries an `accent`. Words, cards and dictionary can switch to all
  six Taiwanese accents (data present: Hailu 90%, Raoping 92%, Dapu 79%, Zhao'an 60% of the Sixian core words).
  Lesson text cannot be converted: in Glossika 38% of sentences use different words in Sixian and Hailu (吾 vs 𠊎个,
  若 vs 你个). So: lesson lines get one text per accent, Sixian is the reference, Hailu second, others vocabulary-only
  with a "Sixian only" label on lessons. Audio is the limit beyond Sixian/Hailu.

## Course decisions (2026-11-07)
Same shape as Tsheh-tû (100 lessons, review every 7th, second wave from 50, then 進修), **faster pace (~20 new words per
lesson)**, **Sam in Miaoli** as backdrop, **Hailu written alongside Sixian**, **no native speaker** (lint against the
official lists, `check: true` on unattested patterns). Details and the vocabulary split: `course/README.md`.

## Next, in order
1. **Audio** for the 115年度 lists: `fetch_gov.ps1 -Audio` (Sixian + Hailu zips, large). Decide where it lives
   (not in git: Git LFS, a release asset, or object storage), then link word ids to files.
2. **Per-accent romanisation**: tone tables for Hailu (7 tones, ˋ53 ∅55 ˊ24 ˇ11 +33, checked ∅5 ˋ2) and the other
   accents in `tools/pinyin.py`; `key()` takes an accent; fill `entry.pkey` for the non-Sixian kaga rows.
3. **Sixian tone sandhi** `tools/sandhi.py` (陰平 24 → 11 before 24, 55 and 陽入 5), tested against the MOE workbook.
4. **Repair the 客語百句 lost characters** from the romanisation (syllable at the '?' → MOE character), reviewed by
   hand; the Sixian set has 44 damaged rows.
5. **Glossika → MOE pinyin** mapping, after checking what its tone marks are (今晡日 is gímbúngi̠t there,
   MOE gimˊbuˊngidˋ). Then Glossika sentences can be searched by key.
6. **Licence of the current MOE 臺灣客語辭典** (hakkadict.moe.edu.tw) and its bulk download: headword audio.
7. Tooling before lesson 1: lesson template with Sixian + Hailu lines, `make lint`, `make coverage`, HSK layer
   (`cognate` class per word), `course/grammar-inventory.md`; then `course/000-reading-pinyin.md`, then
   `course/syllabus.yaml` aimed at the certification levels
   (`docs/sources.md` › kaga-test-specs for the can-do descriptors), then lessons with the `accent` layer.
8. App: copy Tsheh-tû's `app/` and `tools/build_app.py`, add the accent setting.

## Things to know
- The cloud session cannot create GitHub repos, and cannot reach Taiwanese government sites from the shell (data.gov.tw,
  hakkadict.moe.edu.tw, elearning.hakka.gov.tw). GitHub and the web search/fetch tools work.
- The 102年版 audio URLs (wiki.hakka.gov.tw) date from 2013 and are probably dead; do not plan on them.
- The MOE dictionary's 華語對照表 is not under its CC licence; it is not loaded.
- HAT speech database (60 h Sixian TTS) needs a signed agreement: read it before applying (`docs/sources.md`).
