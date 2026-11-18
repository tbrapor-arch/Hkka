# Extra stories (外篇) after 進修 70: plan

Started 11 Nov 2026 (外篇 1–2, app ids 171–172, see `course/batches/P64.md`). This page, 18 Nov 2026, records how the
words for the next extra stories are chosen, and the plan.

## Why raw corpus frequency was dropped
The packets ranked the 中高級 words by `glossika_freq × 10 + corpus_freq`. For the words still untaught this ranking
is unreliable:
- The Hakka Council corpus (`corpus` table) holds only 206 Sixian texts, about 165k tokens after the longest-match
  segmentation of `tools/build_db.py`, and 68% of the tokens are single characters.
- 82 of the 206 texts are certification exam papers (28% of the tokens). They repeat the same passages across papers
  (A–E sets, question and answer sheets), and they supply 41% (中高級) to 48% (高級) of all the hits of the untaught
  advanced words. A word met five times in one exam passage is not a frequent word.
- Glossika reaches only 16 untaught 中高級 and 11 untaught 高級 words.
- Doubled words and short phrases (當當, 在中央, 日日, 平平, 早早) can be segmentation artefacts: their hits may be
  two other words side by side.

## The rule
`python3 -I tools/attested.py` → `course/packets/attested.tsv`. A word is **attested** when it is
- an untaught kaga115 Sixian entry of level 中高級 or 高級 (taught = (hanzi, pinyin key) in any `new_words`, as in
  `tools/coverage.py`; patterns with … left out);
- written with 2+ characters;
- R ≥ 2, where R = the number of distinct **non-exam** corpus works it appears in (all the "Frog, where are you?"
  retellings count as one work; exam papers are left out) + 1 if Glossika has it.

Columns: hanzi, pinyin, level, category, mandarin gloss, R, works, glossika (0/1), example (1 = an official kaga115
example sentence), flags. Flags: `SEG?` possible segmentation artefact, `SEG` artefact confirmed by reading the
contexts (`--ctx WORD`; the verdicts are in the tool, `REVIEWED`), `POLY` the characters have another reading, `VAR`
the list gives a variant spelling. Without the private module the tool still runs (glossika = 0) and says so.

Single characters with R ≥ 2 go to `course/packets/attested-single.tsv`: their hits mix senses, check each by hand.

## Counts (18 Nov 2026, after 外篇 2)
| | words | Glossika | official example | POLY | VAR | SEG | SEG? |
|---|---|---|---|---|---|---|---|
| 中高級 | 129 | 8 | 128 | 26 | 21 | 2 | 1 |
| 高級 | 99 | 4 | 79 | 34 | 7 | 6 | 0 |

228 words (229 list entries: 平平 is listed at both levels, kept under 中高級). 42 single characters in
`attested-single.tsv`. Without the private module: 124 中高級, 99 高級. The 46 words the heuristics flagged were all
read in context: 8 are artefacts (出頭, 講親, 著著, 結結, 粒粒, 到家, 打石, 過水), 亮亮 stays in doubt, the rest are
real (當當 is 當當在該 + verb, "in the middle of doing").
After 外篇 3 (which teaches 七早八早, 毋多知仔, 一𥍉目): 126 中高級, 99 高級.

## Plan
1. **外篇 3** (id 173): the 初級 and 中級 words still untaught (`make coverage`), plus a few attested words that fit.
   Done 18 Nov 2026 (`course/batches/P64.md`, "外篇 3"): 初級 and 中級 99% after it.
2. **7–8 extra stories of about 30 words each** for the attested list, the words grouped by what fits one scene
   (category is a start: 時空與情狀副詞 and the doubled adjectives need a narrator; 外在活動與動作 a working scene).
   Skip `SEG` words unless their official sentence holds them; read the hits of `POLY` words before choosing a sense.
   Done 18 Nov 2026: 外篇 4–10 (ids 174–180; essay, tale, news, story, letter, speech, fable), 233 new words, 210 of
   them attested (`course/batches/P74.md`). Left on the list: the 8 `SEG` words, 亮亮 (`SEG?`), and 吊頸, 一條線, 人老,
   圓墳, 金斗盎, 無核卵 (reasons in P74.md). 中高級 12% → 18%, 高級 2% → 5%.
3. **The remaining attested words as cards**: the official sentence and its recording, no story.
4. Later: a **"met in my books"** list from the private Books tab (跳童 …): words the user meets while reading, ranked
   by that rather than by the corpus. Built in Hkka-private only.
