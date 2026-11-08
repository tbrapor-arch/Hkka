# Handover (updated 2026-11-08)

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
- **Catalogue** `docs/sources.yaml` → `docs/sources.md` (`make sources`): 22 resources, each with URL, accents, use,
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
- **Audio: Taiwanese only.** Real 客委會 recordings for words and example sentences; Taiwan-trained TTS (labelled
  synthetic) for lesson lines we write; no Mainland/Meixian or Azure voice (Azure has no Hakka). See `docs/audio.md`.
- **Accent switch: planned.** Every word and sentence carries an `accent`. Words, cards and dictionary can switch to all
  six Taiwanese accents (data present: Hailu 90%, Raoping 92%, Dapu 79%, Zhao'an 60% of the Sixian core words).
  Lesson text cannot be converted: in Glossika 38% of sentences use different words in Sixian and Hailu (吾 vs 𠊎个,
  若 vs 你个). So: lesson lines get one text per accent, Sixian is the reference, Hailu second, others vocabulary-only
  with a "Sixian only" label on lessons. Audio is the limit beyond Sixian/Hailu.

## Course decisions (2026-11-07)
Same shape as Tsheh-tû (100 lessons, review every 7th, second wave from 50, then 進修), **faster, progressive pace (16 → 25 new
words per lesson, `course/pacing.md`)**, **Sam in Miaoli** as backdrop, **Hailu written alongside Sixian**, **no native speaker** (lint against the
official lists, `check: true` on unattested patterns). Details and the vocabulary split: `course/README.md`.

## Ready for writing (2026-11-07)
- `course/lessons/_template.yaml`: lesson format with a Sixian (`sx`) and a Hailu (`hl`) version of every line,
  `groups` for sandhi breaks, `check: true` for lines a native speaker should review, `names:` exempt from checks.
- `course/lessons/000-reading-pinyin.md`: lesson 0 (consonants, -b/-d/-g, six tones and their shift from Mandarin
  measured on 1,404 characters, sandhi, 仔 linking, correspondences, two readings, the Sixian → Hailu tone code).
- `course/syllabus.yaml`: lessons 1–100 with topic, grammar focus and new-word target (1,856 in all); cast and setting.
- `course/grammar-inventory.md`, `course/pacing.md`, `course/README.md`.
- `make lint` (`tools/lint.py`): both accents, syllables and tone marks per accent, word segmentation that prefers
  taught words, new words declared once, used-before-taught, syllabus targets and hard-word caps.
- `make coverage` (`tools/coverage.py`): coverage of 基礎級 / 初級 / 中級, pacing per lesson, next words to teach.
- Database: tone keys for all six accents (Hailu agrees with MOE 96.7%), `entry.cognate` / `entry.hsk`, English glosses
  for 2,119 of the 3,030 core words.

## Lessons written (2026-11-08)
**Part 1 is complete: lessons 1–100**, `make lint` 0 errors, 1,773 words taught (基礎級 78%, 初級 57%, 中級 18%;
`make coverage`). 15 batches, each with a brief in `course/batches/NN.md` (calendar, scenes, threads, load) and a
fresh-agent review against the database; every finding went into `course/batches/checklist.md`, which is the
rulebook for any further writing. 241 lines carry `check: true` for a native speaker.
- Story: Sam (French, as in Tsheh-tû) with the 劉 family in Miaoli, Nov 2026 – Nov 2027, on the real calendar (lunar
  dates computed): the 伯公 opera, Lucie's week, the Lunar New Year and 天穿日, a month in 竹東 among Hailu speakers,
  清明, 桐花, 美濃, Grandpa in hospital, 義民, the speech contest, the harvest, a year after lesson 1 on the same platform
  (97 mirrors 1), then France (99 Sixian/Hailu video call, 100 a letter). The syllabus was rearranged around the
  calendar from lesson 50 on (`course/syllabus.yaml` comments).
- Course-wide decisions taken in the final pass: sentence-final particle written 吔 (Sixian) / 咧 (Hailu) as in the
  115年度 lists, reading leˊ / leˋ (MOE quotations keep 了; lint knows 吔 through `PARTICLES`); Hailu V等 denˊ; Hailu
  講話 gongˊ faˇ; place names read as in the lists; `source:` names the table that holds the sentence (`kaga115`,
  `kaga`, `moe`, `sentence`; MOE examples have no audio; `abridged: true` for shortened quotes).
- **Counting rule** (checklist, top): the database's "Sixian" example pool mixes 14,969 official-list sentences
  with 20,185 accent-unmarked MOE examples; compare accents on the official lists only.
- `course/grammar-inventory.md` §17 now holds the Sixian/Hailu differences with official-list counts.
- Lint accepts 啊 and 吔 as particles and AABB forms of listed words.

## Next, in order
1. **A native speaker** for the 241 `check: true` lines (collect them with a script into one sheet), and for the
   reading of 吔 (leˊ or eˊ: the lists give no romanisation; listen to the 115年度 recordings).
2. **Audio**: link lesson lines marked `source: kaga115` to their recordings; TTS for the rest (`docs/audio.md`).
3. **Gaps**: 106 基礎級 words still untaught (`make coverage`: 十一, 十二, 無愛, 哪久, 頂高, 脣…); fold them into a light
   revision of early lessons or into the 進修 part. Hailu 美濃 reading (no list entry) is open.
4. **App**: copy Tsheh-tû's `app/` and `tools/build_app.py`, add the accent switch.
5. Older items: 客語百句 lost characters, Glossika → MOE pinyin, the MOE dictionary licence.

## Things to know
- The cloud session cannot create GitHub repos, and cannot reach Taiwanese government sites from the shell (data.gov.tw,
  hakkadict.moe.edu.tw, elearning.hakka.gov.tw). GitHub and the web search/fetch tools work.
- The 102年版 audio URLs (wiki.hakka.gov.tw) date from 2013 and are probably dead; do not plan on them.
- The MOE dictionary's 華語對照表 is not under its CC licence; it is not loaded.
- HAT speech database (60 h Sixian TTS) needs a signed agreement: read it before applying (`docs/sources.md`).
- Hugging Face is reachable from the cloud session (models, spaces); download.pytorch.org and voxhakka.github.io are not.
- The open Hakka TTS/ASR models on Hugging Face (formospeech) are **CC BY-NC 4.0**, not CC BY as first announced.
