"""用工作簿本身校验解析与声母对照（需要仓库根目录下的 ``dict.xlsx``）。

这些测试不是包运行时的依赖：没有 ``dict.xlsx`` 或 ``openpyxl`` 时会跳过。
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from pboc_tanyu import mc_grade, mc_initials, mc_position, mc_rhyme, parse_syllable
from pboc_tanyu._initials import _MC_INITIALS
from pboc_tanyu._rhyme_rules import BASE, OVERRIDES

try:
    import openpyxl
except ImportError:  # pragma: no cover - 开发环境一般都有
    openpyxl = None  # type: ignore[assignment]

DICT_PATH = Path(__file__).resolve().parents[1] / "dict.xlsx"

# 工作簿自身的不一致（不属于解析错误）。
KNOWN_TONE_MISMATCH = {"ŋ̊arh"}  # 獻：擬音作去聲 -h，推導音韻地位卻寫作「平」
KNOWN_TAIL_MISMATCH = {"dzewk"}  # 尾寫作 k，按擬音應為 wk

_CACHE: tuple[list[tuple[object, ...]], list[tuple[object, ...]]] | None = None


def _data() -> tuple[list[tuple[object, ...]], list[tuple[object, ...]]]:
    """返回 (小韻表行, 音節表行)。"""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if openpyxl is None:
        raise unittest.SkipTest("需要 openpyxl")
    if not DICT_PATH.exists():
        raise unittest.SkipTest(f"找不到 {DICT_PATH}")

    workbook = openpyxl.load_workbook(DICT_PATH, read_only=True, data_only=True)
    try:
        rows = workbook["小韻表"].iter_rows(values_only=True)
        syllables = [row for index, row in enumerate(rows) if index > 0]
        sheet = list(workbook["音節表"].iter_rows(values_only=True))
    finally:
        workbook.close()

    _CACHE = (syllables, sheet)
    return _CACHE


_PAREN = re.compile(r"\([^)]*\)")
_GROUP_CODE = re.compile(r"^[A-Za-z.]+")
_TRANSLATE = str.maketrans({"帮": "幫", "群": "羣", "娘": "孃", "雲": "云"})


def _label_initials(label: object) -> list[str]:
    """从《音節表》第 2 行的表头里取出中古声母，如 ``NG曉書(前)；透`` → 曉書透。"""
    text = _PAREN.sub("", str(label))
    text = _GROUP_CODE.sub("", text)
    text = text.replace("；", "")
    return [char.translate(_TRANSLATE) for char in text if "\u4e00" <= char <= "\u9fff"]


def test_sheet_mapping_matches_package() -> None:
    """包内对照表应与《音節表》第 2、3 行完全一致。"""
    _, sheet = _data()
    header, ipa_row = sheet[1], sheet[2]

    expected: dict[str, list[str]] = {}
    for index in range(4, 56):  # E..BD
        label = header[index]
        ipa = ipa_row[index]
        if label is None or ipa is None:
            continue
        bucket = expected.setdefault(str(ipa), [])
        for char in _label_initials(label):
            if char not in bucket:
                bucket.append(char)

    assert {key: tuple(value) for key, value in expected.items()} == dict(_MC_INITIALS)


def test_every_syllable_parses_and_matches_sheet() -> None:
    """小韻表 4036 条拟音全部可解析，且与 聲/等/韻/尾/調 五列一致。"""
    syllables, _ = _data()

    expected_grade = {
        (False, False): {"", None},
        (True, False): {"一"},
        (False, True): {"三"},
        (True, True): {"二"},
    }

    problems: list[str] = []
    tone_mismatches: list[tuple[str, str]] = []
    tail_mismatches: list[tuple[str, object]] = []

    for row in syllables:
        ipa = str(row[0])
        sheet_initial = str(row[2])
        grade = row[3]
        sheet_rime = str(row[4])
        sheet_tail = row[5]
        position = None if row[7] is None else str(row[7])

        try:
            parsed = parse_syllable(ipa)
        except ValueError as error:
            problems.append(f"{ipa}: 解析失败：{error}")
            continue

        if parsed["initial"] != sheet_initial:
            problems.append(f"{ipa}: 声母 {parsed['initial']!r} != {sheet_initial!r}")

        grade_key = (parsed["pharyngealized"], parsed["has_r"])
        if grade is not None and grade not in expected_grade[grade_key]:
            problems.append(f"{ipa}: 等 {grade!r} 与 ˤ/-r- 组合不符")

        expected_rime = parsed["vowel"] + parsed["coda"]
        if parsed["tone_marker"] in ("s", "ps"):
            expected_rime += parsed["tone_marker"]
        if expected_rime != sheet_rime:
            problems.append(f"{ipa}: 韻 {expected_rime!r} != {sheet_rime!r}")

        if position:
            if position[-1] != parsed["tone"]:
                tone_mismatches.append((ipa, position))
            sheet_tail_expected = {"上": "q", "平": None}.get(parsed["tone"])
            if parsed["tone"] == "去":
                sheet_tail_expected = parsed["tone_marker"]
            elif parsed["tone"] == "入":
                sheet_tail_expected = parsed["coda"]
            if sheet_tail_expected != sheet_tail:
                tail_mismatches.append((ipa, sheet_tail))

    assert not problems, "\n".join(problems[:20])
    assert {ipa for ipa, _ in tone_mismatches} <= KNOWN_TONE_MISMATCH, tone_mismatches
    assert {ipa for ipa, _ in tail_mismatches} <= KNOWN_TAIL_MISMATCH, tail_mismatches


def test_all_syllable_initials_are_known() -> None:
    syllables, _ = _data()
    missing = {str(row[2]) for row in syllables} - set(_MC_INITIALS)
    assert not missing, f"对照表缺少声母：{sorted(missing)}"


def test_mapping_accuracy_on_syllables() -> None:
    """粗对照应覆盖绝大多数音节；已知少量逐词例外。"""
    syllables, _ = _data()
    mismatches = []
    for row in syllables:
        if row[7] is None:
            continue
        initial = str(row[2])
        middle_chinese = str(row[7])[0].translate(_TRANSLATE)
        if middle_chinese not in _MC_INITIALS[initial]:
            mismatches.append((initial, middle_chinese, str(row[0])))
    assert len(mismatches) <= 40, f"{len(mismatches)} 条例外，例如 {mismatches[:5]}"


def test_prediction_accuracy_on_syllables() -> None:
    """单值推导与《小韻表》的中古声母基本一致。"""
    syllables, _ = _data()

    correct = 0
    total = 0
    errors: list[tuple[str, str, str]] = []

    for row in syllables:
        ipa = str(row[0])
        predicted = mc_initials(parse_syllable(ipa))

        assert isinstance(predicted, str), ipa
        assert len(predicted) == 1, (ipa, predicted)

        if row[7] is None:
            continue
        actual = str(row[7])[0].translate(_TRANSLATE)
        total += 1
        if predicted == actual:
            correct += 1
        else:
            errors.append((ipa, predicted, actual))

    assert total == 4034
    assert correct / total >= 0.985, f"准确率 {correct}/{total}，例如 {errors[:10]}"
    assert len(errors) <= 60, f"{len(errors)} 条例外：{errors[:10]}"


def test_grade_accuracy_on_syllables() -> None:
    """等第推导与《小韻表》推導音韻地位中的等（含三A/B/C）基本一致。"""
    syllables, _ = _data()
    grade_re = re.compile(r"([一二三四])([ABC])?")

    correct = 0
    total = 0
    errors: list[tuple[str, str, str]] = []
    allowed = {"一", "二", "三", "三A", "三B", "三C", "四"}

    for row in syllables:
        if row[7] is None:
            continue
        match = grade_re.search(str(row[7]))
        if match is None:
            continue
        actual = match.group(1) + (match.group(2) or "")
        predicted = mc_grade(parse_syllable(str(row[0])))
        assert predicted in allowed, str(row[0])
        total += 1
        if predicted == actual:
            correct += 1
        else:
            errors.append((str(row[0]), predicted, actual))

    assert total == 4034
    assert correct / total >= 0.97, f"准确率 {correct}/{total}，例如 {errors[:10]}"
    assert len(errors) <= 120, f"{len(errors)} 条例外：{errors[:10]}"


def test_position_coverage_on_syllables() -> None:
    """每条音节都能生成音韵地位字符串。"""
    syllables, _ = _data()
    for row in syllables:
        position = mc_position(parse_syllable(str(row[0])))
        assert isinstance(position, str) and position, str(row[0])
        assert position[-1] in "平上去入", str(row[0])


def test_rhyme_coverage_on_syllables() -> None:
    """每条《小韻表》音节都能给出合法的 (開/合, 韵)。"""
    syllables, _ = _data()
    for row in syllables:
        result = mc_rhyme(parse_syllable(str(row[0])))
        assert isinstance(result, tuple) and len(result) == 2, str(row[0])
        assert result[0] in {"開", "合"}, str(row[0])
        assert isinstance(result[1], str) and result[1], str(row[0])


def test_rhyme_rule_table() -> None:
    """韵规则为七个元音的小表：默认表 + 声母类型修正。"""
    assert set(BASE) == {"a", "e", "i", "o", "u", "ə", "ia"}
    assert set(OVERRIDES) <= set(BASE)
    assert sum(len(table) for table in BASE.values()) == 221
    assert sum(len(table) for table in OVERRIDES.values()) == 309
