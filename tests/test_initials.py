"""``mc_initials`` 的单元测试。"""

from __future__ import annotations

from pboc_tanyu import mc_initials, parse_syllable
from pboc_tanyu._initials import _MC_INITIALS


def _s(ipa: str):
    return parse_syllable(ipa)


CASES: list[tuple[str, str]] = [
    # T 系：*t' > 端，*tr > 知，*t > 章
    ("tˤa", "端"),
    ("ta", "章"),
    ("tra", "知"),
    ("tˤra", "知"),
    ("tʰa", "昌"),
    ("tʰˤa", "透"),
    ("tʰra", "徹"),
    ("da", "常"),
    ("dˤa", "定"),
    ("dra", "澄"),
    # TS / S 系
    ("tsa", "精"),
    ("tsra", "莊"),
    ("sa", "心"),
    ("sra", "生"),
    # N / L 系
    ("na", "日"),
    ("nˤa", "泥"),
    ("nra", "孃"),
    ("la", "以"),
    ("lˤa", "定"),
    ("lra", "澄"),
    # K 系颚化：前元音 e/i/ia 三等 -> 章、常、書、日
    ("ka", "見"),
    ("ke", "章"),
    ("ki", "章"),
    ("ket", "章"),
    ("keŋh", "章"),
    ("kiw", "見"),
    ("ga", "羣"),
    ("ge", "常"),
    ("geh", "常"),
    ("gin", "常"),
    ("gip", "常"),
    ("gˤa", "匣"),
    ("ŋa", "疑"),
    ("ŋe", "日"),
    ("ŋes", "日"),
    ("ha", "曉"),
    ("hi", "書"),
    # W 系
    ("wa", "云"),
    ("wˤa", "匣"),
    ("wra", "云"),
    ("we", "以"),
    ("wes", "邪"),
    # 清响音：东部方言 + 元音/韵尾/声调
    ("l̥a", "書"),
    ("l̥ˤa", "透"),
    ("l̥ra", "徹"),
    ("n̥a", "心"),
    ("n̥ah", "書"),
    ("n̥am", "書"),
    ("n̥e", "心"),
    ("n̥ep", "書"),
    ("n̥ˤa", "透"),
    ("n̥ra", "徹"),
    ("r̥a", "徹"),
    ("r̥ˤa", "徹"),
    ("r̥ˤi", "透"),
    ("ŋ̊a", "曉"),
    ("ŋ̊e", "書"),
    ("ŋ̊ra", "生"),
    ("ŋ̊ˤranh", "生"),
    ("ŋ̊ˤrum", "透"),
    ("ẘa", "曉"),
    ("ẘar", "心"),
    ("ẘas", "心"),
    ("ẘes", "心"),
    ("ẘəs", "曉"),
    # sl：ia 上声心、去声邪；其余前元音心
    ("sla", "邪"),
    ("sle", "心"),
    ("slˤa", "心"),
    ("sliaʔ", "心"),
    ("sliah", "邪"),
    # ml / mj：之部平上 -> 俟
    ("mla", "船"),
    ("mlə", "俟"),
    ("mjəʔ", "俟"),
    # j̊：-ŋ/-k 及 -unh 归曉
    ("j̊ia", "昌"),
    ("j̊əŋ", "曉"),
    ("j̊uk", "曉"),
    ("j̊un", "昌"),
    ("j̊unh", "曉"),
    # 单值声母
    ("pa", "幫"),
    ("pʰa", "滂"),
    ("ba", "並"),
    ("ma", "明"),
    ("m̥a", "曉"),
    ("ra", "來"),
    ("ja", "以"),
    ("sta", "書"),
    ("sja", "邪"),
    ("ʔa", "影"),
]


def test_cases() -> None:
    for ipa, expected in CASES:
        actual = mc_initials(_s(ipa))
        assert actual == expected, f"{ipa!r}: {actual} != {expected}"


def test_returns_single_string() -> None:
    for ipa in ["ta", "ke", "ŋe", "l̥a", "sla", "mlə"]:
        result = mc_initials(_s(ipa))
        assert isinstance(result, str)
        assert len(result) == 1


def test_only_syllable_accepted() -> None:
    for bad in ["ta", "t", "p", None, 1, b"pa"]:
        try:
            mc_initials(bad)  # type: ignore[arg-type]
        except TypeError:
            continue
        raise AssertionError(f"{bad!r} 应当抛出 TypeError")


def test_bad_syllable() -> None:
    good = _s("ta")
    bad_cases = [
        {},
        {"initial": "t"},
        {key: value for key, value in good.items() if key != "tone_marker"},
        {**good, "tone": "?"},
        {**good, "initial": 1},
    ]
    for bad in bad_cases:
        try:
            mc_initials(bad)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        raise AssertionError(f"{bad!r} 应当报错")


def test_coarse_table_is_wellformed() -> None:
    """粗对照表仍保留作参考，检查其格式。"""
    for initial, initials in _MC_INITIALS.items():
        assert initials, initial
        assert len(set(initials)) == len(initials), f"{initial}: 有重复"
        for char in initials:
            assert "\u4e00" <= char <= "\u9fff", f"{initial}: {char!r} 不是汉字"
