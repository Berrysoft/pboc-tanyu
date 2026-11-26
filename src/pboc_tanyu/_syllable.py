"""Syllable 的校验与解包。"""

from __future__ import annotations

from collections.abc import Mapping

from ._parser import Syllable

_SYLLABLE_KEYS = (
    "initial",
    "pharyngealized",
    "has_r",
    "vowel",
    "coda",
    "tone",
    "tone_marker",
)


def coerce_syllable(syllable: Syllable) -> tuple[str, bool, bool, str, str, str, str]:
    """校验并解包一个 :class:`Syllable`。

    Returns:
        ``(initial, pharyngealized, has_r, vowel, coda, tone, tone_marker)``。
    """
    if not isinstance(syllable, Mapping):
        raise TypeError(
            f"syllable 必须是 parse_syllable 返回的 Syllable，而不是 {type(syllable).__name__}"
        )

    missing = [key for key in _SYLLABLE_KEYS if key not in syllable]
    if missing:
        raise ValueError(f"syllable 缺少键 {missing!r}；请先调用 parse_syllable 生成。")

    initial = syllable["initial"]
    vowel = syllable["vowel"]
    coda = syllable["coda"]
    tone = syllable["tone"]
    tone_marker = syllable["tone_marker"]
    if not isinstance(initial, str) or not isinstance(vowel, str):
        raise TypeError("syllable['initial'] 和 syllable['vowel'] 必须是 str")
    if not isinstance(coda, str) or not isinstance(tone_marker, str):
        raise TypeError("syllable['coda'] 和 syllable['tone_marker'] 必须是 str")
    if tone not in {"平", "上", "去", "入"}:
        raise ValueError(f"syllable['tone'] 必须是 平/上/去/入，而不是 {tone!r}")

    return (
        initial,
        bool(syllable["pharyngealized"]),
        bool(syllable["has_r"]),
        vowel,
        coda,
        str(tone),
        tone_marker,
    )
