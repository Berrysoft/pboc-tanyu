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

#: 鈍音聲母：只有這些聲母在三等分 A/B/C。
_DUN = frozenset("幫滂並明見溪羣疑影曉匣云")

#: 羊系 K 声母：kj/kʰj 的 j 是声母前化，不表示三等。
_KJ = frozenset({"kj", "kʰj"})

#: 等韻搭配：某些韻本身沒有二等，ˤ + -r- 不能機械地判作二等。
_FIRST_ONLY = frozenset({"冬", "模", "泰", "灰", "咍", "魂", "痕", "寒", "豪", "唐", "登", "侯", "覃", "談"})
_SECOND_ONLY = frozenset({"江", "佳", "皆", "夬", "刪", "山", "肴", "耕", "咸", "銜"})
_THIRD_ONLY = frozenset({
    "鍾", "支", "脂", "之", "微", "魚", "虞", "祭", "廢", "真", "臻", "文",
    "殷", "元", "仙", "宵", "陽", "清", "蒸", "尤", "幽", "侵", "鹽", "嚴", "凡",
})
_FOURTH_ONLY = frozenset({"齊", "先", "蕭", "青", "添"})
_FIRST_THIRD = frozenset({"東", "歌"})
_SECOND_THIRD = frozenset({"麻", "庚"})


def _allowed_grades(rhyme: str) -> frozenset[str]:
    """該韻允許的中古等。"""
    if rhyme in _FIRST_ONLY:
        return frozenset({"一"})
    if rhyme in _SECOND_ONLY:
        return frozenset({"二"})
    if rhyme in _THIRD_ONLY:
        return frozenset({"三"})
    if rhyme in _FOURTH_ONLY:
        return frozenset({"四"})
    if rhyme in _FIRST_THIRD:
        return frozenset({"一", "三"})
    if rhyme in _SECOND_THIRD:
        return frozenset({"二", "三"})
    return frozenset()


def _san_grade(syllable: Syllable, has_r: bool) -> str:
    """三等：重紐 AB 韻按有無 -r- 與前元音分 A/B，其餘查 A/B/C 表。"""
    initial = mc_initials(syllable)
    rhyme = mc_rhyme(syllable)[1]
    base_rhyme = _BASE_RHYME.get(rhyme, rhyme)

    # 鈍音 + 重紐 AB 韻：A ⇔ 無 -r- 且前元音（云母永遠 B）。
    if initial in _DUN and base_rhyme in _AB_RIMES:
        if initial == "云":
            return "三B"
        if not has_r and syllable["vowel"] in _FRONT:
            return "三A"
        return "三B"

    group = MC_GROUP.get(initial)
    if group is None:
        return "三"
    return _SAN.get((int(has_r), group, base_rhyme), "三")


def mc_grade(syllable: Syllable) -> str:
    """返回一条 PBOC 音节的切韵等第。

    规则：

    * 没有咽化 ˤ → 三等：
        - 鈍音 + 重紐 AB 韻（支脂祭真仙宵幽侵鹽）：三A ⇔ 無 -r- 且主元音
          為 e/i/ia（云母永遠三B）；其餘三B；
        - 鈍音 + 非重紐三等 → 三C；
        - 銳音 → 三；
    * 羊系 K（kj/kʰj）的 j 是聲母前化，不是三等介音：o/u → 一等，a/ə → 三等；
    * 有 ˤ、有 -r- → 二等；但若該韻本身沒有二等（尤、侯、覃、歌等），
      按該韻的實際等第：尤 → 三，侯/覃/歌 → 一，齊/先/蕭/青/添 → 四；
    * 有 ˤ、无 -r-：
        - 主元音 e/i/ia → 四等；
        - 主元音 ə 且声母是锐音（t、ts、s、l、r 等），韵尾为 -j/-n/-t
          或去声 -s（不含 -ps）→ 四等；
        - 例外：L 系 l + 非三等 + 无 -r- + -əps 走 *-its，也归四等；
        - 其余（a/o/u/ə，或 ə 在钝音后）→ 一等；
    * 最後再按韻的等韻搭配約束：江只能二等、侯只能一等、齊只能四等。

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
    initial, phar, has_r, vowel, coda, tone, tone_marker = coerce_syllable(syllable)
    rhyme = mc_rhyme(syllable)[1]
    base_rhyme = _BASE_RHYME.get(rhyme, rhyme)

    if not phar:
        grade = _san_grade(syllable, has_r)
        # 羊系 K：j 是聲母前化，不是三等介音；o/u 走一等。
        if initial in _KJ and not has_r and vowel in {"o", "u"}:
            grade = "一"
    elif has_r:
        # ˤ + -r- 一般是二等，但二等只出現在有二等的韻。
        if base_rhyme in _THIRD_ONLY:
            grade = _san_grade(syllable, True)
        elif base_rhyme in _FIRST_ONLY or base_rhyme in _FIRST_THIRD:
            grade = "一"
        elif base_rhyme in _FOURTH_ONLY:
            grade = "四"
        else:
            grade = "二"
    elif vowel in _FRONT:
        grade = "四"
    # L 系 *-əps 走 *-its 一支：lˤəps > 四等齊。
    elif initial == "l" and vowel == "ə" and coda == "" and tone_marker == "ps":
        grade = "四"
    elif (
        vowel == "ə"
        and initial in _SHARP
        and (coda in {"j", "n", "t"} or tone_marker == "s")
    ):
        grade = "四"
    else:
        grade = "一"

    # 這些 *-its > 四等齊 的例外，不讓韻的等韻搭配再改回去。
    locked = (
        grade == "四"
        and vowel == "ə"
        and (tone_marker == "ps" or tone_marker == "s" or coda in {"j", "n", "t"})
    )

    # 最後再受韻的等韻搭配約束：江只能二等，侯只能一等，齊只能四等。
    if not locked:
        allowed = _allowed_grades(base_rhyme)
        if allowed and grade[0] not in allowed:
            if len(allowed) == 1:
                grade = next(iter(allowed))
            else:
                for candidate in ("三", "二", "一", "四"):
                    if candidate in allowed:
                        grade = candidate
                        break
    return grade
