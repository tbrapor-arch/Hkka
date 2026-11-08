#!/bin/sh
# Download the open data sources into data/raw at pinned commits.
# Nothing in data/raw is committed to this repo (see .gitignore and ATTRIBUTION.md).
set -e
cd "$(dirname "$0")"
mkdir -p raw
fetch() { # name url commit
  if [ ! -d "raw/$1/.git" ]; then
    git clone --quiet --filter=blob:none "$2" "raw/$1"
  fi
  git -C "raw/$1" fetch --quiet --depth 1 origin "$3" 2>/dev/null || true
  git -C "raw/$1" -c advice.detachedHead=false checkout --quiet "$3"
  echo "ok  $1 @ $(git -C "raw/$1" rev-parse --short HEAD)"
}
# 教育部臺灣客家語常用詞辭典, JSON (CC BY-ND 3.0 TW)
fetch moedict-data-hakka  https://github.com/g0v/moedict-data-hakka.git          c1a28576be319d5e53190d8ba8e969158e86952c
# 客委會 客語能力認證基本詞彙 102年版, merged CSV, all five accents
fetch hakka_elearning     https://github.com/Taiwanese-Corpus/hakka_elearning.git 0a72438deb7d1801e1a2b4239f18c5c34325f371
# HSK word lists (MIT): Mandarin comparison layer (cognate class, HSK level, English for shared words)
fetch complete-hsk-vocabulary https://github.com/drkameleon/complete-hsk-vocabulary.git 7ac65bf1a6387d35f1ade478906172a19311c7f9
# Plangothic (SIL OFL 1.1) webfont chunks: glyphs for Hakka characters (𠊎, 𫣆, 𢯭…) that common Chinese fonts lack.
# tools/build_app.py embeds only the glyphs the app uses.
if [ ! -d raw/plangothic/package ]; then
  mkdir -p raw/plangothic
  (cd raw/plangothic && npm pack @free-fonts/plangothic@1.0.0 --silent >/dev/null && tar xzf free-fonts-plangothic-1.0.0.tgz)
fi
echo "ok  plangothic @ 1.0.0"
