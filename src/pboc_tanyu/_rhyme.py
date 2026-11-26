"""PBOC 音节到切韵开合与韵的推导。

开合和韵放在一张规则表里推导，按七个主元音（a、e、i、o、u、ə、ia）分成
七组小表：

* ``BASE[vowel][(phar, r, coda)]``：该元音在 ˤ / -r- / 韵尾下的默认
  ``(開合, 韵)``；
* ``OVERRIDES[vowel][(phar, r, coda, group, is_w)]``：按声母类型
  （唇、舌頭、舌上、齒頭、莊、章、牙、喉、來、日、以）和是否合口化
  声母修正的条目。

``coda`` 用“有效韵尾”：去声的 ``-s`` / ``-ps`` 记为 ``"s"``，其余仍用
IPA 韵尾。声母类型由中古声母归并而来；``is_w`` 表示 kw、kʰw、gw、ŋw、
ʔw、w、ẘ 这类合口化声母。

另有一条表外补充：L 系 ``l`` + 非三等 + 无 -r- + ``-əps`` 走 *-its 一支，
归四等開齊（``lˤəps``）；``-əps > -us`` 只适用于 T/N/TS，不适用于近音 L。

规则表由 ``dict.xlsx`` 的《小韻表》生成；不能覆盖的例外见
``rhyme_exceptions.tsv``。韵目以《切韵》为准：平/上/去用平声韵目，入声用
入声韵目；寒合作桓、歌合作戈、真合作諄。
"""

from __future__ import annotations

from ._groups import MC_GROUP, W_INITIALS
from ._initials import mc_initials
from ._parser import Syllable
from ._rhyme_rules import BASE, OVERRIDES
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
    group = MC_GROUP.get(mc_initials(syllable))
    if group is None:
        raise ValueError(f"无法归类的声母：{initial!r}")

    flips = (int(phar), int(has_r), effective_coda)
    outcome = OVERRIDES.get(vowel, {}).get(flips + (group, int(initial in W_INITIALS)))
    if outcome is not None:
        return outcome

    table = BASE.get(vowel, {})
    outcome = table.get(flips)
    if outcome is not None:
        return outcome

    # 规则表未覆盖：先忽略韵尾，再退到非三等的默认值。
    outcome = table.get((flips[0], flips[1], "")) or table.get((0, 0, ""))
    if outcome is not None:
        return outcome

    raise ValueError(f"无法推导声母 {initial!r}、元音 {vowel!r}、韵尾 {coda!r} 的开合与韵")
