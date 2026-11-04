#!/bin/sh
# Download the Hakka Affairs Council certification material (115年度 = 2026) into reference/gov/115/.
# Run on your own machine: the cloud build machine cannot reach elearning.hakka.gov.tw.
# Source pages (listed in data.gov.tw dataset 176002, 政府資料開放授權條款-第1版):
#   https://elearning.hakka.gov.tw/hakka/download-files?c=2   基礎級暨初級
#   https://elearning.hakka.gov.tw/hakka/download-files?c=3   中級暨中高級
#   https://elearning.hakka.gov.tw/hakka/download-files?c=5   高級
# Usage: sh data/fetch_gov.sh            vocabulary tables (.ods), all five accents
#        sh data/fetch_gov.sh --audio    also the Sixian and Hailu audio zips
#        sh data/fetch_gov.sh --pdf      also the PDF versions and sample tests
# Then commit nothing from reference/: send the .ods files (or a zip of the folder) to the build session.
set -e
cd "$(dirname "$0")/.."
OUT=reference/gov/115
mkdir -p "$OUT"
BASE=https://elearning.hakka.gov.tw/hakka/files/downloads
get() { # id ext name
  f="$OUT/$3.$2"
  if [ -s "$f" ]; then echo "have $f"; return; fi
  curl -fsSL --retry 3 -o "$f" "$BASE/$1.$2" && echo "ok   $f" || { echo "FAIL $BASE/$1.$2"; rm -f "$f"; }
}
AUDIO=0; PDF=0
for a in "$@"; do case "$a" in --audio) AUDIO=1;; --pdf) PDF=1;; esac; done

# --- vocabulary and question banks (.ods) -------------------------------------------------
# accent order on the site: 四縣 海陸 大埔 饒平 詔安
set -- sixian hailu dapu raoping zhaoan
i=0
for acc in "$@"; do
  get $((761 + 6*i)) ods "basic_vocab_$acc"          # 基礎級詞彙
  get $((762 + 6*i)) ods "elementary_vocab_$acc"     # 初級詞彙
  get $((763 + 6*i)) ods "basic_elementary_bank_$acc" # 基礎級暨初級題庫
  get $((736 + 5*i)) ods "intermediate_vocab_$acc"   # 中級詞彙
  get $((737 + 5*i)) ods "upper_intermediate_vocab_$acc" # 中高級詞彙
  i=$((i + 1))
done
get 797 ods advanced_vocab_sixian; get 801 ods advanced_vocab_hailu; get 805 ods advanced_vocab_dapu
get 809 ods advanced_vocab_raoping; get 813 ods advanced_vocab_zhaoan

# --- audio (large) ------------------------------------------------------------------------
if [ $AUDIO = 1 ]; then
  get 766 zip basic_elementary_audio_sixian;  get 772 zip basic_elementary_audio_hailu
  get 740 zip intermediate_audio_sixian;      get 745 zip intermediate_audio_hailu
  get 800 zip advanced_audio_sixian;          get 804 zip advanced_audio_hailu
  get 245 zip corpus_selection_sixian;        get 246 zip corpus_selection_hailu   # 中級暨中高級語料選粹
fi

# --- PDFs and test descriptions -------------------------------------------------------------
if [ $PDF = 1 ]; then
  get 764 pdf basic_elementary_vocab_sixian;  get 765 pdf basic_elementary_bank_sixian
  get 738 pdf intermediate_vocab_sixian_1;    get 739 pdf intermediate_vocab_sixian_2
  get 476 pdf advanced_reading_sample_sixian; get 791 zip advanced_speaking_sample_sixian
  get 481 zip advanced_writing_sample_sixian
  get 52 zip test_standards_basic;            get 134 zip test_standards_intermediate  # 通過標準與題型說明
fi
ls -la "$OUT"
