# Pacing

Same shape as Tsheh-tû (`tsehtu/course/pacing.md`, `docs/course-plan.md`): 100 lessons, every 7th a review (7, 14, …
98), second wave from lesson 50 (N ↔ N−49), dialogues growing from 8 lines to 20. The difference is the number of new
words: Tsheh-tû taught about 1,300 in part 1; this course aims at about **1,860**, and gets there **progressively**.

## New words per lesson (reviews: none)
| Block | New lessons | Lines | New words / lesson | Words in block | Cumulative | Tsheh-tû (observed) |
|---|---|---|---|---|---|---|
| 1–6 | 6 | 8–9 | 16 | 96 | 96 | 17 |
| 8–13 | 6 | 8–9 | 17 | 102 | 198 | 11.5 |
| 15–27 | 12 | 9–10 | 19 | 228 | 426 | 11.5–13 |
| 29–48 | 18 | 11–14 | 21 | 378 | 804 | 13.4 |
| 50–76 | 24 | 15–16 | 23 | 552 | 1,356 | 14.5–15 |
| 78–100 | 20 | 17–20 | 25 | 500 | **1,856** | 14.6 |

Lesson 1 starts at 16, about where Tsheh-tû started (17), but unlike Tsheh-tû the curve never drops: it climbs every
block to 25. The jump in dialogue length sits at 50–51, as in Tsheh-tû. Early lessons lean on same-as-Mandarin words
(see below) so 16 stays light while pinyin and the six tones settle.

## What a "new word" costs
About half of the core words are written and used as in Mandarin (你, 去, 看, 學校): for this learner they are a
pronunciation job, not a meaning job. Each lesson mixes them with Hakka-only words and false friends:
- lessons 1–27: at most **6** Hakka-only or false-friend words per lesson, the rest same-as-Mandarin or partial;
- lessons 29–48: at most **8**; lessons 50–100: at most **10**.
So the real load grows from about 6 to 10 "hard" words per lesson, while the count climbs from 16 to 25.

## Targets (certification levels, Sixian 115年度 lists)
- By lesson 49: all of **基礎級** (488) and about 300 words of 初級.
- By lesson 100: all of **基礎級 + 初級** (1,330) and about 500 words of 中級 (the most frequent ones).
- 進修 (part 2, 70 texts, about 40 new words each): the rest of 中級 and the start of 中高級.
Order inside a level: frequency (Glossika × 10 + corpus), Hakka-only grammar words first, as `make coverage` will list.

## Rules (as in Tsheh-tû)
- A word is declared new once, in the first lesson that uses it; never declared again.
- Reviews add no words; they recombine the six lessons before them.
- Every word in a line must already be taught or be new in that lesson (lint), except names.
- Hailu lines (written alongside) follow the same new-word list through `v_word_parallel`; a Hailu word that differs from
  Sixian is noted, not counted twice.
