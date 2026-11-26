"""``parse_syllable`` 的单元测试。

不依赖 pytest 的高级特性，因此也可以用 ``python -m pytest`` 或
一个极简的 runner 直接调用。
"""

from __future__ import annotations

from pboc_tanyu import parse_syllable


def _expected(
    initial: str,
    pharyngealized: bool,
    has_r: bool,
    vowel: str,
    coda: str,
    tone: str,
    tone_marker: str,
) -> dict[str, object]:
    return {
        "initial": initial,
        "pharyngealized": pharyngealized,
        "has_r": has_r,
        "vowel": vowel,
        "coda": coda,
        "tone": tone,
        "tone_marker": tone_marker,
    }


CASES: list[tuple[str, dict[str, object]]] = [
    # 咽化 × -r- 的四种组合
    ("pa", _expected("p", False, False, "a", "", "平", "")),
    ("pra", _expected("p", False, True, "a", "", "平", "")),
    ("pˤa", _expected("p", True, False, "a", "", "平", "")),
    ("pˤra", _expected("p", True, True, "a", "", "平", "")),
    # 声调
    ("paʔ", _expected("p", False, False, "a", "", "上", "ʔ")),
    ("pah", _expected("p", False, False, "a", "", "去", "h")),
    ("pas", _expected("p", False, False, "a", "", "去", "s")),
    ("pəps", _expected("p", False, False, "ə", "", "去", "ps")),
    ("pak", _expected("p", False, False, "a", "k", "入", "")),
    ("paŋ", _expected("p", False, False, "a", "ŋ", "平", "")),
    # 韵尾
    ("tawk", _expected("t", False, False, "a", "wk", "入", "")),
    ("pakʷ", _expected("p", False, False, "a", "wk", "入", "")),
    ("ʔaj", _expected("ʔ", False, False, "a", "j", "平", "")),
    ("ʔar", _expected("ʔ", False, False, "a", "r", "平", "")),
    # 各种声母写法
    ("tʰˤaŋ", _expected("tʰ", True, False, "a", "ŋ", "平", "")),
    ("da", _expected("d", False, False, "a", "", "平", "")),
    ("kʰja", _expected("kʰj", False, False, "a", "", "平", "")),
    ("n̥a", _expected("n̥", False, False, "a", "", "平", "")),
    ("ŋ̊a", _expected("ŋ̊", False, False, "a", "", "平", "")),
    ("ʔwa", _expected("ʔw", False, False, "a", "", "平", "")),
    ("m̥a", _expected("m̥", False, False, "a", "", "平", "")),
    ("stia", _expected("st", False, False, "ia", "", "平", "")),
    ("liaʔ", _expected("l", False, False, "ia", "", "上", "ʔ")),
    # 生母是 s + r，而不是一个独立的声母
    ("sra", _expected("s", False, True, "a", "", "平", "")),
    ("sˤra", _expected("s", True, True, "a", "", "平", "")),
    # C.r 是一个整体符号
    ("C.rˤa", _expected("C.r", True, False, "a", "", "平", "")),
    ("C.ra", _expected("C.r", False, False, "a", "", "平", "")),
    # 咽化的严格写法：组合符号 ◌̙
    ("pa\u0319", _expected("p", True, False, "a", "", "平", "")),
    ("p\u0319a", _expected("p", True, False, "a", "", "平", "")),
]


def test_parse_cases() -> None:
    for ipa, expected in CASES:
        actual = parse_syllable(ipa)
        assert actual == expected, f"{ipa!r}: {actual} != {expected}"


def test_tone_marker_is_preserved() -> None:
    assert parse_syllable("pah")["tone_marker"] == "h"
    assert parse_syllable("pas")["tone_marker"] == "s"
    assert parse_syllable("pəps")["tone_marker"] == "ps"
    assert parse_syllable("paʔ")["tone_marker"] == "ʔ"
    assert parse_syllable("pa")["tone_marker"] == ""
    assert parse_syllable("pak")["tone_marker"] == ""


def test_invalid_inputs() -> None:
    for bad in ["", "   ", "xyz", "a", "p", "paq", "pa-", "pá", "pˤ", "pakʔ"]:
        try:
            parse_syllable(bad)
        except ValueError:
            continue
        raise AssertionError(f"{bad!r} 应当抛出 ValueError")


def test_non_string_input() -> None:
    for bad in [None, 1, b"pa", ["p", "a"]]:
        try:
            parse_syllable(bad)  # type: ignore[arg-type]
        except TypeError:
            continue
        raise AssertionError(f"{bad!r} 应当抛出 TypeError")
