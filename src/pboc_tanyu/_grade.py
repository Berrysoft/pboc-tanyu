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

#: 重紐 AB 類的韻。云母沒有 A 類，遇到這些韻一律作 B 類。
_AB_RIMES = frozenset({"支", "脂", "祭", "真", "仙", "宵", "幽", "侵", "鹽"})

#: 等韻搭配：某些韻本身沒有二等，ˤ + -r- 不能機械地判作二等。
_FIRST_ONLY = frozenset({"冬", "模", "泰", "灰", "咍", "魂", "痕", "寒", "豪", "唐", "登", "侯", "覃", "談"})
_THIRD_ONLY = frozenset({
    "鍾", "支", "脂", "之", "微", "魚", "虞", "祭", "廢", "真", "臻", "文",
    "殷", "元", "仙", "宵", "陽", "清", "蒸", "尤", "幽", "侵", "鹽", "嚴", "凡",
})
_FOURTH_ONLY = frozenset({"齊", "先", "蕭", "青", "添"})
_FIRST_THIRD = frozenset({"東", "歌"})


def _san_grade(syllable: Syllable, has_r: bool) -> str:
    """三等：按 r、声母类型、韵查 A/B/C 表。"""
    initial = mc_initials(syllable)
    rhyme = mc_rhyme(syllable)[1]
    base_rhyme = _BASE_RHYME.get(rhyme, rhyme)
    if initial == "云" and base_rhyme in _AB_RIMES:
        return "三B"
    group = MC_GROUP.get(initial)
    if group is None:
        return "三"
    return _SAN.get((int(has_r), group, base_rhyme), "三")


def mc_grade(syllable: Syllable) -> str:
    """返回一条 PBOC 音节的切韵等第。

    规则：

    * 没有咽化 ˤ → 三等；三等再按 -r-、声母类型和韵分辨 ``三A`` / ``三B`` /
      ``三C`` / ``三``；
    * 有 ˤ、有 -r- → 二等；但若該韻本身沒有二等（尤、侯、覃、歌等），
      按該韻的實際等第：尤 → 三，侯/覃/歌 → 一，齊/先/蕭/青/添 → 四；
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
        # ˤ + -r- 一般是二等，但二等只出現在有二等的韻。若該韻沒有二等，
        # 就按該韻的實際等第：尤 → 三，侯/覃/歌 → 一，齊/先/蕭/青/添 → 四。
        rhyme = mc_rhyme(syllable)[1]
        if rhyme in _THIRD_ONLY:
            return _san_grade(syllable, True)
        if rhyme in _FIRST_ONLY or rhyme in _FIRST_THIRD:
            return "一"
        if rhyme in _FOURTH_ONLY:
            return "四"
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
