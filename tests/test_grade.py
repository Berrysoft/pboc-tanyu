"""``mc_grade`` 的单元测试。"""

from __future__ import annotations

from pboc_tanyu import mc_grade, parse_syllable


def _s(ipa: str):
    return parse_syllable(ipa)


CASES: list[tuple[str, int]] = [
    # 无咽化 -> 三等（带不带 -r- 都是）
    ("ta", 3),
    ("tra", 3),
    ("tia", 3),
    # 有咽化 + r -> 二等
    ("tˤra", 2),
    ("tsˤra", 2),
    ("kˤro", 2),  # 规则值；侯部是例外
    # 有咽化、无 r：e/i/ia -> 四等
    ("tˤe", 4),
    ("tˤi", 4),
    ("l̥ˤe", 4),
    # a/o/u -> 一等
    ("tˤa", 1),
    ("tˤo", 1),
    ("tˤu", 1),
    # ə：锐音 + -j/-n/-t/-s -> 四等
    ("tˤəj", 4),
    ("tsˤən", 4),
    ("sˤət", 4),
    ("lˤəs", 4),
    # ə：钝音或 -ps 等 -> 一等
    ("pˤəj", 1),
    ("kˤən", 1),
    ("tˤəps", 1),
    ("tˤə", 1),
    # L 系 *-əps 走 *-its：四等
    ("lˤəps", 4),
]


def test_cases() -> None:
    for ipa, expected in CASES:
        actual = mc_grade(_s(ipa))
        assert actual == expected, f"{ipa!r}: {actual} != {expected}"


def test_returns_int_in_range() -> None:
    for ipa in ["ta", "tˤa", "tˤra", "tˤe", "tˤəj"]:
        result = mc_grade(_s(ipa))
        assert isinstance(result, int)
        assert 1 <= result <= 4


def test_only_syllable_accepted() -> None:
    for bad in ["ta", "t", None, 1, b"pa"]:
        try:
            mc_grade(bad)  # type: ignore[arg-type]
        except TypeError:
            continue
        raise AssertionError(f"{bad!r} 应当抛出 TypeError")


def test_bad_syllable() -> None:
    good = _s("ta")
    for bad in [
        {},
        {"initial": "t"},
        {key: value for key, value in good.items() if key != "tone"},
        {**good, "tone": "?"},
    ]:
        try:
            mc_grade(bad)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        raise AssertionError(f"{bad!r} 应当报错")
