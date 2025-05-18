from __future__ import annotations

import pytest

from panoptikon.filesystem.paths import PathMatchType
from panoptikon.search.query_parser import QueryParser, QueryParserError


def test_parse_exact_match() -> None:
    pattern = QueryParser.parse("file.txt")
    assert pattern.pattern == "file.txt"
    assert pattern.match_type == PathMatchType.EXACT
    assert not pattern.case_sensitive
    assert not pattern.whole_word
    assert pattern.extension is None


def test_parse_wildcard() -> None:
    pattern = QueryParser.parse("file*.txt")
    assert pattern.pattern == "file*.txt"
    assert pattern.match_type == PathMatchType.GLOB


def test_parse_regex() -> None:
    pattern = QueryParser.parse(r"file\d+\.txt")
    assert pattern.pattern == r"file\d+\.txt"
    assert pattern.match_type == PathMatchType.REGEX


def test_parse_case_sensitive() -> None:
    pattern = QueryParser.parse("File.txt", case_sensitive=True)
    assert pattern.case_sensitive


def test_parse_whole_word() -> None:
    pattern = QueryParser.parse("file.txt", whole_word=True)
    assert pattern.whole_word


def test_parse_extension_filter() -> None:
    pattern = QueryParser.parse("report ext:pdf")
    assert pattern.pattern == "report"
    assert pattern.extension == "pdf"
    pattern2 = QueryParser.parse("report ext=pdf")
    assert pattern2.pattern == "report"
    assert pattern2.extension == "pdf"
    pattern3 = QueryParser.parse("report.pdf")
    assert pattern3.pattern == "report.pdf"
    assert pattern3.extension is None


def test_parse_invalid_regex() -> None:
    with pytest.raises(QueryParserError):
        QueryParser.parse(r"file[.txt", case_sensitive=True)


def test_parse_empty_query() -> None:
    with pytest.raises(QueryParserError):
        QueryParser.parse("")


def test_create_sql_condition_exact() -> None:
    pattern = QueryParser.parse("file.txt", whole_word=True)
    sql, params = QueryParser.create_sql_condition(pattern)
    assert "=" in sql
    assert params["pattern"] == "file.txt"


def test_create_sql_condition_wildcard() -> None:
    pattern = QueryParser.parse("file*.txt")
    sql, params = QueryParser.create_sql_condition(pattern)
    assert "LIKE" in sql
    assert "%" in params["pattern"]


def test_create_sql_condition_regex() -> None:
    pattern = QueryParser.parse(r"file\d+\.txt")
    sql, params = QueryParser.create_sql_condition(pattern)
    assert "REGEXP" in sql
    assert params["pattern"] == r"file\d+\.txt"


def test_create_sql_condition_extension() -> None:
    pattern = QueryParser.parse("report ext:pdf")
    sql, params = QueryParser.create_sql_condition(pattern)
    assert "extension" in sql
    assert params["ext"] == "pdf"
