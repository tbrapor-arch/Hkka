# Data sources and attribution

None of these datasets are stored in this repository, except the Hakka Council files under `data/gov/`, which the
open-data licence allows us to redistribute with attribution. `make data` downloads them at pinned commits into
`data/raw/` (git-ignored), and `make db` builds `data/build/hakka.db` locally. The full catalogue of documentation,
including material that is only used as reference, is `docs/sources.md`.

| Dataset | Rights holder / maintainer | Licence | How it is used |
|---|---|---|---|
| 教育部臺灣客家語常用詞辭典 | Ministry of Education, Taiwan (中華民國教育部). Data via [g0v/moedict-data-hakka](https://github.com/g0v/moedict-data-hakka) (conversion CC0, Audrey Tang and Pierre Magistry) | [CC BY-ND 3.0 TW](https://creativecommons.org/licenses/by-nd/3.0/tw/) | Characters, six-accent readings, definitions and example sentences. Entries and sentences are reproduced unaltered; lessons are written independently. The 華語對照表 (Mandarin comparison table) is not under this licence and is not used. |
| 客語能力認證基本詞彙 (102年版) | 客家委員會 Hakka Affairs Council. Merged CSV via [Taiwanese-Corpus/hakka_elearning](https://github.com/Taiwanese-Corpus/hakka_elearning) | Government work; the Council now publishes the certification vocabulary as open data under the [政府資料開放授權條款-第1版](https://data.gov.tw/license) | Core vocabulary by level and theme, English and Mandarin glosses, example sentences. |
| 臺灣客語語料庫：客委會出版品或採錄品 ([data.gov.tw 176307](https://data.gov.tw/dataset/176307)) | 客家委員會 Hakka Affairs Council | [政府資料開放授權條款-第1版](https://data.gov.tw/license) | Committed unaltered as `data/gov/hakka_corpus_176307.csv`. Word frequencies over the Sixian texts; texts for reading practice. |
| 客家委員會客語百句 ([data.gov.tw 162998](https://data.gov.tw/dataset/162998)) | 客家委員會 Hakka Affairs Council | [政府資料開放授權條款-第1版](https://data.gov.tw/license) | Committed unaltered as `data/gov/hakka_100_sentences_162998.csv`. Parallel sentences in six accents for the accent switch and early lessons. |
| 客語能力認證詞彙 115年度 and 基礎級暨初級題庫 ([data.gov.tw 176002](https://data.gov.tw/dataset/176002), files from elearning.hakka.gov.tw) | 客家委員會 Hakka Affairs Council | [政府資料開放授權條款-第1版](https://data.gov.tw/license) | Committed unaltered in `data/gov/115/`. Core vocabulary by level, examples, exam-style exercises; five accents. |

Attribution text for Hakka Affairs Council open data: 資料來源：客家委員會（政府資料開放平臺），依政府資料開放授權條款-第1版使用。

Romanisation throughout is the Ministry of Education's 臺灣客家語拼音方案 (2012 revision), Sixian (四縣腔).

## In the app
| Asset | Author | Licence | Use |
|---|---|---|---|
| Noto Sans (`app/fonts/`) | Google, via [@fontsource-variable/noto-sans](https://fontsource.org/fonts/noto-sans) | [SIL OFL 1.1](https://openfontlicense.org) | Embedded in the app for pinyin, with the tone letters ˊ ˇ ˋ. |
| Plangothic | Fitzgerald Wu (@free-fonts/plangothic 1.0.0) | SIL OFL 1.1 | Glyphs of rare characters (𠊎, 𫣆, 𢯭…), subset at build time. |
| Iansui, Noto Sans TC, Atkinson Hyperlegible, Nunito | Google Fonts | SIL OFL 1.1 | Loaded from Google Fonts. |
| Word and example recordings (Hkka-audio `clips/`) | 客家委員會 Hakka Affairs Council | 政府資料開放授權條款-第1版 | Played on word cards and examples. |
| Synthetic voice (Hkka-audio `tts/`) | generated with VoxHakka, `formospeech/yourtts-htia-240704` (United Link, National United University) | [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/), not the course licence | Titles, dialogue lines, exercise answers, new words without a recording. |
| App design and code | adapted from Tsheh-tû (tbrapor-arch/tsehtu) | as this repository | |

## Private, local-only
`HAKKA_PRIVATE=../Hkka-private make db` also loads sentences parsed from the Glossika *Mass Sentences — Hakka
Sixian/Hailu* books (© Glossika, all rights reserved). They stay in your local database. Nothing derived from them
verbatim may be committed to this repository or published with the app.
