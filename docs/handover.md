# Handover (2026-11-04)

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
  - `kaga`: certification vocabulary 102年版 for five accents, Sixian 7,241 words with level, theme, glosses, example;
  - private: 3,000 Glossika sentences + word segmentation (`glossika`, `glossika_word`, `entry.glossika_freq`);
  - `v_core`: 6,637 Sixian certification words, basic level first, then by Glossika frequency.
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

## Next, in order
1. **Open data from data.gov.tw** (by hand; the cloud machine cannot reach it): datasets
   [176002](https://data.gov.tw/dataset/176002) (certification vocabulary + audio, current years, adds 基礎級 and
   南四縣), [176307](https://data.gov.tw/dataset/176307) (Hakka corpus), 客語百句. Put the files in
   `reference/gov/`, then write the importers from the real files and make the current list the core source.
2. **Per-accent romanisation**: tone tables for Hailu (7 tones, ˋ53 ∅55 ˊ24 ˇ11 +33, checked ∅5 ˋ2) and the other
   accents in `tools/pinyin.py`; `key()` takes an accent; fill `entry.pkey` for the non-Sixian kaga rows.
3. **Sixian tone sandhi** `tools/sandhi.py` (陰平 24 → 11 before 24, 55 and 陽入 5), tested against the MOE workbook.
4. **Glossika → MOE pinyin** mapping, after checking what its tone marks are (今晡日 is gímbúngi̠t there,
   MOE gimˊbuˊngidˋ). Then Glossika sentences can be searched by key.
5. **Licence of the current MOE 臺灣客語辭典** (hakkadict.moe.edu.tw) and its bulk download: headword audio.
6. `course/000-reading-pinyin.md`, then `course/syllabus.yaml` aimed at the certification levels
   (`docs/sources.md` › kaga-test-specs for the can-do descriptors), then lessons with the `accent` layer.
7. App: copy Tsheh-tû's `app/` and `tools/build_app.py`, add the accent setting.

## Things to know
- The cloud session cannot create GitHub repos, and cannot reach Taiwanese government sites from the shell (data.gov.tw,
  hakkadict.moe.edu.tw, elearning.hakka.gov.tw). GitHub and the web search/fetch tools work.
- The 102年版 audio URLs (wiki.hakka.gov.tw) date from 2013 and are probably dead; do not plan on them.
- The MOE dictionary's 華語對照表 is not under its CC licence; it is not loaded.
- HAT speech database (60 h Sixian TTS) needs a signed agreement: read it before applying (`docs/sources.md`).
