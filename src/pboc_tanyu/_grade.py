"""PBOC 音节到切韵等第（一、二、三、四等）的推导。"""

from __future__ import annotations

from ._parser import Syllable
from ._syllable import coerce_syllable

__all__ = ["mc_grade"]

#: 三等以外的前元音：e/i 一律四等。
_FRONT = frozenset({"e", "i", "ia"})

#: 锐音声母。非三等、无 -r- 的 ə 在这些声母后接 -j/-n/-t（或 -s 尾）时归四等，
#: 在钝音声母后则归一等。
_SHARP = frozenset({"t", "tʰ", "d", "n", "ts", "tsʰ", "dz", "s", "l", "l̥", "sl", "r"})


def mc_grade(syllable: Syllable) -> int:
    """返回一条 PBOC 音节对应的切韵等第。

    规则：

    * 没有咽化 ˤ → 三等（带不带 -r- 都是三等）；
    * 有 ˤ、有 -r- → 二等；
    * 有 ˤ、无 -r-：
        - 主元音 e/i/ia → 四等；
        - 主元音 ə 且声母是锐音（t、ts、s、l、r 等），韵尾为 -j/-n/-t
          或去声 -s（不含 -ps）→ 四等；
        - 例外：L 系 l + 非三等 + 无 -r- + -əps 走 *-its，也归四等；
        - 其余（a/o/u/ə，或 ə 在钝音后）→ 一等。

    Args:
        syllable: ``parse_syllable`` 返回的 :class:`pboc_tanyu.Syllable`。

    Returns:
        ``1``、``2``、``3`` 或 ``4``。

    Examples:
        >>> from pboc_tanyu import mc_grade, parse_syllable
        >>> mc_grade(parse_syllable("ta"))
        3
        >>> mc_grade(parse_syllable("tˤa"))
        1
        >>> mc_grade(parse_syllable("tˤra"))
        2
        >>> mc_grade(parse_syllable("tˤe"))
        4
        >>> mc_grade(parse_syllable("tˤəj"))
        4
        >>> mc_grade(parse_syllable("pˤəj"))
        1
    """
    initial, phar, has_r, vowel, coda, _tone, tone_marker = coerce_syllable(syllable)

    if not phar:
        return 3
    if has_r:
        return 2
    if vowel in _FRONT:
        return 4
    # L 系 *-əps 走 *-its 一支：lˤəps > 四等齊。
    # *-əps > *-us 只适用于 T/N/TS，L 是近音，不在此列。
    if initial == "l" and phar and not has_r and vowel == "ə" and tone_marker == "ps":
        return 4
    if (
        vowel == "ə"
        and initial in _SHARP
        and (coda in {"j", "n", "t"} or tone_marker == "s")
    ):
        return 4
    return 1
