# Project notes

## State as of 17 Nov 2026
Update this section at the end of every batch of work (one line "state as of" is enough when little changed): a
session starting from here trusts it.

- **Repos.** `Hkka` (public: course, database build, app), `Hkka-private` (private: Glossika, the owner's books and
  the Books tab of the app, audio tools), `Hkka-audio` (public: recordings and synthetic voice the app copies).
- **Course: complete.** `make lint`: 180 files, 0 errors. `make coverage`: 4,177 words taught; 基礎級 100%,
  初級 99%, 中級 99%, 中高級 18% (高級 5%).
  - Part 1, `course/lessons/001–100.yaml`: Sixian with Hailu written alongside every line. Story: Sam with the 劉
    family in Miaoli, Nov 2026 – Nov 2027.
  - Accent bridge, `course/bridge/`: six pages between lesson 100 and 進修 1 (`tools/bridge.py`).
  - Part 2 進修, `course/perfectionnement/01–70.yaml` (Sixian only), plus 外篇 1–10 (`71–80.yaml`, app ids
    171–180; 外篇 4–10 teach the attested 中高級 and 高級 words, `course/batches/P74.md`). Method and tools: `docs/perfectionnement-plan.md`, `docs/tooling-handover.md`.
  - 1,055 lines carry `check: true`, waiting for a native speaker.
- **Audio.** 客委會 recordings cut per word for all Sixian list words; VoxHakka synthetic voice for every lesson line
  (Part 1 both accents, Part 2 Sixian). `docs/audio.md`, `docs/voice-handover.md`.
- **App.** `make app` → `app/dist/index.html`, `make site` → `_site/`. The Books tab appears only with a token that
  can read Hkka-private (private reader, 跳童 chapter 1).
- **Database.** `make db`: 115年度 lists (core, five accents), 2013 lists, MOE dictionary, 客語百句, the Hakka corpus;
  Glossika frequencies with `HAKKA_PRIVATE`. `docs/handover.md` has the details and the decisions.

## One pipeline for every module (17 Nov 2026, after the cross-app review)
- **`tools/cards.py`**: the lexicon, the word cut and the word card, used by `lint.py`, `build_app.py` and the private
  `build_reader.py`. One cut rule: the cheapest cut into words of the lexicon; in lessons a taught word is cheap
  (lint's old rule), in Hailu lines and in the books every word costs the same (fewest words). A book word the course
  teaches shows "New word in Lesson N" on its card.
- **`course/supplement.yaml`**: words no list has, with reading and English, known to lint (a warning when a lesson
  uses one), the app and the reader. The books keep the same kind of file in Hkka-private (`books/supplement.yaml`).
- **`tools/verify_words.py`** (port of Tsheh-tû's, branch `dict-db`), run by `make lint` and by `build_reader.py`:
  every new word (both accents), the supplement and every book word against the 115年度 lists, then 2013, then MOE,
  sandhi spellings accepted. Prints only the suspects. On 17 Nov: 3 in the course (Hailu 新正年時 L52, 主持人 L80,
  恁早 L23), 8 in the book (囥人尋 read kong where both lists read duˋ; five glossary spellings that differ from the
  course's).
- **`tools/zh_words.py`** + `zhLine()` in the template (port of Tsheh-tû's, branch `dict-pinyin`): every Mandarin text
  (card glosses, MOE definitions, example translations, "Mandarin X" in notes, the books' narration and notes) is cut
  the same way and opens the 華語 · Mandarin sheet. CC-CEDICT comes from `make data` (`data/raw/cedict`); the reader
  no longer needs a `shujia` clone.

## Next
1. A native speaker for the `check: true` lines and the verifier's suspects.
2. Hailu 中高級 and 高級 recordings (`docs/audio.md`); final voice casting.
3. More books in the private reader (`Hkka-private/docs/books.md`).
4. Keep in step with Tsheh-tû, the lead app: its `PORTING.md` lists the fixes to carry over.
