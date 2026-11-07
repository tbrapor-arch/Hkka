# make data      download open sources (data/raw)
# make db        build data/build/hakka.db and data/build/sixian_core.csv
#                HAKKA_PRIVATE=../Hkka-private make db  also loads the private Glossika sentences (local only)
# make lookup W=今晡日
# make sources  render docs/sources.yaml → docs/sources.md
# make lint      check the lessons; make coverage  what is taught, what comes next
PY = python3 -I
RAW = data/raw
OUT = data/build

.PHONY: data db lookup clean test sources lint coverage
data:
	sh data/fetch.sh

db: data
	mkdir -p $(OUT)
	$(PY) tools/build_db.py $(RAW) $(OUT)/hakka.db
	$(PY) tools/export.py $(OUT)/hakka.db $(OUT)/sixian_core.csv

lookup:
	$(PY) tools/lookup.py $(OUT)/hakka.db "$(W)"

test:
	$(PY) tools/pinyin.py --test
	$(PY) tools/sandhi.py --test

clean:
	rm -rf $(OUT)

sources:
	$(PY) tools/sources_md.py

lint:
	$(PY) tools/lint.py

coverage:
	$(PY) tools/coverage.py
