"""把 Syllable 格式化成切韵自动推导器接受的音韵地位字符串。"""

from __future__ import annotations

from ._grade import mc_grade
from ._initials import mc_initials
from ._parser import Syllable
from ._rhyme import mc_rhyme
from ._syllable import coerce_syllable

__all__ = ["mc_position"]


def mc_position(syllable: Syllable) -> str:
    """返回 ``声母 + 开合 + 韵等 + 韵母 + 声调`` 的音韵地位字符串。

    这是 AWs-363 切韵音系自动推导器的括号内格式，例如 ``日開三侵平``。

    Args:
        syllable: ``parse_syllable`` 返回的 :class:`pboc_tanyu.Syllable`。

    Returns:
        音韵地位字符串，如 ``"幫開三A支平"``、``"端合一模平"``。

    Examples:
        >>> from pboc_tanyu import mc_position, parse_syllable
        >>> mc_position(parse_syllable("ta"))
        '章開三魚平'
        >>> mc_position(parse_syllable("tˤa"))
        '端合一模平'
    """
    initial, _, _, _, _, tone, _ = coerce_syllable(syllable)
    open_, rhyme = mc_rhyme(syllable)
    grade = mc_grade(syllable)
    return f"{mc_initials(syllable)}{open_}{grade}{rhyme}{tone}"
