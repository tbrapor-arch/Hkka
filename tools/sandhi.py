#!/usr/bin/env python3
"""Sixian 四縣 tone sandhi (MOE pinyin).

Rule (MOE 客家語拼音學習手冊 四縣腔, lesson 25; 客家語拼音方案使用手冊): inside a tone group, a 陰平 syllable
(ˊ 24) is read 陽平-like ˇ 11 when the next syllable is 陰平 (24), 去聲 (55) or 陽入 (5). Before 陽平 (11),
上聲 (31) or 陰入 (2) it keeps 24. Only the last syllable of a group never changes.

A tone group ends at punctuation, at '|' or at the end of the line. Sandhi works inside a phrase, not across a
phrase break: in the MOE example 麻油炒豬肝 | 盡補 ("pig liver fried in sesame oil | is very nourishing"),
豬 zuˊ → zuˇ before 肝 gonˊ, but 肝 keeps ˊ before 盡 qin. So lesson lines mark phrase breaks with '|' in their
`groups` field, as in Tsheh-tû; without '|' the whole clause is one group.
Spoken Hakka varies (the MOE workbook says so); the course marks the citation tones and shows these as a guide.

Hailu 海陸 (MOE article 107_015, part 3): inside a tone group, 上聲 (ˊ 24) is read 陽去 (+ 33) before any tone
(點心 diamˊ → diam+ simˋ), and 陰入 (unmarked, 5) is read 陽入 (ˋ 2) before any tone (菊花 kiug → kiugˋ faˋ). The
article's exceptions (emphasis, numbers 五 and 七 often unchanged, the rising first syllable of AAA) are not applied.

  python3 -I tools/sandhi.py "maˇ iuˇ cauˋ zuˊ gonˊ | qin buˋ"
  python3 -I tools/sandhi.py --hailu "diamˊ simˋ"
"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pinyin as py  # noqa: E402

TRIGGERS = {"24", "55", "5"}
# 仔 suffix forms in Sixian (assimilated to the preceding final: 雞仔 gieˊ eˋ, 豬仔 zuˊ veˋ, 柑仔 gamˊ meˋ …)
ZAI = {"e", "ve", "ie", "me", "ne", "nge", "be", "le", "ge"}


def apply_hailu(syllables):
    """[(syl, value)] in one Hailu tone group → spoken values: 上聲 24 → 33, 陰入 5 → 2, before any syllable."""
    return [(s, "33" if v == "24" and i + 1 < len(syllables) else "2" if v == "5" and i + 1 < len(syllables) else v)
            for i, (s, v) in enumerate(syllables)]


def apply(syllables):
    """[(syl, value)] in one tone group → [(syl, spoken value)].
    Rule 1: 陰平 24 → 11 before 24, 55, 5.  Rule 2 (仔 suffix, MOE article 107_015): 仔 eˋ 31 → eˇ 11 after
    上聲 31 or 陰入 2 (草仔 coˋ eˇ, 鐵仔 tiedˋ leˇ)."""
    out = []
    for i, (s, v) in enumerate(syllables):
        nxt = syllables[i + 1][1] if i + 1 < len(syllables) else None
        prev = syllables[i - 1][1] if i else None
        if v == "24" and nxt in TRIGGERS:
            v = "11"
        elif v == "31" and s in ZAI and prev in ("31", "2"):
            v = "11"
        out.append((s, v))
    return out


def spoken(text, accent="sixian"):
    """Line in MOE pinyin (tone marks) → the same line with sandhi tones, keeping spaces and punctuation."""
    rule = apply_hailu if accent == "hailu" else apply
    marks = py.mark_of_value(accent)
    result = []
    for group in re.split(r"([|,，.。?？!！;；:：、]+)", text):
        if not group or re.fullmatch(r"[|,，.。?？!！;；:：、]+", group):
            result.append("" if group and set(group) <= {"|"} else group)
            continue
        words = group.split(" ")
        sylls = [py.syllables(w, accent) for w in words]
        flat = rule([x for w in sylls for x in w])
        k, rebuilt = 0, []
        for w in sylls:
            part = flat[k:k + len(w)]; k += len(w)
            rebuilt.append("".join(s + marks.get(v or "", "") for s, v in part))
        result.append(" ".join(rebuilt))
    return re.sub(r"\s+", " ", "".join(result)).strip()


def _test():
    cases = {   # MOE Sixian workbook, lesson 25 and front matter
        "aˊ meˊ": "aˇ meˊ", "aˊ poˇ": "aˊ poˇ", "aˊ jiˋ": "aˊ jiˋ", "aˊ tai": "aˇ tai",
        "aˊ bagˋ": "aˊ bagˋ", "vuˊ pag": "vuˇ pag",
        "maˇ iuˇ cauˋ zuˊ gonˊ | qin buˋ": "maˇ iuˇ cauˋ zuˇ gonˊ qin buˋ",
        "banˊ maˊ": "banˇ maˊ",
        "cuˊ siib": "cuˇ siib", "suˊ liuˇ": "suˊ liuˇ", "cuˊ samˊ": "cuˇ samˊ", "suˊ abˋ": "suˊ abˋ",
        "zuˊ, gonˊ": "zuˊ, gonˊ", "zuˊ | gonˊ": "zuˊ gonˊ",
        # MOE article 107_015 (Sixian/Hailu sandhi): 天光 tienˇ gongˊ, 添飯, 三月; 仔 after 上聲 / 陰入
        "tienˊ gongˊ": "tienˇ gongˊ", "tiamˊ fan": "tiamˇ fan", "samˊ ngied": "samˇ ngied",
        "coˋ eˋ": "coˋ eˇ", "tiedˋ leˋ": "tiedˋ leˇ", "banˋ neˋ": "banˋ neˇ", "gieˊ eˋ": "gieˊ eˋ",
        "zuˊ veˋ": "zuˊ veˋ",
    }
    for a, b in cases.items():
        got = spoken(a)
        assert got == b, f"{a!r}: {got!r} != {b!r}"
    hailu = {   # MOE article 107_015, part 3
        "diamˊ simˋ": "diam+ simˋ", "gongˊ gaiˊ": "gong+ gaiˊ", "shiuˊ boiˇ": "shiu+ boiˇ",
        "siauˊ sied": "siau+ sied", "zhimˊ teu": "zhim+ teu", "denˊ lu+": "den+ lu+", "foˊ shidˋ": "fo+ shidˋ",
        "kiug faˋ": "kiugˋ faˋ", "giog daiˊ": "giogˋ daiˊ", "kied foˇ": "kiedˋ foˇ", "fad gog": "fadˋ gog",
        "giog pun": "giogˋ pun", "fab tu+": "fabˋ tu+", "chud ngibˋ": "chudˋ ngibˋ",
        "denˊ, lu+": "denˊ, lu+",
    }
    for a, b in hailu.items():
        got = spoken(a, "hailu")
        assert got == b, f"hailu {a!r}: {got!r} != {b!r}"
    print(f"sandhi: ok ({len(cases)} Sixian, {len(hailu)} Hailu cases)")


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        _test()
    else:
        acc = "hailu" if sys.argv[1:2] == ["--hailu"] else "sixian"
        for a in sys.argv[2 if acc == "hailu" else 1:]:
            print(spoken(a, acc))
