# Handover: synthetic voice for the lessons (2026-11-08)

**Verdict from the listening check:** the user found VoxHakka's quality "really good" on the Sixian voice-check page
(official sentences heard next to the real 客委會 recordings, plus lesson lines). Next step: voice every lesson line.

## What exists

| Piece | Where | State |
|---|---|---|
| Real recordings, one clip per word + one per word's examples | Hkka-private `audio/clips` (release `audio-115-clips`, `tools/fetch_clips.sh`), table `audio_clip` in hakka.db | Sixian 基礎級 → 高級 complete (7,890 words); Hailu 基礎級 → 中級. See `docs/audio.md` |
| Synthetic voice | VoxHakka, `formospeech/yourtts-htia-240704` (YourTTS/VITS, 6 accents, multi-speaker, runs on CPU) | **CC BY-NC 4.0**: ship as separately licensed assets in a free app, never under the course's CC BY-SA |
| Comparison tool | Hkka-private `tools/tts_compare.py` | builds the listening page ("Sixian Voice Check" artifact) |
| Lessons | `course/lessons/001–100.yaml`: 1,147 dialogue lines, Sixian + Hailu blocks (`hanzi`, `pinyin`, optional `groups`) | part 1 complete (other discussion) |

## How the voice is driven (keep this)

1. **Input = the lesson's own pinyin, never the characters.** VoxHakka's character reader (formog2p) gets grammar words
   wrong (人 min24, 好 hau55, 會 fi55, 若 na55, 個 gai55…) and applies no sandhi.
2. `tools/sandhi.py` `spoken()` turns the pinyin (or `groups`, where `|` marks phrase breaks) into spoken tones:
   陰平 → 11 inside a phrase, 仔 eˋ → eˇ after 31/2.
3. Each syllable goes to the IPA symbols VoxHakka was trained on. The table is learnt from formog2p's parallel
   lexicons `lexicon/pinyin/hak_sx.json` ↔ `lexicon/ipa/hak_sx.json` (majority vote per toneless syllable). The tone
   value is appended as `_24`, `_11`… Unmarked = 55.
4. Punctuation becomes a `，` pause. Tokenising follows the Space's `parse_ipa`: tones are separate tokens, every
   other symbol is one character.
5. Call `Synthesizer.tts(tokens, speaker_name=…, language_name="sixian")`. Use `hailu` for Hailu, which needs a
   `hak_hl` IPA table built the same way.

## Environment (cloud session; re-create, it is not persistent)

```
python3.11 -m venv tts311 && tts311/bin/pip install "TTS==0.22.0" formog2p huggingface_hub pyyaml scipy
GIT_LFS_SKIP_SMUDGE=1 git clone https://huggingface.co/spaces/united-link/taiwanese-hakka-tts space   # for replace/tts.py
HF_HUB_DISABLE_XET=1 tts311/bin/python Hkka-private/tools/tts_compare.py --space space --out OUT
```

Notes for the environment:
- Download from Hugging Face with `HF_HUB_DISABLE_XET=1` (the Xet CDN is blocked).
- `tts_compare.py` imports numba before putting `Hkka/tools` on the path: that folder has a `coverage.py`, which
  shadows the `coverage` package numba imports.
- Speed: about 1 s of CPU per line and voice. All 1,147 lines × 2 accents take minutes, not hours.

## Voices (VoxHakka speakers)

The age of each speaker is not documented, so listen before casting the older characters.

| Region | Male | Female |
|---|---|---|
| 苗栗 (Sixian heartland, Sam's backdrop) | 朱品諭, XM | 江芮敏, 王于郡, 胡祺梓, 陳筠蓁, XF |
| 新竹 (Hailu country) | 羅盛滿, 蘇佑昇, 黃盛源, HM | 戴君儒, 黃于娟, HF |
| Other | 周碩興 (桃園) | 宋涵葳 (東勢), 洪藝晅 (雲林) |

Proposed casting, one fixed voice per character. Main speakers by line count: Sam 319, 阿婆 210, 阿明 132, 阿英 129,
阿公 87, 阿姆 37, 財伯姆 26, 頭家 21…
- Sixian: Miaoli voices.
- Hailu lines (the 竹東 / Hsinchu chapters from lesson 50): Hsinchu voices.
- Sam is a learner. Using the same native voice for him is simplest. Do not try to fake an accent.

## Next steps

1. **Casting page.** One short line per candidate voice, so the user can assign a voice to each main character.
   Same page pattern as the voice check.
2. **`tools/tts.py`.**
   - Input: lesson YAML. Output: `audio/tts/<accent>/<lesson>-<line>.m4a`, in Hkka-private (the output is NC).
   - Cache keyed by hash(accent, voice, spoken pinyin), so editing a line re-voices only that line.
   - Also voice the new words: use the real clip from `audio_clip` when one exists, TTS otherwise.
3. **Lines that are official sentences use the real recording.**
   - 115-list examples: the `.ex` clip. When a word has several examples they share one clip, so split it first.
   - Lessons also quote the 2013 lists, MOE dictionary examples and the 客語百句. The 客語百句 have official mp3 URLs
     (easytalk.hakka.gov.tw, `sentence.audio_url`), downloadable only through the user's browser.
4. **Hailu.** Build the `hak_hl` table, check Hailu sandhi in `sandhi.py` (Hailu has its own rules), and run a voice
   check page for Hailu before voicing.
5. **Automatic check.**
   - Round trip through a Hakka recogniser (`formospeech/whisper-large-v3-taiwanese-hakka`, also CC BY-NC; large-v3
     is slow on CPU, so run it in GitHub Actions or on Kaggle), then diff with the input pinyin.
   - Lines that fail get `check: true` and stay unvoiced.
6. **Licence.**
   - Add the VoxHakka credit and its NC licence to ATTRIBUTION.md, kept apart from the course content licence.
   - If the app is ever paid: apply for HAT-TTS (NT$1,000 per accent set, commercial use allowed) and fine-tune our
     own voice. That needs 10–30 GPU-hours (Kaggle free quota or a rented GPU), not Claude usage.

## Decisions (2026-11-08)

- **Input: "ours"** (our pinyin + sandhi). The user could not tell the two apart by ear, so this was settled by
  measurement. On the 1,382 Sixian dialogue lines, the character path differs from the lesson text in **990 lines
  (72%)**, and 73 more lines are unreadable to it. The most frequent differences:
  - **missing sandhi:** 阿 a24 instead of a11, 當 dong24 instead of dong11, 頭, 有, 較, 三, 公, 今, 山…;
  - **wrong readings:** 吔 e31 instead of le24, 會 fi55 instead of voi55, 好 hau55 instead of ho31, 毋 ŋ̩ instead of
    m̩, 在 cai55 instead of coi24;
  - Latin names read as English.

  With "ours", the audio always matches the pinyin the learner reads.
- **Voices:** the proposal above is approved: one fixed voice per character, Miaoli voices for Sixian, Hsinchu
  voices for Hailu. The casting page (step 1) picks the individual voices.
- **Licence:** CC BY-NC audio is accepted for the app, shipped as separately licensed assets (ATTRIBUTION.md).
  HAT-TTS stays the route if the app ever becomes paid.
