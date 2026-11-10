# Handover: the tooling for writing 進修 lessons (10 Nov 2026)

For whoever writes P36–P70 next. It explains what was added on 10 Nov 2026, why, and how to use it.
The plan and the decisions are in `docs/perfectionnement-plan.md`.

## Why it exists
Writing P1–P35 was slow and cost a lot of usage. Three things took the time:
1. For every lesson, the writer searched the database for 40–60 words and checked each one.
2. The writer read the whole checklist (233 lines) before every batch.
3. The review agent spent its time on mechanical errors (a wrong reading, a wrong `source:`).

Now a script does these three things. Lessons are still written one at a time, and a fresh agent still reviews each
batch of seven.

## Set-up (the cloud session is not persistent: do this first)
```sh
git clone https://github.com/tbrapor-arch/Hkka && git clone https://github.com/tbrapor-arch/Hkka-private
cd Hkka
HAKKA_PRIVATE=../Hkka-private make db     # about 1 minute → data/build/hakka.db
make lint                                 # must end with "0 error(s)"
```
Without `HAKKA_PRIVATE` the database has no frequencies and no audio flags. The packets still work, but the word
order is poorer.

## What was added
| File | What it is |
|---|---|
| `tools/packets.py` | Four commands: `plan`, `packet N`, `status`, `recycle` |
| `course/packets/plan.tsv` | The word plan: 1,350 words for P36–P69, about 45 per lesson. Made once. You can edit it by hand |
| `course/packets/PNN.md` | The packet of one lesson. Generated, not committed (`.gitignore`) |
| `course/batches/rules.yaml` | 37 checklist rules that a pattern can catch. Lint reads it |
| `course/batches/card.md` | One page: the rules a script cannot check, and the order of work |
| `course/batches/state.md` | The story so far, in 40 lines. Add three lines per lesson |
| `tools/lint.py` | New checks for 進修 (list below) |
| `Makefile` | `make packet N=36` |

## How to write one lesson
1. `make packet N=36`, then read `course/packets/P36.md`, `course/batches/card.md` and `course/batches/state.md`.
2. Choose a genre and a scene that hold 40 or more of the packet words.
3. Start from the sentences tagged `[clean]`. Quote them exactly, with `source: kaga115`. Then write the lines between.
4. `make lint`. Fix every error. Fix every warning, or know why it stays.
5. Commit. Add three lines to the log in `state.md`.

After seven lessons: write the batch table in `course/batches/P36.md`, ask a fresh agent to review, fix, then run
`python3 -I tools/packets.py recycle` and `make coverage`.

## How to read a packet
- **Words table.** One row per word: reading, level, glosses, type, flags.
  - `POLY`: the same characters have another reading. Choose the reading by sense.
  - `DECL`: the same characters are already declared in a lesson with another reading.
  - `SYL`: one syllable for two characters (幾下 giaˊ). Lint cannot align it.
  - `f=0`: a rare word. Use its official sentence.
- **Official sentences per word.** Up to three for each word.
  - `[clean]`: every word is taught or in the packet. You can quote the sentence as it is.
  - `[+ 甲 乙]`: the sentence also brings in these untaught words.
  - `audio`: the word's example clip holds this sentence alone. `audio (clip shared)`: the clip holds several examples.
  - The second line is a draft pinyin. `{a|b}` means the word has two readings: choose one. The draft is not checked:
    lint checks it when it is in the lesson.
- **Left over from earlier packets.** Planned words that an earlier lesson did not teach. Use what fits.
- **Recycle.** Part 1 words that no dialogue uses. They are not new words.

## How the plan was made
- Pool: every untaught 初級 word (131) and 中級 word (798), then the 421 most frequent untaught 中高級 words.
- The lists give each word a theme (類別). Eleven themes can give a scene (居家生活, 人體與醫療 …). Their words are cut
  into packets of about 27, easier words first, and the themes alternate from lesson to lesson.
- Seven themes give no scene (抽象概念, 副詞, 量詞 …). Their words are dealt out evenly, about 18 per lesson.
- `plan --force` makes the plan again from the words still untaught. Do this only if the plan no longer fits.

## What lint now checks in 進修
| Level | Check | From |
|---|---|---|
| E | `source:` names a table that does not hold the sentence (dialogue and exercises); `abridged: true` means "part of a sentence" | all 進修 lessons |
| W | A pattern in `rules.yaml` (for example 幾點, 逐 read giugˋ before 日, bare 毋 + adjective) | all 進修 lessons |
| W | A review lesson reuses fewer than 3 new words of one of the six lessons before it | all 進修 lessons |
| W | A new word is used only in the exercises | P36 on |
| W | A new word's characters were already used in an earlier lesson with the same reading | P36 on |
| W | A new word's characters are already declared with another reading | P36 on |

To silence a rule on one line, add `ok: [rule-id]` to the line (see P10, line 25).
The three "P36 on" checks skip P1–P35 because their findings there were reviewed and accepted (`CHECK_FROM` in `lint.py`).

## How to add a rule after a review
- If a pattern can catch the finding, add a rule to `rules.yaml` (`id`, `hanzi`, optional `key`, `msg`).
- If not, add one line to `card.md`.
- In both cases, put the evidence (counts, example sentences) in `checklist.md`.
- Then run `make lint` on all lessons. If the new rule gives a false alarm, make the pattern narrower.

## Checked on 10 Nov 2026
- `make lint` on the 135 lessons: 0 errors, and no new warning on P1–P35.
- A test lesson with errors on purpose (wrong table in `source:`, 幾點, 逐日 read giugˋ, 打針, bare 毋貴, a word used
  only in an exercise): lint reported every one.
- Packet P36: 45 words, 120 clean official sentences, no word without an official sentence.
- `recycle` leaves the 145 words of `recycle.tsv` unchanged, as expected: no lesson was written since the last update.

## Limits to know
- The `[clean]` tag cuts sentences by characters only, because the lists give the examples no pinyin. A character with
  two readings (落 log / lau) counts as taught when either reading is taught. Lint finds the difference later.
- The draft pinyin applies no sandhi and no 仔 rule. The lessons write citation tones, so this is correct for them.
- The themes of the lists are broad. A packet of 外在活動與動作 holds actions of many kinds: the writer still has to
  find the scene. You may move words between lessons in `plan.tsv`.
- The rules look at 進修 lessons only (Sixian). Part 1 is not checked against them.
- No lesson has been written with the packets yet. P36 is the first test: note what was missing in the packet and
  improve `packets.py` after the first batch.

## Next
1. Brief for batch P36–P42 (`course/batches/P36.md`): calendar from Mon 19 Feb 2029 (compute 元宵, 天穿日, 清明 with
   `lunardate`), one genre and scene per packet.
2. Write P36–P41 one at a time, then the review lesson P42.
3. Fresh-agent review, fixes, new rules, `recycle`, `make coverage`. Show the batch result to the user.
