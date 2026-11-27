"""PBOC 音节到切韵开合与韵的推导。

开合和韵分开：

* ``BASE_OPEN[(vowel, coda)]``：四个 ``(ˤ, -r-)`` 槽的开口韵，每槽一个字符；
* ``BASE_CLOSED[(vowel, coda)]``：四个 ``(ˤ, -r-)`` 槽的合口韵；
* ``OPEN_SET``：开合规则表中较少的一侧，``OPEN_DEFAULT`` 是默认值；
* ``OVERRIDES``：声母类型和特例修正。

韵表按“有效韵尾”索引：去声的 ``-s`` 记为 ``"s"``，其余仍用 IPA 韵尾。槽内 ``?`` 表示该开合下没有合法韵目；若只有一侧有韵，开合由
该侧直接确定；两侧都有时才查 ``OPEN_SET`` / ``CLOSED_SET``。
"""

from __future__ import annotations

from ._groups import rhyme_group
from ._initials import mc_initials
from ._parser import Syllable
from ._rhyme_rules import (
    A_SCHWA_OPEN,
    BASE_CLOSED,
    BASE_OPEN,
    BOD_CLOSED_RIMES,
    BOD_CODAS,
    BOD_INITIALS,
    CONSONANT_OPEN,
    O_U_OPEN_RIMES,
    O_U_VOWELS,
    OVERRIDES,
)
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

    effective_coda = "s" if marker == "s" else coda

    group = rhyme_group(initial, mc_initials(syllable))
    if group is None:
        raise ValueError(f"无法归类的声母：{initial!r}")

    flips = (int(phar), int(has_r), effective_coda)
    idx = 2 * int(phar) + int(has_r)
    open_char = BASE_OPEN.get((vowel, effective_coda), "????")[idx]
    closed_char = BASE_CLOSED.get((vowel, effective_coda), "????")[idx]

    # 只有一侧有韵时，开合由该侧直接确定。
    if open_char == "?" and closed_char == "?":
        rhyme = OVERRIDES.get(vowel, {}).get(flips + (group,), "?")
        return ("?", rhyme) if rhyme != "?" else ("?", "?")
    if open_char == "?":
        open_, base_rhyme = "合", closed_char
    elif closed_char == "?":
        open_, base_rhyme = "開", open_char
    else:
        # 两侧都有字时，先由声母/元音确定开合。
        if vowel in {"i", "e"}:
            open_ = "合" if initial in CONSONANT_OPEN else "開"
        elif vowel in {"a", "ə"}:
            open_ = "合" if initial in A_SCHWA_OPEN else "開"
        elif vowel in O_U_VOWELS:
            bod = initial in BOD_INITIALS and effective_coda in BOD_CODAS
            open_ = "開" if bod else "合"
        else:
            open_ = "開"
        base_rhyme = open_char if open_ == "開" else closed_char

    rhyme = OVERRIDES.get(vowel, {}).get(flips + (group,), base_rhyme)
    if vowel in O_U_VOWELS:
        if rhyme in O_U_OPEN_RIMES:
            open_ = "開"
        elif (
            initial in BOD_INITIALS
            and effective_coda in BOD_CODAS
            and rhyme in BOD_CLOSED_RIMES
        ):
            open_ = "合"
    return (open_, rhyme)
