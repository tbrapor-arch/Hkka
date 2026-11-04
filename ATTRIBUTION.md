# Data sources and attribution

None of these datasets are stored in this repository. `make data` downloads them at pinned commits into
`data/raw/` (git-ignored), and `make db` builds `data/build/hakka.db` locally. The full catalogue of documentation,
including material that is only used as reference, is `docs/sources.md`.

| Dataset | Rights holder / maintainer | Licence | How it is used |
|---|---|---|---|
| 教育部臺灣客家語常用詞辭典 | Ministry of Education, Taiwan (中華民國教育部). Data via [g0v/moedict-data-hakka](https://github.com/g0v/moedict-data-hakka) (conversion CC0, Audrey Tang and Pierre Magistry) | [CC BY-ND 3.0 TW](https://creativecommons.org/licenses/by-nd/3.0/tw/) | Characters, six-accent readings, definitions and example sentences. Entries and sentences are reproduced unaltered; lessons are written independently. The 華語對照表 (Mandarin comparison table) is not under this licence and is not used. |
| 客語能力認證基本詞彙 (102年版) | 客家委員會 Hakka Affairs Council. Merged CSV via [Taiwanese-Corpus/hakka_elearning](https://github.com/Taiwanese-Corpus/hakka_elearning) | Government work; the Council now publishes the certification vocabulary as open data under the [政府資料開放授權條款-第1版](https://data.gov.tw/license) | Core vocabulary by level and theme, English and Mandarin glosses, example sentences. |

Attribution text for Hakka Affairs Council open data: 資料來源：客家委員會（政府資料開放平臺），依政府資料開放授權條款-第1版使用。

Romanisation throughout is the Ministry of Education's 臺灣客家語拼音方案 (2012 revision), Sixian (四縣腔).

## Private, local-only
`HAKKA_PRIVATE=../hakka-private make db` also loads sentences parsed from the Glossika *Mass Sentences — Hakka
Sixian/Hailu* books (© Glossika, all rights reserved). They stay in your local database. Nothing derived from them
verbatim may be committed to this repository or published with the app.
