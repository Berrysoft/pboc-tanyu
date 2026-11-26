"""把一条 PBOC 拟音切成声母、咽化、-r-、主元音、韵尾和声调。

PBOC（“基于文献的上古汉语”）的拟音形如 ``pˤrak``，可以按固定顺序切成：

.. code-block:: text

    声母 + 咽化 ˤ + -r- + 主元音 + 韵尾 + 声调

声调在 IPA 里由韵尾后的标记表示：

* 平声：无标记；
* 上声：``ʔ``（喉塞尾）；
* 去声：``h``（来自 *-ks）、``s``（来自 *-ts / *-ps）、``ps``（只出现在 ``əps``）；
* 入声：无标记，由 ``p`` / ``t`` / ``k`` / ``wk`` 韵尾判断。
"""

from __future__ import annotations

import unicodedata
from typing import Literal, TypedDict

__all__ = ["Syllable", "parse_syllable"]

Tone = Literal["平", "上", "去", "入"]


class Syllable(TypedDict):
    """:func:`parse_syllable` 返回的字典结构。

    Attributes:
        initial: 声母的 IPA 写法，例如 ``"pʰ"``、``"n̥"``、``"C.r"``。
        pharyngealized: 是否咽化（非三等），即拟音里是否带 ``ˤ``
            （或等价的 RTR 记号 ``◌̙``）。
        has_r: 声母后是否带 -r- 介音。
        vowel: 主元音，例如 ``"a"``、``"ə"``、``"ia"``。
        coda: 韵尾；开音节为空串，入声为 ``p``/``t``/``k``/``wk``。
        tone: 平、上、去、入。
        tone_marker: 声调的原始 IPA 标记：平声与入声为空串，
            上声为 ``"ʔ"``，去声为 ``"h"``、``"s"`` 或 ``"ps"``。
    """

    initial: str
    pharyngealized: bool
    has_r: bool
    vowel: str
    coda: str
    tone: Tone
    tone_marker: str


# PBOC 声母（与《音節表》第 3 行一致，共 42 个）。
#
# 注意：《音節表》第 3 行把生母写作 "sr"，但那是 "s" 与三等 -r- 的合写，
# 实际拟音（如 "sra"）按 "s" + r 切分，因此这里不列 "sr"。
_INITIALS: tuple[str, ...] = (
    # P 系
    "p",
    "pʰ",
    "b",
    "m",
    "m̥",
    # T 系
    "t",
    "st",
    "tʰ",
    "d",
    "n",
    "n̥",
    # TS 系
    "ts",
    "tsʰ",
    "dz",
    "s",
    # L 系
    "l",
    "l̥",
    "sl",
    "ml",
    # R 系
    "r",
    "r̥",
    "C.r",
    # J 系
    "j",
    "j̊",
    "kj",
    "kʰj",
    "mj",
    "sj",
    # K 系
    "k",
    "kʰ",
    "g",
    "ŋ",
    "ŋ̊",
    "h",
    # KW 系
    "kw",
    "kʰw",
    "gw",
    "ŋw",
    # W 系
    "w",
    "ẘ",
    # Q 系
    "ʔ",
    "ʔw",
)

# 长音先匹配，避免 "n̥" 被切成 "n"、"kʰj" 被切成 "kʰ"。
_INITIALS_BY_LENGTH: tuple[str, ...] = tuple(sorted(_INITIALS, key=len, reverse=True))

# "ia" 必须排在 "i" 前面。
_VOWELS: tuple[str, ...] = ("ia", "a", "e", "i", "o", "u", "ə")

# 韵尾。"kʷ" 只是 "wk" 的另一种写法，输出时统一规范成 "wk"。
_CODAS: tuple[str, ...] = ("wk", "kʷ", "j", "w", "r", "m", "n", "ŋ", "p", "t", "k")

# 入声韵尾。
_STOP_CODAS = frozenset({"p", "t", "k", "wk"})

# 声调标记。"ps" 必须排在 "s" 前面。
_TONE_MARKERS: tuple[str, ...] = ("ps", "ʔ", "h", "s")

_RTR = "\u0319"  # COMBINING RIGHT HALF RING BELOW，即 ˤ 的严格写法。


def parse_syllable(ipa: str) -> Syllable:
    """把一条 PBOC 的 IPA 拟音拆成六个部分。

    Args:
        ipa: PBOC 拟音，例如 ``"pˤrak"``、``"sra"``、``"C.rˤa"``。
            允许带咽化记号 ``ˤ`` 或其等价写法 ``◌̙``；声调标记可省略
            （省略时按平声处理，入声仍由韵尾判断）。

    Returns:
        一个字典，键为 ``initial``、``pharyngealized``、``has_r``、
        ``vowel``、``coda``、``tone``、``tone_marker``。

    Raises:
        TypeError: ``ipa`` 不是字符串。
        ValueError: 输入不是可识别的 PBOC 拟音。

    Examples:
        >>> parsed = parse_syllable("pˤrak")
        >>> parsed["initial"], parsed["pharyngealized"], parsed["has_r"]
        ('p', True, True)
        >>> parsed["vowel"], parsed["coda"], parsed["tone"]
        ('a', 'k', '入')
        >>> parse_syllable("pah")["tone_marker"]
        'h'
    """
    if not isinstance(ipa, str):
        raise TypeError(f"ipa 必须是 str，而不是 {type(ipa).__name__}")

    text = unicodedata.normalize("NFC", ipa).strip()
    if not text:
        raise ValueError("拟音不能为空字符串")

    # 咽化记号可以出现在声母后（ˤa）或写在元音上（a̙），统一先摘掉。
    pharyngealized = "ˤ" in text or _RTR in text
    if pharyngealized:
        text = text.replace("ˤ", "").replace(_RTR, "")

    initial = next(
        (candidate for candidate in _INITIALS_BY_LENGTH if text.startswith(candidate)),
        None,
    )
    if initial is None:
        raise ValueError(f"无法从 {ipa!r} 中识别出 PBOC 声母")

    rest = text[len(initial) :]

    has_r = rest.startswith("r")
    if has_r:
        rest = rest[1:]

    vowel = next((candidate for candidate in _VOWELS if rest.startswith(candidate)), None)
    if vowel is None:
        raise ValueError(f"无法从 {ipa!r} 中识别出主元音（剩余 {rest!r}）")
    rest = rest[len(vowel) :]

    tone_marker = ""
    for marker in _TONE_MARKERS:
        if rest.endswith(marker):
            tone_marker = marker
            rest = rest[: -len(marker)]
            break

    coda = ""
    for candidate in _CODAS:
        if rest.endswith(candidate):
            coda = candidate
            rest = rest[: -len(candidate)]
            break

    if rest:
        raise ValueError(f"{ipa!r} 的韵尾无法识别（剩余 {rest!r}）")

    if coda == "kʷ":
        coda = "wk"

    if tone_marker and coda in _STOP_CODAS:
        raise ValueError(f"{ipa!r} 同时带有入声韵尾和 {tone_marker!r} 声调标记")

    if tone_marker == "ʔ":
        tone: Tone = "上"
    elif tone_marker in {"h", "s", "ps"}:
        tone = "去"
    elif coda in _STOP_CODAS:
        tone = "入"
    else:
        tone = "平"

    result: Syllable = {
        "initial": initial,
        "pharyngealized": pharyngealized,
        "has_r": has_r,
        "vowel": vowel,
        "coda": coda,
        "tone": tone,
        "tone_marker": tone_marker,
    }
    return result
