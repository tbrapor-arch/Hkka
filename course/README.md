# Course content

Audience: English-speaking learners who already read Traditional Chinese and speak Mandarin at around B2 / HSK 5,
exactly as in [Tsheh-tû](https://github.com/tbrapor-arch/tsehtu). The course leans on that: words with the same
characters as Mandarin are learned as pronunciation, and teaching time goes to false friends, Hakka-only words, tone
sandhi and grammar words.

How the core vocabulary splits for this learner (3,030 words, 115年度 基礎級 + 初級 + 中級, Sixian; measured
2026-11-07 against the HSK word list and the official Mandarin glosses; `entry.cognate` in the database):
- **1,482 same as Mandarin** (你, 去, 看, 做…): only the reading is new.
- **484 Hakka-only** (𠊎, 佢, 个, 毋, 吂, 恁, 屋下, 食…): most grammar words are here; these get the notes.
- **295 same characters, different use**, possible false friends (無 = 嗎 / 沒有, 當 = 很, 係 = 是, 愛 = 要, 該 = 那, 好 = 喜歡).
- **769 partial** (做得 = 可以, 今晡日 = 今天, 睡目 = 睡覺…).
In the 100 most frequent words, 60 are not plain Mandarin. That is where the time goes.

## Shape (same as Tsheh-tû)
- Part 1: **100 lessons**, every 7th a review (7, 14, … 98) with no new material. Each lesson: a dialogue with a topic
  title, notes, two short exercises (translate, fill the gap).
- First wave: all 100 lessons, each new. Second wave: from lesson 50, finishing lesson N brings back lesson N−49,
  read in English first and said in Hakka.
- Dialogue length as in Tsheh-tû: 8–10 lines at the start, 15 by lesson 51, 18–20 at the end; reviews about 10.
- Between the two parts: **the accent bridge**, six pages from Sixian to Hailu, South Sixian, Dapu, Raoping and
  Zhao'an (`course/bridge/`, written by `tools/bridge.py` from the lists; remarks in `course/bridge/notes.yaml`).
- Part 2: **進修** (perfectionnement), 70 longer texts in varied genres (dialogue, tale, letter, essay, interview,
  play), every 7th a review.

## Decisions (2026-11-07)
- **Pace: faster than Tsheh-tû, and progressive like it.** From 16 new words per lesson (lessons 1–6) to 25
  (lessons 78–100), about 1,860 in part 1: all of 基礎級 + 初級 (1,330) and about 500 words of 中級. The number of
  Hakka-only words and false friends per lesson is capped (6 → 10). See `pacing.md`. 進修 covers the rest of 中級 and
  the start of 中高級 (about 40 new words per text).
- **Story backdrop: Sam in Miaoli.** The same Sam as in Tsheh-tû, now staying with a Hakka family in 苗栗 (Sixian
  heartland). The characters stay a backdrop; vocabulary and structures come first.
- **Hailu alongside.** Every dialogue line is written in Sixian and in Hailu (海陸) at once, for the accent switch.
  Sixian is the reference; the Hailu line uses Hailu words, not a transliteration (see the 38% of Glossika sentences
  that change words between the two). Notes on Hailu differences where they teach something.
- **No native speaker for now.** Every word must exist in the official lists or the MOE dictionary for that accent
  (checked by lint); sentence patterns follow the official example sentences (7,729 in Sixian); any line built on a
  pattern not attested there is marked `check: true` for a later native review. Audio: official word and sentence
  recordings where they exist; dialogue audio is an open question.

## Rules for content (as in Tsheh-tû)
1. Everything here is original. No sentences, dialogues, storylines or notes from published courses (Glossika
   included: it may be used to choose words and check naturalness, never copied).
2. Romanisation: MOE Hakka pinyin. Characters: MOE recommended characters.
3. Every word in a dialogue must be found in `data/build/hakka.db` for that accent.
4. A sentence copied from the MOE dictionary or the official lists is marked `source: moe` / `source: kaga115` and is
   not edited.
