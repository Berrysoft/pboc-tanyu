"""把 Syllable 格式化成切韵自动推导器接受的音韵地位字符串。"""

from __future__ import annotations

from ._grade import mc_grade
from ._initials import mc_initials
from ._parser import Syllable
from ._rhyme import mc_rhyme
from ._syllable import coerce_syllable

__all__ = ["mc_position"]

#: 入声韵 → 对应的平声韵。
_RU_TO_PING = {
    "屋": "東", "沃": "冬", "燭": "鍾", "覺": "江",
    "質": "真", "術": "諄", "物": "文", "迄": "殷",
    "月": "元", "曷": "寒", "末": "桓", "黠": "山", "鎋": "刪",
    "屑": "先", "薛": "仙", "藥": "陽", "鐸": "唐",
    "陌": "庚", "麥": "耕", "昔": "清", "錫": "青",
    "職": "蒸", "德": "登", "緝": "侵", "合": "覃",
    "盍": "談", "葉": "鹽", "帖": "添", "洽": "咸",
    "狎": "銜", "業": "嚴", "乏": "凡",
}

#: 切韵分韵并回《小韻表》的平声韵目。
_MERGE = {"桓": "寒", "戈": "歌", "諄": "真"}

#: 唇音：呼固定為 null。
_LIP = frozenset({"幫", "滂", "並", "明"})

#: 開合中立韻：呼固定為 null。
_NEUTRAL = frozenset({"東", "冬", "鍾", "江", "模", "尤", "侯"})

#: 分開合韻：呼必填開或合。
_BOTH = frozenset(
    {
        "支", "脂", "微", "齊", "祭", "泰", "佳", "皆", "夬", "廢",
        "真", "元", "寒", "刪", "山", "先", "仙", "歌", "麻",
        "陽", "唐", "庚", "耕", "清", "青", "蒸", "登",
    }
)

#: 僅開口韻：非唇音呼固定為開。
_OPEN = frozenset(
    {
        "之", "魚", "咍", "臻", "殷", "痕",
        "蕭", "宵", "肴", "豪", "幽",
        "侵", "覃", "談", "鹽", "添", "咸", "銜", "嚴",
    }
)

#: 僅合口韻：非唇音呼固定為合。
_CLOSED = frozenset({"虞", "灰", "文", "魂", "凡"})


def mc_position(syllable: Syllable) -> str:
    """返回 ``声母 + 开合 + 韵等 + 韵母 + 声调`` 的音韵地位字符串。

    这是 AWs-363 切韵音系自动推导器的括号内格式，例如 ``日開三侵平``。
    开合的写法直接采用该推导器 ``音韻地位.驗證`` 的 ``呼韻搭配``：

    * 唇音（幫滂並明）：呼固定为 null，不写；
    * 開合中立韻（東冬鍾江模尤侯）：呼固定为 null，不写；
    * 分開合韻（支脂微齊祭泰佳皆夬廢真元寒刪山先仙歌麻陽唐庚耕清青蒸登）：
      呼必填，写開或合；
    * 僅開口韻（之魚咍臻殷痕蕭宵肴豪幽侵覃談鹽添咸銜嚴）：写開；
    * 僅合口韻（虞灰文魂凡）：写合。

    入声韵母改用对应的平声韵；桓、戈、諄并回寒、歌、真。

    Args:
        syllable: ``parse_syllable`` 返回的 :class:`pboc_tanyu.Syllable`。

    Returns:
        音韵地位字符串，如 ``"章開三魚平"``、``"端一模平"``、``"日合三真平"``。

    Examples:
        >>> from pboc_tanyu import mc_position, parse_syllable
        >>> mc_position(parse_syllable("ta"))
        '章開三魚平'
        >>> mc_position(parse_syllable("tˤa"))
        '端一模平'
        >>> mc_position(parse_syllable("bˤəŋ"))
        '並一登平'
        >>> mc_position(parse_syllable("nun"))
        '日合三真平'
    """
    _initial, _, _, _, _, tone, _ = coerce_syllable(syllable)
    initial = mc_initials(syllable)
    open_, rhyme = mc_rhyme(syllable)
    grade = mc_grade(syllable)

    if tone == "入":
        rhyme = _RU_TO_PING.get(rhyme, rhyme)
    rhyme = _MERGE.get(rhyme, rhyme)

    parts = [initial]
    if initial in _LIP or rhyme in _NEUTRAL:
        pass
    elif rhyme in _BOTH:
        parts.append(open_)
    elif rhyme in _OPEN:
        parts.append("開")
    elif rhyme in _CLOSED:
        parts.append("合")
    else:
        raise ValueError(f"未知韻：{rhyme!r}")

    parts.extend([grade, rhyme, tone])
    return "".join(parts)
