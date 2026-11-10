# Part 2: 進修 (Perfectionnement), plan

Decided with the user on 8 Nov 2026. Model: Tsheh-tû's `docs/perfectionnement-plan.md` (P1–P70, finished 3 Nov 2026).
Before writing a lesson, read `course/batches/card.md` (one page) and `course/batches/state.md`.
`course/batches/checklist.md` holds the evidence behind the card.

## Status (10 Nov 2026, evening)
**P1–P35 written, reviewed by fresh agents, fixed and merged into main. P36–P42 written and reviewed on branch
`claude/p36-tooling`** (not merged). Lint shows 0 errors. The accent bridge (six pages between lesson 100 and 進修 1) is
on the same branch: see "Accent bridge" below.
- Briefs and progress tables: `course/batches/P01.md` (P1–P7), `P08.md` (P8–P21), `P22.md` (P22–P35), `P36.md` (P36–P42).
- Coverage after P42: 3,093 words taught. 基礎級 100%, 初級 92%, 中級 61%, 中高級 6% (after P35: 2,862; 84%, 53%, 5%).
- New words per lesson average about 35, short of the 40 target:
  - P8–P21 averaged 28, because many candidates were already taught in Part 1.
  - From P22 on, picking words first from the untaught list raised the average.
- Recycling: 145 of Part 1's 258 exercise-only words are still unused.
- The 40-word question (raise the line cap to 35, or add a third exercise?) is answered by the word plan below:
  about 45 planned words per lesson, lessons stay at 20–30 lines and two exercises (P22 and P24 already held 43–45 new
  words in 26–30 lines). The user can still change this.
- P36–P41 average 38.5 new words (231 in six lessons); 40% of their lines are exact official sentences.
- Story so far: Sam is at 聯合大學 from Sept 2028. P42 is Sun 15 Apr 2029 (`course/batches/state.md`).
- Next: P43 onwards, from late April 2029 (桐花 season, then 端午 on 16 Jun). The 中級 exam is around Nov 2029. The second wave is the app's business
  (finishing P36 brings back P1): it puts no constraint on the words or the theme of P36.

## Process from P36 on (10 Nov 2026: faster, still one lesson at a time)
The user found the process slow and costly in usage. The cost was the word hunt for every lesson, the reading of the
whole checklist, and a review that looked for mechanical errors. These are now done once, or by a script:
1. **Word plan, once**: `python3 -I tools/packets.py plan` → `course/packets/plan.tsv`. 1,350 words for the 30
   lessons P36–P69 (reviews: P42, P49, P56, P63, P70): all the untaught 初級 (131) and 中級 (798), then the 421 most
   frequent 中高級. About 45 per lesson: about 27 of one scene theme and 18 function words dealt out evenly.
   After P70: 初級 and 中級 100%, 中高級 about 25%.
2. **One packet per lesson**: `make packet N=36` → `course/packets/P36.md`: the words with readings, glosses and
   flags, every official sentence with a draft pinyin and a `[clean]` tag when all its words are taught or in the
   packet, leftovers of earlier packets, 4–5 recycle words. No database query while writing.
3. **Lint does the mechanical review**: `course/batches/rules.yaml` holds the checklist rules a pattern can catch.
   Lint also checks `source:` in dialogue and exercises against the right table, exercise-only new words, words used
   before their declaration, a second reading of declared characters, and the 3-words-per-lesson rule of reviews.
4. **One-page card** `course/batches/card.md` for what a script cannot check.
5. **Story state** `course/batches/state.md` (40 lines) replaces re-reading the old briefs.
6. **Review once per batch of 7**, by a fresh agent, on what lint cannot judge (senses, wording, story, notes).
   The user approves the batch result, not each lesson.

Handover of the tooling: `docs/tooling-handover.md`.

