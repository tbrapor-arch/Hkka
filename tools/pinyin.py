#!/usr/bin/env python3
"""Taiwan MOE Hakka romanisation (臺灣客家語拼音方案, 2012 revision), Sixian 四縣 focus.

Two notations meet in the sources:
  * tone marks, as in textbooks and the certification lists: konˊbangˋua
  * tone values (調值) as numbers, as in the MOE dictionary: kon²⁴bang³¹ua⁵⁵
`key()` turns either into one comparable key: 'kon24-bang31-ua55' (syllables joined by '-').

Sixian tones   陰平 ˊ 24 · 陽平 ˇ 11 · 上聲 ˋ 31 · 去聲 (unmarked) 55 · 陰入 -b/-d/-g + ˋ 2 · 陽入 -b/-d/-g unmarked 5
"""
import re, sys, unicodedata

SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
# Tone marks → tone values per accent (MOE 客家語拼音方案使用手冊, 聲調符號表). (open syllables, checked -b/-d/-g)
TABLES = {
    "sixian":       ({"ˊ": "24", "ˇ": "11", "ˋ": "31", "": "55"}, {"ˋ": "2", "": "5"}),
    "south-sixian": ({"ˊ": "24", "+": "33", "ˇ": "11", "ˋ": "31", "": "55"}, {"ˋ": "2", "": "5"}),
    "hailu":        ({"ˋ": "53", "": "55", "ˊ": "24", "ˇ": "11", "+": "33"}, {"": "5", "ˋ": "2"}),
    # Dapu 去聲 53: unmarked in the MOE dictionary, ˋ in the 115年度 lists. Zhao'an: an entering syllable that lost its
    # stop keeps tone 24 with ˊ (額 ngiaˊ).
    "dapu":         ({"+": "33", "ˊ": "35", "ˇ": "113", "ˆ": "31", "ˋ": "53", "": "53"}, {"ˆ": "21", "ˋ": "54"}),
    "raoping":      ({"ˇ": "11", "": "55", "ˋ": "53", "ˊ": "24"}, {"ˋ": "2", "": "5"}),
    "zhaoan":       ({"ˇ": "11", "ˋ": "53", "ˆ": "31", "ˊ": "24", "": "55"}, {"ˊ": "24", "ˋ": "43"}),
}
MARKS, CHECKED_MARKS = TABLES["sixian"]
TONE_NAMES = {"24": "陰平", "11": "陽平", "31": "上聲", "55": "去聲", "2": "陰入", "5": "陽入"}
MARK_OF_VALUE = {"24": "ˊ", "11": "ˇ", "31": "ˋ", "55": "", "2": "ˋ", "5": ""}


def mark_of_value(accent="sixian"):
    o, c = TABLES[accent]
    out = {v: m for m, v in o.items()}
    out.update({v: m for m, v in c.items()})
    return out

INITIALS = ["ng", "b", "p", "m", "f", "v", "d", "t", "n", "l", "g", "k", "h", "j", "q", "x", "z", "c", "s", "r", ""]
_inventories = {}   # accent → toneless syllables known to be valid (filled from the MOE dictionary by build_db)
_inventory = _inventories.setdefault("sixian", set())


def set_inventory(sylls, accent="sixian"):
    inv = _inventories.setdefault(accent, set())
    inv.clear(); inv.update(sylls)


def is_checked(syl):
    return syl[-1:] in ("b", "d", "g") and not syl.endswith("ng")


def _split_unmarked(chunk, accent="sixian"):
    """Split a run of letters with no tone marks into syllables, using the inventory (longest match, DP)."""
    _inventory = _inventories.get(accent, set())
    if not chunk or not _inventory or chunk in _inventory:
        return [chunk] if chunk else []
    n = len(chunk); best = [None] * (n + 1); best[0] = []
    for i in range(n):
        if best[i] is None:
            continue
        for j in range(n, i, -1):
            if chunk[i:j] in _inventory and (best[j] is None or len(best[j]) > len(best[i]) + 1):
                best[j] = best[i] + [chunk[i:j]]
    return best[n] or [chunk]


def syllables(s, accent="sixian"):
    """'konˊbangˋua' or 'kon²⁴bang³¹ua⁵⁵' → [('kon','24'), ('bang','31'), ('ua','55')]. Unknown tone → None."""
    s = unicodedata.normalize("NFC", s).lower().translate(SUP).replace("^", "ˆ").replace("＋", "+")
    opens, checks = TABLES[accent]
    out = []
    for word in re.split(r"[\s\-–,，.。?？!！、;；:：'’\"“”()（）\[\]【】/|]+", s):
        if not word:
            continue
        if re.search(r"\d", word):                                  # numeric tone values
            for syl, val in re.findall(r"([a-z]+)(\d+)", word):
                out.append((syl, val))
            continue
        for chunk, mark in re.findall(r"([a-z]+)([ˊˇˋˆ+]?)", word):
            parts = _split_unmarked(chunk, accent)
            for p in parts[:-1]:
                out.append((p, (checks if is_checked(p) else opens).get("")))
            last = parts[-1]
            table = checks if is_checked(last) else opens
            out.append((last, table.get(mark)))
    return out


def key(s, accent="sixian"):
    return "-".join(f"{a}{b or ''}" for a, b in syllables(s, accent))


def toneless(s, accent="sixian"):
    return "-".join(a for a, _ in syllables(s, accent))


def marked(s, accent="sixian"):
    """Any notation → tone-mark spelling, syllables joined: 'kon²⁴bang³¹ua⁵⁵' → 'konˊbangˋua'."""
    mv = mark_of_value(accent)
    return "".join(a + mv.get(b or "", "") for a, b in syllables(s, accent))


def _test():
    set_inventory({"kon", "bang", "ua", "ji", "id", "ngien", "teu", "tien", "o", "hai", "io", "ma", "ga", "ge"})
    assert key("konˊbangˋua") == "kon24-bang31-ua55", key("konˊbangˋua")
    assert key("kon²⁴bang³¹ua⁵⁵") == "kon24-bang31-ua55"
    assert key("idˋji bangˋ") == "id2-ji55-bang31"
    assert key("id²ngien¹¹teu⁵⁵tien²⁴") == key("idˋngienˇteu tienˊ")
    assert marked("id²ngien¹¹teu⁵⁵tien²⁴") == "idˋngienˇteutienˊ"
    assert key("oˇhai io") == "o11-hai55-io55"
    # Hailu: 今晡日 gimˋ buˋ ngid (53 53 5), 食 shidˋ (2), 陽去 +33
    assert key("gimˋ buˋ ngid", "hailu") == "gim53-bu53-ngid5", key("gimˋ buˋ ngid", "hailu")
    assert key("shidˋ", "hailu") == "shid2" and key("tai+ gaˋ", "hailu") == "tai33-ga53"
    assert key("gim⁵³bu⁵³ngid⁵", "hailu") == "gim53-bu53-ngid5"
    assert marked("gim⁵³bu⁵³ngid⁵", "hailu") == "gimˋbuˋngid"
    assert key("ngaiˇ | gimˊ", "sixian") == "ngai11-gim24"
    print("pinyin: ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        _test()
    else:
        for a in sys.argv[1:]:
            print(a, "→", key(a), " ".join(f"{s}{TONE_NAMES.get(v or '', '?')}" for s, v in syllables(a)))
