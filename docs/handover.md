# Handover (updated 2026-11-07, 13:30)

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

## Next, in order
1. **Write lesson 1**, then 2–6, with `make lint` clean; check the Hailu lines word by word. Start from `make coverage`
   (the next words: 𠊎, 个, 佢, 無, 當, 係, 愛…).
2. **Audio** (plan: `docs/audio.md`). The six 115年度 zips are being uploaded as release `audio-115` on Hkka-private;
   then link word and example ids to files and convert for the app. In parallel, test the Taiwanese Hakka TTS engines
   (VoxHakka, the 客委會 API) on official example sentences against their real recordings.
3. **Repair the 客語百句 lost characters** from the romanisation; 44 Sixian rows.
4. **Glossika → MOE pinyin** mapping (its tone marks to be understood first).
5. **Licence of the current MOE 臺灣客語辭典** and its bulk download (headword audio).
6. App: copy Tsheh-tû's `app/` and `tools/build_app.py`, add the accent switch.

## Things to know
- The cloud session cannot create GitHub repos, and cannot reach Taiwanese government sites from the shell (data.gov.tw,
  hakkadict.moe.edu.tw, elearning.hakka.gov.tw). GitHub and the web search/fetch tools work.
- The 102年版 audio URLs (wiki.hakka.gov.tw) date from 2013 and are probably dead; do not plan on them.
- The MOE dictionary's 華語對照表 is not under its CC licence; it is not loaded.
- HAT speech database (60 h Sixian TTS) needs a signed agreement: read it before applying (`docs/sources.md`).
- Hugging Face is reachable from the cloud session (models, spaces); download.pytorch.org and voxhakka.github.io are not.
- The open Hakka TTS/ASR models on Hugging Face (formospeech) are **CC BY-NC 4.0**, not CC BY as first announced.
