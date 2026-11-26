"""PBOC 音节到中古声母的单值推导。

输入只接受 :class:`pboc_tanyu.Syllable`（``parse_syllable`` 的返回值），
返回一个中古声母。推导分两步：

1. 先按咽化 ˤ 和 -r- 决定基本的中古声母（T、TS、N、L、K、W 等系）；
2. 再看主元音的前后高低和韵尾、声调：前元音 e/i 会使牙喉音颚化
   （k > 章、g > 常、ŋ > 日、h > 書），清响音和个别齿音再按元音、
   韵尾、声调选择具体结果。

方言分歧按东部方言（中原）标准处理：n̥、l̥、r̥ 在东部方言中三等变書、
非三等变透，西部方言则一律变曉；本包取东部，不取曉。

规则主要依据知乎《上古-中古音类源流略说》
（https://zhuanlan.zhihu.com/p/567955454），并用《小韻表》全量校验。
"""

from __future__ import annotations

from ._parser import Syllable
from ._syllable import coerce_syllable

__all__ = ["mc_initials"]

#: 粗对照表，仅作参考与测试用；实际推导不再直接返回这张表。
_MC_INITIALS: dict[str, tuple[str, ...]] = {
    "p": ("幫",),
    "pʰ": ("滂",),
    "b": ("並",),
    "m": ("明",),
    "m̥": ("曉",),
    "t": ("端", "知", "章"),
    "st": ("書",),
    "tʰ": ("透", "徹", "昌"),
    "d": ("定", "澄", "常"),
    "n": ("泥", "娘", "日"),
    "n̥": ("透", "徹", "書", "曉", "心"),
    "ts": ("精", "莊"),
    "tsʰ": ("清", "初"),
    "dz": ("從", "崇"),
    "s": ("心", "生"),
    "l": ("以", "定", "澄"),
    "l̥": ("透", "徹", "書", "曉", "心"),
    "sl": ("心", "邪"),
    "ml": ("船", "俟"),
    "r": ("來",),
    "r̥": ("透", "徹"),
    "sr": ("生",),
    "C.r": ("來",),
    "j": ("以",),
    "j̊": ("昌", "曉"),
    "kj": ("見",),
    "kʰj": ("溪",),
    "mj": ("船", "俟"),
    "sj": ("邪",),
    "k": ("見",),
    "kʰ": ("溪",),
    "g": ("羣", "匣"),
    "ŋ": ("疑", "日"),
    "ŋ̊": ("曉", "書", "透", "心", "生"),
    "h": ("曉", "書"),
    "kw": ("見",),
    "kʰw": ("溪",),
    "gw": ("羣", "匣"),
    "ŋw": ("疑",),
    "w": ("云", "匣", "以", "邪"),
    "ẘ": ("心", "曉"),
    "ʔ": ("影",),
    "ʔw": ("影",),
}

#: 可诱发牙喉音颚化的前元音。
_FRONT = frozenset({"i", "e", "ia"})

#: 与 ˤ、-r-、元音都无关的单值声母。
_SIMPLE: dict[str, str] = {
    "p": "幫",
    "pʰ": "滂",
    "b": "並",
    "m": "明",
    "m̥": "曉",
    "r": "來",
    "C.r": "來",
    "j": "以",
    "st": "書",
    "kj": "見",
    "kʰj": "溪",
    "kw": "見",
    "kʰw": "溪",
    "ŋw": "疑",
    "ʔ": "影",
    "ʔw": "影",
    "sj": "邪",
}


