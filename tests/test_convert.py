"""``convert_tsv`` 的单元测试。"""

from __future__ import annotations

from pboc_tanyu import convert_tsv


def test_basic() -> None:
    assert convert_tsv("日\tnəm\n端\ttˤa\n") == "日(日開三侵平)端(端合一模平)"
    assert convert_tsv("幫\tpe\n") == "幫(幫開三A支平)"


def test_no_annotation() -> None:
    assert convert_tsv("日\n") == "日"
    assert convert_tsv("，\n") == "，"


def test_multiple_lines_and_blank() -> None:
    text = "日\tnəm\n\n月\tŋwat\n"
    assert convert_tsv(text) == "日(日開三侵平)月(疑合三C月入)"


def test_trailing_newline() -> None:
    assert convert_tsv("日\tnəm") == "日(日開三侵平)"
    assert convert_tsv("日\tnəm\n") == "日(日開三侵平)"


def test_bad_annotation() -> None:
    try:
        convert_tsv("日\tzzz\n")
    except ValueError:
        pass
    else:
        raise AssertionError("'日\\tzzz' 应当报错")


def test_bad_character() -> None:
    for bad in ["\t\n", "日日\tnəm\n", "日\tnəm\textra\n"]:
        try:
            convert_tsv(bad)
        except ValueError:
            continue
        raise AssertionError(f"{bad!r} 应当报错")
