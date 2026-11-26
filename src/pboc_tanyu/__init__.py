"""PBOC（基于文献的上古汉语）拟音的切分与声母推导工具。

本包只做两件小事：

1. :func:`parse_syllable`：把一条 PBOC 的 IPA 拟音切成
   声母 + 是否咽化 + 是否带 -r- + 主元音 + 韵尾 + 声调；
2. :func:`mc_initials`：给定 :class:`Syllable`，返回一个中古声母
   （传统字母，如 ``幫``、``知``、``羣``）。

方言分歧按东部方言（中原）标准处理。
数据来自 ``dict.xlsx`` 的《音節表》（表内版本 26.11.21）。
"""

from ._initials import mc_initials
from ._parser import Syllable, parse_syllable

__all__ = ["parse_syllable", "mc_initials"]
__version__ = "0.5.0"