def _resolve(
    initial: str,
    phar: bool,
    has_r: bool,
    vowel: str,
    coda: str,
    tone: str,
    tone_marker: str,
) -> str:
    simple = _SIMPLE.get(initial)
    if simple is not None:
        return simple

    # T 系：*t' > 端，*tr > 知，*t > 章
    if initial == "t":
        return "章" if (not phar and not has_r) else ("知" if has_r else "端")
    if initial == "tʰ":
        return "昌" if (not phar and not has_r) else ("徹" if has_r else "透")
    if initial == "d":
        return "常" if (not phar and not has_r) else ("澄" if has_r else "定")

    # TS 系：-r- 决定精组 / 莊组
    if initial == "ts":
        return "莊" if has_r else "精"
    if initial == "tsʰ":
        return "初" if has_r else "清"
    if initial == "dz":
        return "崇" if has_r else "從"

    # S 系
    if initial == "s":
        return "生" if has_r else "心"

    # N 系：*n' > 泥，*n > 日，*nr > 娘
    if initial == "n":
        if has_r:
            return "娘"
        return "泥" if phar else "日"

    # L 系：*l' > 定，*l > 以，*lr > 澄
    if initial == "l":
        if has_r:
            return "澄"
        return "定" if phar else "以"

    # K 系：前元音三等使 k > 章、g > 常、h > 書、ŋ > 日。
    if initial == "k":
        if not phar and not has_r and vowel in _FRONT:
            return "章"
        return "見"
    if initial == "kʰ":
        return "溪"
    if initial == "g":
        if phar:
            return "匣"
        if not has_r and vowel in _FRONT:
            return "常"
        return "羣"
    if initial == "gw":
        return "匣" if phar else "羣"
    if initial == "h":
        return "書" if (not phar and not has_r and vowel in _FRONT) else "曉"
    if initial == "ŋ":
        return "日" if (not phar and not has_r and vowel in _FRONT) else "疑"
    if initial == "ŋw":
        return "疑"

    # W 系：*w' > 匣，*w > 云；前元音三等 *wE- 再分入以/邪。
    if initial == "w":
        if phar:
            return "匣"
        if has_r:
            return "云"
        if vowel in _FRONT:
            return "邪" if tone == "去" else "以"
        return "云"
    if initial == "ẘ":
        if not phar and (
            coda == "r" or (tone_marker == "s" and vowel in {"a", "e"})
        ):
            return "心"
        return "曉"

    # 清响音：按东部方言；n̥ 的書/心再按韵尾、元音、声调互补。
    if initial == "n̥":
        if has_r:
            return "徹"
        if phar:
            return "透"
        if coda == "m":
            return "書"
        if vowel in {"e", "o"} and coda != "p":
            return "心"
        return "心" if tone == "平" else "書"
    if initial == "l̥":
        if has_r:
            return "徹"
        if phar:
            return "透"
        return "書"
    if initial == "r̥":
        if phar and not has_r and vowel != "a":
            return "透"
        return "徹"
    if initial == "ŋ̊":
        if phar and has_r:
            return "生" if vowel == "a" else "透"
        if has_r:
            return "生"
        if not phar and vowel in _FRONT:
            return "書"
        return "曉"

    # 其他多对一
    if initial == "sl":
        # ia 特殊：上声心、去声邪；其余前元音（含 ia 平/入）心。
        if not phar and vowel == "ia" and tone == "去":
            return "邪"
        return "心" if (phar or vowel in _FRONT) else "邪"
    if initial in {"ml", "mj"}:
        if vowel == "ə" and coda == "" and tone in {"平", "上"}:
            return "俟"
        return "船"
    if initial == "j̊":
        if coda in {"ŋ", "k"} and vowel in {"ə", "u"}:
            return "曉"
        if coda == "n" and tone == "去":
            return "曉"
        return "昌"

    raise ValueError(f"无法处理的 PBOC 声母：{initial!r}")


def mc_initials(syllable: Syllable) -> str:
    """返回一条 PBOC 音节的中古声母。

    Args:
        syllable: ``parse_syllable`` 返回的 :class:`pboc_tanyu.Syllable`。
            只接受这个类型（运行时是含 ``initial``、``pharyngealized``、
            ``has_r``、``vowel``、``coda``、``tone``、``tone_marker`` 的字典）；
            不再接受裸声母或 IPA 字符串。

    Returns:
        一个中古声母（传统字母，繁体），如 ``"端"``、``"章"``、``"書"``。

    Raises:
        TypeError: 参数不是 Syllable，或字段类型不对。
        ValueError: 字典缺键、声调不合法，或声母无法处理。

    Examples:
        >>> from pboc_tanyu import mc_initials, parse_syllable
        >>> mc_initials(parse_syllable("tˤa"))
        '端'
        >>> mc_initials(parse_syllable("ta"))
        '章'
        >>> mc_initials(parse_syllable("ke"))
        '章'
        >>> mc_initials(parse_syllable("ŋe"))
        '日'
    """
    initial, phar, has_r, vowel, coda, tone, tone_marker = coerce_syllable(syllable)
    return _resolve(initial, phar, has_r, vowel, coda, tone, tone_marker)
