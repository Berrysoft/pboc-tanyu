"""PBOC（基于文献的上古汉语）拟音的切分、声母、等第与韵推导。

本包做五件小事：

1. :func:`parse_syllable`：把一条 PBOC 的 IPA 拟音切成
   声母 + 是否咽化 + 是否带 -r- + 主元音 + 韵尾 + 声调；
2. :func:`mc_initials`：给定 :class:`Syllable`，返回一个中古声母；
3. :func:`mc_grade`：给定 :class:`Syllable`，返回切韵等第（含三A/三B/三C）；
4. :func:`mc_rhyme`：给定 :class:`Syllable`，返回 ``(開/合, 韵)``；
5. :func:`mc_position`：给定 :class:`Syllable`，返回切韵音韵地位字符串。

方言分歧按东部方言（中原）标准处理。
数据来自 ``dict.xlsx`` 的《音節表》（表内版本 26.11.21）。
"""

from ._grade import mc_grade
from ._initials import mc_initials
from ._parser import Syllable, parse_syllable
from ._position import mc_position
from ._rhyme import mc_rhyme
from .convert import convert_tsv

__all__ = [
    "parse_syllable",
    "mc_initials",
    "mc_grade",
    "mc_rhyme",
    "mc_position",
    "convert_tsv",
]
__version__ = "0.18.3"