## Accent bridge (10 Nov 2026)
Asked by the user: "a bridge between normal and perfectionnement, from the perspective of Sixian toward Hailu and
others". Six pages, shown in the app from the Part 2 cover, before 進修 1:
overview, then Hailu, South Sixian, Dapu, Raoping, Zhao'an. Each page has the same seven sections (tones,
consonants, vowels and endings, the suffix 仔, words that change, the same eight sentences, try it).
- `tools/bridge.py build` writes `course/bridge/*.md`. Every table, count and example is measured on the 115年度 lists
  (Hailu, Dapu, Raoping, Zhao'an), the MOE dictionary (South Sixian) and 客語百句 (the eight sentences, six accents).
- The hand-written remarks are in `course/bridge/notes.yaml`. A remark may only say what its table shows; places and
  speaker ranks are from the MOE dictionary article 107_002. The script stops if a word listed there is not in the data.
- Measured distance (Part 1 words written with the same characters): Hailu 96%, Raoping 94%, Dapu 89%, Zhao'an 77%.
  South Sixian: 91% of the MOE entries are read exactly as in the north.
- Not done: the recordings of the eight sentences (easytalk.hakka.gov.tw) are not played by the app. No native speaker
  has checked the pages.

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
| New words | **about 40 per lesson** (45 planned from P36) → all of 初級 and 中級, plus the most frequent 中高級 words |
| Length | 20–30 lines, as in Tsheh-tû |
| **Accent** | **Sixian only.** No Hailu lines in 進修 (user's decision). Word cards may still show the Hailu form taken automatically from `v_word_parallel`; nothing is written by hand. The app labels Part 2 "Sixian only" |
| Story | **Sam back in Taiwan** for a second year near Miaoli / Hsinchu; he sits the 中級 certification. The 劉 family, 阿舅 in 竹東 and the 美濃 couple recur. Prose genres (article, tale, news, document…) need no cast |
| Method | Words first. P1–P35: take 40–60 untaught words (`python3 -I tools/coverage.py 1100`), group them by theme, find a genre and a scene that hold 30–40, verify every word with `tools/candidates.py`. From P36: the packet (`make packet N=`) gives the words and their official sentences; `candidates.py` only for a word outside the packet |
| Exercises | Two exercises of 5 items each (translate, fill); no exercise-only new words |
| Reviews | Each review lesson reuses at least 3 new words from each of the six lessons before it |
| Files | `course/perfectionnement/NN.yaml`, `id: N` (internal id 100 + N), field `genre:`, `speaker:` optional in prose; `sx` block only |
| Review loop | One brief per batch (`course/batches/PNN.md`), a fresh-agent review against the database, fixes; then each finding becomes a rule in `rules.yaml` or a line in `card.md`, with its evidence in `checklist.md` |
| App | "Second notebook" after the grid of 100, as in Tsheh-tû; waits for the app |

## Recycling Part 1's exercise-only words (decided 8 Nov 2026)
`course/batches/recycle.tsv` lists the Part 1 words that no dialogue uses: the 106 basic words added in the light
revision (exercises only) and older exercise-only words. Part 1 is not reopened. Instead, 進修 lessons reuse these words
on purpose in their texts:
- they are not new words (no `new_words` entry); a note may point back with "(lesson N)";
- after each batch, `python3 -I tools/packets.py recycle` removes the words used.

## Genres
Tsheh-tû's set: dialogue, article, letter, interview, tale, speech, essay, document, song, news, play, diary, debate,
story. Hakka additions to use where the words fit:
- **山歌** lyrics for song lessons (阿公 sings them in Part 1);
- a **採茶戲** scene for a play lesson;
- tales: 伯公, 天穿日, local legends;
- **客家電視** style news;
- an **exam paper** (the 中級 format: listening, reading, picture description) as a document lesson, in the batch
  where Sam sits the test.

## Tools
`tools/lint.py` and `tools/coverage.py` scan `course/perfectionnement/` (Sixian only, 中高級 included).
`tools/candidates.py` does the one-pass word check. `tools/packets.py` (plan, packet, status, recycle) and
`course/batches/rules.yaml` were added on 10 Nov 2026; lint now checks exercise `source:` lines.
Still to port from Tsheh-tû if needed: `xrefs.py`, `qc_readings.py`, `qc_glosses.py`, `fresh.py` / `taught_later.py`.
