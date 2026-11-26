"""PBOC 音节到切韵等第的推导。

等第返回字符串：``"一"``、``"二"``、``"三"``、``"三A"``、``"三B"``、
``"三C"``、``"四"``。三等再用 A/B/C 区分重紐/無重紐，供切韵推导器使用。
"""

from __future__ import annotations

from ._grade_rules import SAN
from ._groups import MC_GROUP
from ._initials import mc_initials
from ._parser import Syllable
from ._rhyme import mc_rhyme
from ._syllable import coerce_syllable

__all__ = ["mc_grade"]

_SAN = {(r, group, rhyme): label for r, group, rhyme, label in SAN}

#: 三等以外的前元音：e/i 一律四等。
_FRONT = frozenset({"e", "i", "ia"})

#: 锐音声母。非三等、无 -r- 的 ə 在这些声母后接 -j/-n/-t（或 -s 尾）时归四等，
#: 在钝音声母后则归一等。
_SHARP = frozenset({"t", "tʰ", "d", "n", "ts", "tsʰ", "dz", "s", "l", "l̥", "sl", "r"})

#: 入声韵、桓/戈/諄 归回平声韵目，供三等 A/B/C 表使用。
_BASE_RHYME = {
    "桓": "寒", "戈": "歌", "諄": "真",
    "屋": "東", "沃": "冬", "燭": "鍾", "覺": "江",
    "質": "真", "術": "真", "物": "文", "迄": "殷",
    "月": "元", "曷": "寒", "末": "寒", "黠": "山", "鎋": "刪",
    "屑": "先", "薛": "仙", "藥": "陽", "鐸": "唐",
    "陌": "庚", "麥": "耕", "昔": "清", "錫": "青",
    "職": "蒸", "德": "登", "緝": "侵", "合": "覃",
    "盍": "談", "葉": "鹽", "帖": "添", "洽": "咸",
    "狎": "銜", "業": "嚴", "乏": "凡",
}


def _san_grade(syllable: Syllable, has_r: bool) -> str:
    """三等：按 r、声母类型、韵查 A/B/C 表。"""
    rhyme = mc_rhyme(syllable)[1]
    base_rhyme = _BASE_RHYME.get(rhyme, rhyme)
    group = MC_GROUP.get(mc_initials(syllable))
    if group is None:
        return "三"
    return _SAN.get((int(has_r), group, base_rhyme), "三")


def mc_grade(syllable: Syllable) -> str:
    """返回一条 PBOC 音节的切韵等第。

    规则：

    * 没有咽化 ˤ → 三等；三等再按 -r-、声母类型和韵分辨 ``三A`` / ``三B`` /
      ``三C`` / ``三``；
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
        ``"一"``、``"二"``、``"三"``、``"三A"``、``"三B"``、``"三C"`` 或 ``"四"``。

    Examples:
        >>> from pboc_tanyu import mc_grade, parse_syllable
        >>> mc_grade(parse_syllable("ta"))
        '三'
        >>> mc_grade(parse_syllable("tˤa"))
        '一'
        >>> mc_grade(parse_syllable("tˤra"))
        '二'
        >>> mc_grade(parse_syllable("tˤe"))
        '四'
        >>> mc_grade(parse_syllable("pe"))
        '三A'
    """
    initial, phar, has_r, vowel, coda, _tone, tone_marker = coerce_syllable(syllable)

    if not phar:
        return _san_grade(syllable, has_r)
    if has_r:
        return "二"
    if vowel in _FRONT:
        return "四"
    # L 系 *-əps 走 *-its 一支：lˤəps > 四等齊。
    # *-əps > *-us 只适用于 T/N/TS，L 是近音，不在此列。
    if initial == "l" and vowel == "ə" and coda == "" and tone_marker == "ps":
        return "四"
    if (
        vowel == "ə"
        and initial in _SHARP
        and (coda in {"j", "n", "t"} or tone_marker == "s")
    ):
        return "四"
    return "一"
