#!/usr/bin/env python3
"""Sixian 四縣 tone sandhi (MOE pinyin).

Rule (MOE 客家語拼音學習手冊 四縣腔, lesson 25; 客家語拼音方案使用手冊): inside a tone group, a 陰平 syllable
(ˊ 24) is read 陽平-like ˇ 11 when the next syllable is 陰平 (24), 去聲 (55) or 陽入 (5). Before 陽平 (11),
上聲 (31) or 陰入 (2) it keeps 24. Only the last syllable of a group never changes.

A tone group ends at punctuation, at '|' (explicit break, as in Tsheh-tû's `groups` field) or at the end of the line.
Words are not a boundary: 豬肝盡補 zuˊ gonˊ qin buˋ → zuˇ gonˊ qin buˋ (MOE example).
Spoken Hakka varies (the MOE workbook says so); the course marks the citation tones and shows these as a guide.

  python3 -I tools/sandhi.py "maˇ iuˇ cauˋ zuˊ gonˊ qin buˋ"
"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pinyin as py  # noqa: E402

TRIGGERS = {"24", "55", "5"}


def apply(syllables):
    """[(syl, value)] in one tone group → [(syl, spoken value)]."""
    out = []
    for i, (s, v) in enumerate(syllables):
        nxt = syllables[i + 1][1] if i + 1 < len(syllables) else None
        out.append((s, "11" if v == "24" and nxt in TRIGGERS else v))
    return out


def spoken(text):
    """Line in MOE pinyin (tone marks) → the same line with sandhi tones, keeping spaces and punctuation."""
    result = []
    for group in re.split(r"([|,，.。?？!！;；:：、]+)", text):
        if not group or re.fullmatch(r"[|,，.。?？!！;；:：、]+", group):
            result.append("" if group and set(group) <= {"|"} else group)
            continue
        words = group.split(" ")
        sylls = [py.syllables(w) for w in words]
        flat = apply([x for w in sylls for x in w])
        k, rebuilt = 0, []
        for w in sylls:
            part = flat[k:k + len(w)]; k += len(w)
            rebuilt.append("".join(s + py.MARK_OF_VALUE.get(v or "", "") for s, v in part))
        result.append(" ".join(rebuilt))
    return re.sub(r"\s+", " ", "".join(result)).strip()


def _test():
    cases = {   # MOE Sixian workbook, lesson 25 and front matter
        "aˊ meˊ": "aˇ meˊ", "aˊ poˇ": "aˊ poˇ", "aˊ jiˋ": "aˊ jiˋ", "aˊ tai": "aˇ tai",
        "aˊ bagˋ": "aˊ bagˋ", "vuˊ pag": "vuˇ pag",
        "maˇ iuˇ cauˋ zuˊ gonˊ qin buˋ": "maˇ iuˇ cauˋ zuˇ gonˊ qin buˋ",
        "banˊ maˊ": "banˇ maˊ",
        "cuˊ siib": "cuˇ siib", "suˊ liuˇ": "suˊ liuˇ", "cuˊ samˊ": "cuˇ samˊ", "suˊ abˋ": "suˊ abˋ",
        "zuˊ, gonˊ": "zuˊ, gonˊ", "zuˊ | gonˊ": "zuˊ gonˊ",
    }
    for a, b in cases.items():
        got = spoken(a)
        assert got == b, f"{a!r}: {got!r} != {b!r}"
    print(f"sandhi: ok ({len(cases)} cases)")


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        _test()
    else:
        for a in sys.argv[1:]:
            print(spoken(a))
