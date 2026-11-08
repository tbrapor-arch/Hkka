# Handover: planning Part 2, 進修 (Perfectionnement)

Written 8 Nov 2026, at the end of Part 1. Open a new conversation in the claude.ai project "Hakka APP" and paste:
**"Read claude/hakka-perfectionnement-handover.md and let's plan the 進修 part."** The first session is for
planning with the user, not for writing lessons.

## Where Part 1 stands
- **Lessons 1–100 are written, reviewed and fixed.** Sixian, with Hailu written alongside every line. `make lint`
  shows 0 errors. A light revision then taught the 106 basic words that were still missing: 基礎級 is now 100%,
  初級 58%, 中級 18%.
- **The story** covers Sam's year with the 劉 family in Miaoli, Nov 2026 – Nov 2027, on the real calendar. Lessons
  99–100 are in France: a video call in two accents, then a letter.
- **How it was written.** Each of the 15 batches had a brief, `course/batches/NN.md`, and a fresh-agent review
  against the database. `course/batches/checklist.md` is the rulebook that grew out of those reviews; read it in full
  before writing anything.
- **Facts to know before you start:**
  - The counting rule at the top of the checklist: compare the accents on the official lists only.
  - `source:` labels name the table a quote actually comes from. Only `kaga115` sentences have audio.
  - The sentence-final particle is written 吔 in Sixian and 咧 in Hailu, read leˊ / leˋ.
  - 241 lines are marked `check: true`, waiting for a native speaker.
- Repo status, decisions and other open items: `docs/handover.md`.

## Model: Tsheh-tû's 進修 (read it first)
Tsheh-tû finished its Part 2 on 3 Nov 2026: 70 lessons, P1–P70. Take its approach as the starting point, and adapt
it only where Hakka needs something different. Read, in the Tsheh-tû repo (`tbrapor-arch/tsehtu`):
- **`docs/perfectionnement-plan.md`.** The spec, the decisions made with the user, the method, the checks per batch,
  and every batch table. Note the progression:
  - new words went from about 30 to about 40, then to 44–55 a lesson at the user's request (27 Oct);
  - 20–30 lines per lesson;
  - one review every 7th lesson;
  - the second wave starts at P36 and stays inside Part 2.
- **`docs/batch-progress.md` and `docs/lessons-22-49-lengthening.md`.** How the batches were run. The
  "consequences for future lessons" are relevant: never declare a word twice; check `taught_later.py`.
- **`docs/modern-vocab-brief.md`.** What came after 進修: coverage, the gaps, and modern vocabulary.
- **Its tools** `coverage.py`, `candidates.py`, `xrefs.py`, `qc_readings.py` and `qc_glosses.py`. Port the ones that
  Hkka lacks.

Main decisions to carry over (the user confirms each one in the planning session):
- **The spirit of an Assimil *Perfectionnement* volume.** Lessons are longer and their genres vary: dialogue,
  article, letter, interview, tale, speech, essay, document, song, news, play, diary, debate. The registers vary too.
  Use proverbs (in Hakka, 師傅話 and 諺語) as titles. The aim is **vocabulary**, not a thematic plan.
- **Method: start from the words, not the theme.**
  - Take 40–60 untaught words (`make coverage`, levels 中級 and above). Group them, then find a genre and a scene that
    hold 30–40 of them.
  - Verify every word in one pass before writing.
  - Prefer official sentences (`source: kaga115`, which have audio).
- **Format.**
  - Files are `course/perfectionnement/NN.yaml`, numbered from 1, with internal id 100 + N.
  - Add a `genre:` field; `speaker:` is optional in prose.
  - Two exercises of 5 items each.
- **Layout in the app.** It is a "second notebook" after the grid of 100. That waits for the app itself (still to do).

What Hakka needs on top:
- **Two accents.** Every line gets a Hailu version. Genres like news, article and document also need it, so check
  the Hailu wording of set phrases and proverbs.
- **Coverage after Part 1.**
  - 中級 is only partly covered (18%; 初級 58%; figures in `make coverage`). That gives Part 2 a clear vocabulary
    target: the rest of 初級 and 中級 first, then 中高級.
  - The 115年度 lists also have about 7,700 official example sentences with recordings, so many 進修 lines can be
    official sentences.
- **Story options for the user to choose from.**
  - Sam in France, and A-in's visit in spring (promised in lessons 97–100).
  - Sam's return to Taiwan.
  - Prose genres with no cast at all.
  - The family is all available, including 阿舅 in 竹東 (Hailu) and the 美濃 couple (south Sixian).
- **Keep the review loop.** Each batch gets a brief, a fresh review and fixes; that is what kept Part 1 accurate.

## The Assimil Russian *Perfectionnement*
The user can upload the Assimil *Perfectionnement russe* if it helps, for example to compare its lesson lengths,
genre mix and new-word counts with Tsheh-tû's reference volume. If it is uploaded:
- Store it in **Hkka-private** under `reference/`, never in the public repo.
- Use it only for **ideas and counts**: lesson length, genre mix, words per lesson, how the exercises are built.
- **Nothing from its text leaves that folder.** Tsheh-tû applied the same rule to its reference scan.
- Ask for it if the planning needs real numbers; don't assume its contents.

## First session: suggested agenda
1. Confirm or change the carried-over decisions above, especially the number of lessons, the new words per lesson,
   and the length.
2. Choose the story frame and the cast.
3. Draft the brief for batch P1–P7 using the words-first method. Get the user's agreement, then write.
