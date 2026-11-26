"""把“字 + PBOC 注音”的 TSV 转成 AWs-363 切韵推导器的格式。

输入 TSV 没有表头：

* 第一列：单个汉字（或标点）；
* 第二列：PBOC 的 IPA 注音，可以省略。

输出每行是 ``字(音韵地位)``；没有注音的行只输出该字符。
"""

from __future__ import annotations

from ._parser import parse_syllable
from ._position import mc_position

__all__ = ["convert_tsv"]


def convert_tsv(text: str) -> str:
    """把标准注音 TSV 转成 AWs-363 的 ``字(音韵地位)`` 文本。

    Args:
        text: TSV 文本。每行两列：字符、PBOC 注音；第二列可省略。
            空行原样保留。

    Returns:
        连续的 ``字(音韵地位)`` 文本，不含换行；没有注音的行只保留字符。
        空行不产生内容。

    Raises:
        ValueError: 某行超过两列、第一列不是单个字符，或注音无法解析。
    """
    out: list[str] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if line == "":
            continue

        fields = line.split("\t")
        if len(fields) > 2 and any(field.strip() for field in fields[2:]):
            raise ValueError(f"第 {lineno} 行超过两列")

        char = fields[0].strip()
        annotation = fields[1].strip() if len(fields) >= 2 else ""

        if not char:
            raise ValueError(f"第 {lineno} 行第一列为空")
        if len(char) != 1:
            raise ValueError(f"第 {lineno} 行第一列不是单个字符：{char!r}")

        if not annotation:
            out.append(char)
            continue

        try:
            position = mc_position(parse_syllable(annotation))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"第 {lineno} 行注音 {annotation!r} 无法解析：{exc}") from exc
        out.append(f"{char}({position})")

    return "".join(out)
