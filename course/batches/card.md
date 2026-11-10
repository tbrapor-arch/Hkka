# Writer's card for 進修 (one page)

What a script cannot check. `make lint` checks the rest (`rules.yaml`). The evidence for every point is in
`checklist.md`: open it only when a point here is not enough. 進修 is Sixian only, so the Hailu rules are left out.

## Order of work for one lesson
1. `make packet N=36` and read `course/packets/P36.md` and `state.md`.
2. Pick a genre and a scene that hold 40 or more of the packet words. Start from the `[clean]` sentences: quoted word
   for word with `source: kaga115`, they are already correct and have a real recording.
3. Write 20–30 lines, two exercises of 5 items, notes, `new_words`. Every new word is in the text, not only in an exercise.
4. `make lint`: 0 errors, and no warning left without a reason.
5. Read the lesson once against this card. Commit. Add three lines to `state.md`.

## Quoting
- An official sentence is quoted exactly, with its own particles (哩, 了, 異). If you change one character, it is the
  course's sentence: no `source:`.
- A shortened quote gets `abridged: true`. A sentence lint cannot read is adapted, with `check: true` and a note.
- In a note, "official" means kaga115 or kaga. An MOE example is "MOE", has no accent and no recording.
- A song or verse quote names its source. No copyright claim.

## Words and senses
- A word with a POLY flag: choose the reading by sense, and say the sense in the gloss.
- The gloss of a new word matches a sense the list gives. If the list has only a measure-word sense, gloss from MOE and
  say so.
- Before writing "our own phrase", check that no taught word already covers it.
- 歇: hed "live (long term)", hiedˋ "stay (guest, a few nights)". 喊: ham "tell someone to", hemˊ "shout".
- 好 + verb: hau "like to, keen to", hoˋ "easy to, good to; may". 頭擺 "formerly"; 頭一擺 "the first time".
- 頭先 "just now"; "at first" is 一開始. 黏時 "at once"; "suddenly" is 好恬恬. 識 "know (a person); ever", not "can" (會).
- 還好 + adjective is "very". "Not bad" is 會做得. Gloss 盡 every time ("very" or "most").

## Grammar a script cannot see
- "We": 𫣆兜 includes the listener, 𠊎兜 excludes. Check each one against who is listening (in a letter: writer +
  reader is 𫣆兜).
- Demonstrative + classifier + noun (這隻柚仔). A bare noun only where an official sentence has it.
- Adjectives are negated with 毋會 or 無. 毋好 "bad" is the one exception.
- "Talk to X" is 同 X 講話; 同 X 講 is "tell X". "Never" is 從來毋識 + verb, or 毋識 + V過.
- Advice: 愛多 + verb. Quantity: verb + 加 + amount (歇加兩暗晡, 買加兜仔).
- A pattern with no official sentence either changes or gets `check: true` and a note that says so.

## People and story
- Sam (French, surname Martin) calls Mrs Liu 伯姆. 阿姆 is for A-in and A-min. Sam has a sister, Lucie.
- 阿太 is Grandpa's father. 姐婆 is the maternal grandmother. 頭家 is the owner, not the waiter.
- Sam spent the winter of 2026–27 with the Lius: nothing in Part 2 is his "first" winter or New Year in Taiwan.
- No claim about a character's earlier lines (first, longest, never) without counting them.
- Keep the calendar of the batch: weekday, who is at school or work, weather, what was eaten when.
- January and February: 今年, 舊年 and 天光年 change at the lunar New Year. For a season, name the season.

## Notes
- No "never" or "always" without evidence. No unverified geography, history or custom: an official sentence, or the
  words "general knowledge".
- Leaflets, rules and opening hours of real institutions are invented: say so in the setting.
- "Not in the data" only after searching the official sentences and the MOE definitions.
- After any insertion, check the line numbers and the "lesson N" references in the notes.
- Numbered items inside a text run in order.

## Review lessons (every 7th)
- No new words. At least 3 new words from each of the six lessons before (lint counts them).
- Check the batch calendar before "long time no see" and similar lines.

## After the batch
- A fresh agent reviews the seven lessons against the database, for what lint cannot judge: sense of polyphonic words,
  natural wording, story, notes, the English.
- A finding that a pattern can catch becomes a rule in `rules.yaml`. Another finding becomes one line here, and its
  evidence goes into `checklist.md`.
- `python3 -I tools/packets.py recycle`, then `make coverage`, then update the batch table and `state.md`.
