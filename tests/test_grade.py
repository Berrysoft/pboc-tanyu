"""``mc_grade`` 的单元测试。"""

from __future__ import annotations

from pboc_tanyu import mc_grade, parse_syllable


def _s(ipa: str):
    return parse_syllable(ipa)


CASES: list[tuple[str, str]] = [
    # 无咽化 -> 三等；三等再分 A/B/C
    ("ta", "三"),
    ("tra", "三"),
    ("tia", "三"),
    ("pe", "三A"),
    ("paj", "三B"),
    ("pre", "三B"),
    ("praj", "三B"),
    ("praŋ", "三B"),
    ("pa", "三C"),
    # 有咽化 + r -> 二等
    ("tˤra", "二"),
    ("tsˤra", "二"),
    # 但韻本身沒有二等時，按韻的實際等第
    ("tˤroh", "三"),   # 晝：尤韻無二等
    ("kˤro", "一"),    # 侯韻無二等
    ("sroŋ", "二"),    # 江韻只有二等，無 ˤ 也不能作三等
    ("tsrok", "二"),   # 入声覺韻也歸江，仍只能二等
    ("ʔwˤah", "一"),  # 咽化 + a，按影一模去
    ("ʔwˤa", "一"),   # 平聲同
    # 有咽化、无 r：e/i/ia -> 四等
    ("tˤe", "四"),
    ("tˤi", "四"),
    ("l̥ˤe", "四"),
    # a/o/u -> 一等
    ("tˤa", "一"),
    ("tˤo", "一"),
    ("tˤu", "一"),
    # ə：锐音 + -j/-n/-t/-s -> 四等
    ("tˤəj", "四"),
    ("tsˤən", "四"),
    ("sˤət", "四"),
    ("lˤəs", "四"),
    # ə：钝音或 -ps 等 -> 一等
    ("pˤəj", "一"),
    ("kˤən", "一"),
    ("tˤəps", "一"),
    ("tˤə", "一"),
    # L 系 *-əps 走 *-its：四等
    ("lˤəps", "四"),
]


def test_cases() -> None:
    for ipa, expected in CASES:
        actual = mc_grade(_s(ipa))
        assert actual == expected, f"{ipa!r}: {actual} != {expected}"


def test_returns_string() -> None:
    allowed = {"一", "二", "三", "三A", "三B", "三C", "四"}
    for ipa in ["ta", "pe", "praŋ", "pa", "tˤa", "tˤra", "tˤe", "lˤəps"]:
        result = mc_grade(_s(ipa))
        assert isinstance(result, str)
        assert result in allowed


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
