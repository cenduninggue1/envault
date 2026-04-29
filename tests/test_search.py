"""Tests for envault.search module."""

from __future__ import annotations

import pytest

from envault.search import SearchError, SearchResult, format_results, search_vars

SAMPLE: dict[str, str] = {
    "DATABASE_URL": "postgres://localhost/mydb",
    "DEBUG": "true",
    "SECRET_KEY": "s3cr3t",
    "API_KEY": "abc123",
    "APP_ENV": "production",
}


def test_search_by_key_glob():
    results = search_vars(SAMPLE, "*KEY*", search_keys=True)
    keys = {r.key for r in results}
    assert "SECRET_KEY" in keys
    assert "API_KEY" in keys
    assert "DEBUG" not in keys


def test_search_by_key_substring():
    results = search_vars(SAMPLE, "debug", search_keys=True, case_sensitive=False)
    assert len(results) == 1
    assert results[0].key == "DEBUG"


def test_search_by_value():
    results = search_vars(SAMPLE, "true", search_keys=False, search_values=True)
    assert len(results) == 1
    assert results[0].key == "DEBUG"
    assert results[0].match_type == "value"


def test_search_both_key_and_value():
    results = search_vars(SAMPLE, "*key*", search_keys=True, search_values=True, case_sensitive=False)
    # 'API_KEY' key matches; value 'abc123' does not contain 'key'
    keys = {r.key for r in results}
    assert "API_KEY" in keys
    assert "SECRET_KEY" in keys


def test_match_type_both():
    variables = {"KEY_NAME": "some_key_value"}
    results = search_vars(variables, "key", search_keys=True, search_values=True, case_sensitive=False)
    assert len(results) == 1
    assert results[0].match_type == "both"


def test_search_regex():
    results = search_vars(SAMPLE, r"^DB|^DATABASE", search_keys=True, use_regex=True)
    assert any(r.key == "DATABASE_URL" for r in results)


def test_search_regex_invalid_raises():
    with pytest.raises(SearchError, match="Invalid regex"):
        search_vars(SAMPLE, "[invalid", search_keys=True, use_regex=True)


def test_search_empty_pattern_raises():
    with pytest.raises(SearchError, match="must not be empty"):
        search_vars(SAMPLE, "", search_keys=True)


def test_search_case_sensitive():
    results = search_vars(SAMPLE, "debug", search_keys=True, case_sensitive=True)
    assert len(results) == 0  # 'DEBUG' != 'debug'


def test_search_no_matches_returns_empty():
    results = search_vars(SAMPLE, "NONEXISTENT", search_keys=True)
    assert results == []


def test_format_results_no_matches():
    output = format_results([])
    assert output == "No matches found."


def test_format_results_basic():
    results = [SearchResult(key="FOO", value="bar", match_type="key")]
    output = format_results(results)
    assert "FOO=bar" in output


def test_format_results_show_match_type():
    results = [SearchResult(key="FOO", value="bar", match_type="both")]
    output = format_results(results, show_match_type=True)
    assert "[both]" in output
