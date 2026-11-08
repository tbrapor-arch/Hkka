# Part 2: 進修 (Perfectionnement), plan

Decided with the user on 8 Nov 2026. Model: Tsheh-tû's `docs/perfectionnement-plan.md` (P1–P70, finished 3 Nov 2026).
Read `course/batches/checklist.md` in full before writing any lesson.

## Starting point (8 Nov 2026, after the light revision of Part 1)
`make coverage`: 1,874 words taught; 基礎級 483/483, 初級 487/841, 中級 311/1,706.
Still to teach up to 中級: **1,749 words** (354 初級 + 1,395 中級). Nearly all have an official example sentence with a
Sixian recording in the 115年度 lists, so many lines can be `source: kaga115` sentences with real audio.
About 430 of the 中級 words have zero Glossika and corpus frequency: expect the late lessons to need more care.

## Decisions
| Point | Decision |
|---|---|
| Spirit | Assimil *Perfectionnement*: longer texts, varied genres and registers, proverbs (師傅話, 諺語) as titles; the aim is vocabulary |
| Size | 70 lessons, every 7th a review (no new words); second wave from P36 (P(N−35)), inside Part 2 |
| New words | **about 40 per lesson** → all of 初級 and 中級 (1,749) plus about 650 frequent 中高級 words |
| Length | 20–30 lines, as in Tsheh-tû |
| **Accent** | **Sixian only.** No Hailu lines in 進修 (user's decision). Word cards may still show the Hailu form taken automatically from `v_word_parallel`; nothing is written by hand. The app labels Part 2 "Sixian only" |
| Story | **Sam back in Taiwan** for a second year near Miaoli / Hsinchu; he sits the 中級 certification. The 劉 family, 阿舅 in 竹東 and the 美濃 couple recur. Prose genres (article, tale, news, document…) need no cast |
| Method | Words first: take 40–60 untaught words (`make coverage`), group them, then find a genre and a scene that hold 30–40; verify every word in one pass before writing; prefer official sentences |
| Exercises | Two exercises of 5 items each (translate, fill) |
| Files | `course/perfectionnement/NN.yaml`, `id: N` (internal id 100 + N), field `genre:`, `speaker:` optional in prose; `sx` block only |
| Review loop | One brief per batch (`course/batches/PNN.md`), a fresh-agent review against the database, fixes, then the checklist is updated |
| App | "Second notebook" after the grid of 100, as in Tsheh-tû; waits for the app |

## Genres
Tsheh-tû's set: dialogue, article, letter, interview, tale, speech, essay, document, song, news, play, diary, debate,
story. Hakka additions to use where the words fit:
- **山歌** lyrics for song lessons (阿公 sings them in Part 1);
- a **採茶戲** scene for a play lesson;
- tales: 伯公, 天穿日, local legends;
- **客家電視** style news;
- an **exam paper** (the 中級 format: listening, reading, picture description) as a document lesson, in the batch
  where Sam sits the test.

## Tools to port or adapt
`make lint` and `make coverage` must scan `course/perfectionnement/` and accept lessons with no `hl` block.
Port from Tsheh-tû as needed: `candidates.py` (one-pass word check), `xrefs.py` (lesson references in notes,
duplicate `new_words`), `qc_readings.py`, `qc_glosses.py`, `fresh.py` / `taught_later.py`.

## Next
1. Adapt lint and coverage to `course/perfectionnement/` (Sixian only).
2. Brief for batch P1–P7 (words first), agreed with the user, then write.
