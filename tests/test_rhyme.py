"""``mc_rhyme`` 的单元测试。"""

from __future__ import annotations

from pboc_tanyu import mc_rhyme, parse_syllable


def _s(ipa: str):
    return parse_syllable(ipa)


CASES: list[tuple[str, tuple[str, str]]] = [
    # 三等 no ˤ：魚/虞
    ("ta", ("開", "魚")),
    ("kwa", ("合", "虞")),
    # 一等 ˤ：模、歌、寒、鐸、曷
    ("tˤa", ("合", "模")),
    ("tˤaj", ("開", "歌")),
    ("tˤan", ("開", "寒")),
    ("tˤak", ("開", "鐸")),
    ("tˤat", ("開", "曷")),
    # 合口一等：末、灰
    ("tˤot", ("合", "末")),
    ("tˤəps", ("合", "灰")),
    # 四等：齊
    ("tˤe", ("開", "齊")),
    ("tˤi", ("開", "齊")),
    # 三等：仙、藥、昔
    ("tan", ("開", "仙")),
    ("bak", ("合", "藥")),
    ("l̥ak", ("開", "清")),
    # 去声 -s：泰
    ("tˤas", ("開", "泰")),
    # 入声 -p：合
    ("tˤəp", ("開", "合")),
    # L 系 *-əps：四等開齊
    ("lˤəps", ("開", "齊")),
    # 影母 + i + t：「一」是開口質韻，不是合口術韻
    ("ʔit", ("開", "質")),
    # 《小韻表》wap 行 H 誤作東；《廣韻》饁是云母葉韻入
    ("wap", ("合", "葉")),
    # ʔwˤa / ʔwˤah：ˤ+a 一律模，平聲 H 的虞是例外
    ("ʔwˤa", ("合", "模")),
    ("ʔwˤah", ("合", "模")),
    # 羊系 K
    ("kjoŋ", ("合", "東")),
    ("kjon", ("合", "桓")),
    ("kʰjuʔ", ("開", "豪")),
    ("kjunʔ", ("合", "魂")),
    ("kjəʔ", ("開", "之")),
    # srap 是生三鹽，tsʰrap 的初二咸是不規則讀法
    ("srap", ("開", "葉")),
    ("tsʰrap", ("開", "葉")),
]


def test_cases() -> None:
    for ipa, expected in CASES:
        actual = mc_rhyme(_s(ipa))
        assert actual == expected, f"{ipa!r}: {actual} != {expected}"


def test_return_shape() -> None:
    for ipa, _ in CASES:
        result = mc_rhyme(_s(ipa))
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] in {"開", "合"}
        assert isinstance(result[1], str) and result[1]


def test_only_syllable_accepted() -> None:
    for bad in ["ta", "t", None, 1, b"pa"]:
        try:
            mc_rhyme(bad)  # type: ignore[arg-type]
        except TypeError:
            continue
        raise AssertionError(f"{bad!r} 应当抛出 TypeError")


def test_bad_syllable() -> None:
    good = _s("ta")
    for bad in [
        {},
        {"initial": "t"},
        {key: value for key, value in good.items() if key != "tone_marker"},
        {**good, "tone": "?"},
    ]:
        try:
            mc_rhyme(bad)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        raise AssertionError(f"{bad!r} 应当报错")
