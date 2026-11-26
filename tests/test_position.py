"""``mc_position`` 的单元测试。"""

from __future__ import annotations

from pboc_tanyu import mc_position, parse_syllable


def _s(ipa: str):
    return parse_syllable(ipa)


CASES: list[tuple[str, str]] = [
    ("ta", "章開三魚平"),
    ("tˤa", "端合一模平"),
    ("tˤra", "知開二麻平"),
    ("tˤe", "端開四齊平"),
    ("pe", "幫開三A支平"),
    ("praŋ", "幫開三B庚平"),
    ("pa", "幫合三C虞平"),
    ("lˤəps", "定開四齊去"),
]


def test_cases() -> None:
    for ipa, expected in CASES:
        actual = mc_position(_s(ipa))
        assert actual == expected, f"{ipa!r}: {actual} != {expected}"


def test_format() -> None:
    result = mc_position(_s("ta"))
    assert isinstance(result, str)
    assert result[-1] in "平上去入"
    assert result[1] in {"開", "合"}


def test_only_syllable_accepted() -> None:
    for bad in ["ta", "t", None, 1, b"pa"]:
        try:
            mc_position(bad)  # type: ignore[arg-type]
        except TypeError:
            continue
        raise AssertionError(f"{bad!r} 应当抛出 TypeError")
