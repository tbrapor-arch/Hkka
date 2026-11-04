# Project notes

## State (2026-11-04)
- Repos: `Hkka` (public), `Hkka-private` (private), same split as Tsheh-tû.
- Documentation catalogue: `docs/sources.yaml` (19 resources, licence and status for each).
- Database: MOE dictionary + 102年版 certification vocabulary in `hakka.db`; Glossika sentences from the private repo.
- Checks: for the 2,870 Sixian certification words whose characters are also MOE headwords, 2,669 (93%) have the same
  reading key. The rest are real differences (variant readings, words written with sandhi tones such as 丈人
  congˊminˊ). 78% of Glossika word tokens (23,108 of 29,738) link to an entry.

## Next
1. Download from data.gov.tw on your own machine (the cloud build machine cannot reach it) into `reference/gov/`:
   dataset 176002 (certification vocabulary + audio, current years), 176307 (Hakka corpus), 客語百句. Then write the
   importers from the real files and replace the 2013 list as the core source.
2. Check the licence and bulk download of the current MOE 臺灣客語辭典 (hakkadict.moe.edu.tw): headword audio.
3. Tone sandhi engine for Sixian (`tools/sandhi.py`, as in Tsheh-tû); the main rule is 陰平 ˊ24 → ˇ11 before
   ˊ24, 去聲 55 and 陽入 5. Test it against the workbook examples (written with sandhi tones).
4. Map Glossika's romanisation to MOE pinyin (tones and -p/-t/-k → -b/-d/-g, y → ii) so the Sixian sentences can be
   searched by key.
5. `course/000-reading-pinyin.md`, then `syllabus.yaml`.
