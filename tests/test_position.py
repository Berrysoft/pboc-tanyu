"""``mc_position`` 的单元测试。"""

from __future__ import annotations

from pboc_tanyu import mc_position, parse_syllable


def _s(ipa: str):
    return parse_syllable(ipa)


CASES: list[tuple[str, str]] = [
    # 唇音：不写呼
    ("pe", "幫三A支平"),
    ("praŋ", "幫三B庚平"),
    ("pa", "幫三C虞平"),
    ("bˤəŋ", "並一登平"),
    # 開合中立韻：不写呼
    ("tˤa", "端一模平"),
    ("ta", "章開三魚平"),  # 魚是僅開口韻，非唇音要写開
    # 分開合韻：写開/合
    ("tˤra", "知開二麻平"),
    ("tˤe", "端開四齊平"),
    ("lˤəps", "定開四齊去"),
    ("tˤak", "端開一唐入"),
    ("tˤot", "端合一寒入"),
    ("nən", "日開三真平"),
    ("nun", "日合三真平"),
    ("ŋwat", "疑合三C元入"),
    ("kwaŋ", "見合三C陽平"),
    ("gˤəŋ", "匣合一登平"),
    # 僅開口韻
    ("nəm", "日開三侵平"),
    ("tˤəp", "端開一覃入"),
    # 僅合口韻
    ("kwa", "見合三C虞平"),
    ("tˤəps", "端合一灰去"),
]


def test_cases() -> None:
    for ipa, expected in CASES:
        actual = mc_position(_s(ipa))
        assert actual == expected, f"{ipa!r}: {actual} != {expected}"


def test_format() -> None:
    result = mc_position(_s("ta"))
    assert isinstance(result, str)
    assert result[-1] in "平上去入"
    assert "開" in result
    assert "三" in result


def test_only_syllable_accepted() -> None:
    for bad in ["ta", "t", None, 1, b"pa"]:
        try:
            mc_position(bad)  # type: ignore[arg-type]
        except TypeError:
            continue
        raise AssertionError(f"{bad!r} 应当抛出 TypeError")
