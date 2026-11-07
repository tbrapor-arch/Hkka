# Audio plan (2026-11-07)

The course must sound **Taiwanese Sixian**, not Mainland Hakka. No Mainland voice is used anywhere.

## Why not a Mainland or Azure voice
- Azure TTS has **no Hakka voice**. Its Chinese locales are Mandarin (with Shandong, Sichuan, Henan, Liaoning, Shaanxi,
  Guangxi accents), Wu (`wuu-CN`), Cantonese (`yue-CN`, `zh-HK`) and Taiwan Mandarin (`zh-TW`); the dialect voice
  `zh-CN-XiaoxiaoDialectsNeural` adds Minnan (`nan-CN`) and more Mandarin accents, still no Hakka.
- The Mainland reference accent is Meixian 梅縣. Taiwan Sixian comes from the four counties around it and is close,
  but not close enough for audio: Meixian 陰平 is level (~44) where Sixian rises (ˊ24), and its 去聲 falls (~53) where
  Sixian is level (55). Two of six tones, on very frequent words (家, 天, 係, 愛…), plus vocabulary differences.
  A Meixian voice would train the wrong accent.

## Layers
| What | Audio | Status |
|---|---|---|
| Certification words and their example sentences (115年度, Sixian + Hailu) | **real recordings**, 客委會 | **cut**: one clip per word + one per word's examples for 基礎級, 初級, 中級 (Sixian + Hailu) and 中高級 (Sixian): 8,174 words; Hailu 中高級 and 高級 to run. See below |
| Lesson lines that match an official example sentence | the real recording of that sentence | lint to flag matches (to write) |
| Other lesson lines (dialogues we write) | **Taiwanese Hakka TTS**, labelled "synthetic" in the app | engines under test, see below |
| Glossika | none in the app (private, for the learner's own listening) | — |

Never splice word recordings into sentences: no sandhi, robotic prosody.

## TTS candidates (Taiwan-trained only)
| Engine | Accents | Input | Licence | Notes |
|---|---|---|---|---|
| 客委會 web TTS (speech.hakka.gov.tw/TTS/Synthesis) | Sixian M/F, Hailu M/F | Hakka characters (pinyin input untested) | site content under the Council's open-data statement (free, non-exclusive, sublicensable, irrevocable, cite source); synthesized output not named explicitly | free, no login; one sentence at a time, download valid for the session (members: last 10). No public API; the API existed for the 2025 客語AI應用黑客松 teams |
| VoxHakka (United Link + National United University), `formospeech/yourtts-htia-240704` | all six | pinyin (via `formog2p`) or characters | **CC BY-NC 4.0** on Hugging Face (the 2024 paper and press said CC BY 4.0; the model card now says NC) | YourTTS (VITS), multi-speaker, runs on CPU. Demo: HF space `united-link/taiwanese-hakka-tts` |
| formospeech F5-TTS / OmniVoice Hakka | Sixian, Hailu (+) | text + reference audio (zero-shot) | CC BY-NC 4.0, gated | newer, voice cloning from a reference clip |
| HAT TTS set (60 h per accent: 30 h male + 30 h female, studio, single track) to train or fine-tune our own voice | Sixian, Hailu | — | signed agreement; individuals may apply; perpetual; fee per set (NT$1,000); **commercial use permitted, education encouraged; models we train are ours**, the corpus itself cannot be resold or sublicensed; credit "台灣客語語音資料庫（客委會授權）" (speech.hakka.gov.tw FAQ and AboutDB) | the clean-licence route: our own voice, no NC restriction |

**Licence consequence:** NC audio can ship in a free app as separately licensed assets with attribution, but cannot
go under the course's CC BY-SA. Keep TTS audio out of the content licence; say so in ATTRIBUTION.md.

**Feed pinyin, not characters**: we control readings (文白) and apply sandhi ourselves (`tools/sandhi.py`).

**Reference recordings**: speech.hakka.gov.tw/search/list (音檔試聽) has searchable HAT sample recordings by accent,
gender, age and speaker type, each with characters and tone-number pinyin, downloadable. Under the site's open-data
statement; a ready test set for comparing synthetic voices.

## First VoxHakka test (2026-11-07)
- Runs on CPU in the cloud session (Python 3.11, `TTS==0.22.0`, `formog2p`; download with `HF_HUB_DISABLE_XET=1`).
  18 speakers, 8 of them from Miaoli (e.g. 江芮敏 F, 朱品諭 M), which suits Sam's Miaoli backdrop.
- **Its character reader is not reliable enough**: on the 477 基礎級 words it knows, it gives the official reading for
  414 (87%), and misses exactly the grammar words: 人 min24, 好 hau55, 會 fi55, 吾 ng11, 若 na55, 個 gai55, 較 gau31;
  no sandhi, no 仔 → eˇ.
- **Feeding our own pinyin works**: syllable → IPA table built from formog2p's Sixian lexicons; sandhi applied
  before synthesis (天光日 tien11 gong24). So `tools/tts.py` takes the lesson's pinyin + `tools/sandhi.py`, never
  the characters.
- Still to judge by ear, and against the real recordings once `audio-115` is up.

## Real recordings: cut into clips (2026-11-07)
- Source: the six 115 zips, release `audio-115` on Hkka-private (each with a silence report).
- Each batch file (`01基礎級/01-001-010.mp3`, `06--041-050.mp3`) reads, per word: its number (一, 二 … 二百七十一), the
  word, then its example sentence(s). `Hkka-private/tools/audio_cut.py` splits at silences, transcribes the short
  pieces with Whisper small (the Hakka numbers come out as 一 二 三, or as "Sup" for 十 siib, "Q" for 九 giu), and aligns
  one number per word with a duration model (syllables of the word + its examples, from kaga115). Between two
  numbers: first piece = the word, the rest = the examples.
- Workflow `audio-cut` (16 parallel jobs, ~25 min) → release `audio-115-clips`; `tools/fetch_clips.sh` merges them
  into `audio/clips/<accent>/<level>/<unit>-<n>.m4a` and `.ex.m4a` (AAC 40 kb/s mono, ~200 MB for 6,060 words)
  and `audio/manifest.json`, keyed by kaga115 `src_id`.
- `build_db.py` with `HAKKA_PRIVATE` loads them into `audio_clip(entry_id, accent, kind, path, number_heard)`:
  **all 3,030 core words have a Sixian word clip**, 3,027 a Hailu one; 2,913 / 2,717 have example audio.
- Confidence: 3,988 of 6,060 words have their number actually heard; the rest are placed by the duration model.
  Hand checks on test files (Sixian, Hailu, 中級, 高級) were 10/10; a Whisper round trip on 300 random clips found no
  clear shift (Mandarin Whisper is weak evidence on Hakka words). Known limits: a word read twice keeps the repeat in
  the `.ex` clip; when a word has several examples they share one `.ex` clip.
- 2026-11-07: Sixian 中高級 cut too (`set=sixian-zgj`, 2,114 words, 1,270 with the number heard). One file
  (017--081-090) had pauses too short between number and word: the cutter now retries with 0.2 s silences; that
  file was re-cut locally and lives in `audio/extra/` (the session cannot upload release assets).
  Sixian now has a word clip for every 基礎級–中高級 word (5,144).
- To do: Hailu 中高級 and 高級 (`set=upper`, cost ≈ 400 Actions minutes per set of 4 zips); split multi-example clips; flag lesson lines that are official
  examples so they use the real `.ex` audio.

## Checking quality without a native speaker
1. **Against real recordings**: synthesize official example sentences (we have their real audio) and compare,
   by ear and by the recogniser below.
2. **Round trip**: run TTS output through a Hakka recogniser (`formospeech/whisper-large-v3-taiwanese-hakka`, or the
   客委會 recognition API) and diff the result with the input text.
3. Lines that fail either check get `check: true` and stay unvoiced until fixed.

## Next
1. ~~Finish the `audio-115` upload; map file names to word ids; convert to AAC~~ done for 基礎級–中級 (see above).
2. Compare VoxHakka (pinyin input) with the real recordings of the same official example sentences.
3. 客委會 web TTS: synthesize the same sentences by hand (characters; try tone-number pinyin too), compare.
4. If the lesson voice must be clean of NC terms: apply for HAT-TTS-Sixian (+ Hailu) as an individual and fine-tune
   VoxHakka/YourTTS on it.
5. Pick the engine; write `tools/tts.py` (pinyin + sandhi in, cached audio out, keyed by text hash).
