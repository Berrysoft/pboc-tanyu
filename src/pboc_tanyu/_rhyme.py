"""PBOC 音节到切韵开合与韵的推导。

开合和韵分开：

* ``BASE_OPEN[(vowel, coda)]``：四个 ``(ˤ, -r-)`` 槽的开口韵，每槽一个字符；
* ``BASE_CLOSED[(vowel, coda)]``：四个 ``(ˤ, -r-)`` 槽的合口韵；
* ``OPEN_SET``：开合规则表中较少的一侧，``OPEN_DEFAULT`` 是默认值；
* ``OVERRIDES``：声母类型和特例修正。

韵表按“有效韵尾”索引：去声的 ``-s`` / ``-ps`` 记为 ``"s"``，其余仍用
IPA 韵尾。槽内 ``?`` 表示该开合下没有合法韵目；若只有一侧有韵，开合由
该侧直接确定；两侧都有时才查 ``OPEN_SET`` / ``CLOSED_SET``。
"""

from __future__ import annotations

from ._groups import rhyme_group
from ._initials import mc_initials
from ._parser import Syllable
from ._rhyme_rules import A_SCHWA_OPEN, BASE_CLOSED, BASE_OPEN, CONSONANT_OPEN, OVERRIDES
from ._syllable import coerce_syllable

__all__ = ["mc_rhyme"]


def mc_rhyme(syllable: Syllable) -> tuple[str, str]:
    """返回一条 PBOC 音节的切韵开合与韵。

    Args:
        syllable: ``parse_syllable`` 返回的 :class:`pboc_tanyu.Syllable`。

    Returns:
        ``(开合, 韵)``，开合为 ``"開"`` 或 ``"合"``，韵为切韵韵目。
        平/上/去声用平声韵目；入声用入声韵目；寒合作桓、歌合作戈、真合作諄。

    Raises:
        TypeError: 参数不是 Syllable，或字段类型不对。
        ValueError: 字典缺键、声调不合法，或该音节无法套用规则。

    Examples:
        >>> from pboc_tanyu import mc_rhyme, parse_syllable
        >>> mc_rhyme(parse_syllable("tˤa"))
        ('合', '模')
        >>> mc_rhyme(parse_syllable("ta"))
        ('開', '魚')
        >>> mc_rhyme(parse_syllable("tˤe"))
        ('開', '齊')
        >>> mc_rhyme(parse_syllable("kwa"))
        ('合', '虞')
    """
    initial, phar, has_r, vowel, coda, _tone, marker = coerce_syllable(syllable)

    # L 系 *-əps 走 *-its 一支：lˤəps > 四等開齊。
    if initial == "l" and phar and not has_r and vowel == "ə" and coda == "" and marker == "ps":
        return ("開", "齊")

    effective_coda = "s" if marker in {"s", "ps"} else coda

    group = rhyme_group(initial, mc_initials(syllable))
    if group is None:
        raise ValueError(f"无法归类的声母：{initial!r}")

    flips = (int(phar), int(has_r), effective_coda)
    outcome = OVERRIDES.get(vowel, {}).get(flips + (group,))
    if outcome is not None:
        return outcome

    idx = 2 * int(phar) + int(has_r)
    open_char = BASE_OPEN.get((vowel, effective_coda), "????")[idx]
    closed_char = BASE_CLOSED.get((vowel, effective_coda), "????")[idx]

    # 只有一侧有韵时，开合由该侧直接确定；两侧都没有就返回问号。
    if open_char == "?" and closed_char == "?":
        return ("?", "?")
    if open_char == "?":
        return ("合", closed_char)
    if closed_char == "?":
        return ("開", open_char)

    if vowel in {"i", "e"}:
        open_ = "合" if initial in CONSONANT_OPEN else "開"
    elif vowel in {"a", "ə"}:
        open_ = "合" if initial in A_SCHWA_OPEN else "開"
    elif vowel in {"o", "u"}:
        open_ = "合"
    else:
        open_ = "開"
    return (open_, open_char if open_ == "開" else closed_char)
