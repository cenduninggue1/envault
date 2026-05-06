"""Tests for envault.env_check."""

import pytest

from envault.env_check import CheckResult, CheckError, check_vars, format_result


# ---------------------------------------------------------------------------
# check_vars – missing / empty
# ---------------------------------------------------------------------------

def test_check_all_required_present():
    result = check_vars({"A": "1", "B": "2"}, required=["A", "B"])
    assert result.passed
    assert result.missing == []
    assert result.empty == []


def test_check_missing_required_key():
    result = check_vars({"A": "1"}, required=["A", "B"])
    assert not result.passed
    assert "B" in result.missing


def test_check_empty_value_flagged_by_default():
    result = check_vars({"A": ""}, required=["A"])
    assert not result.passed
    assert "A" in result.empty
    assert "A" not in result.missing


def test_check_empty_value_allowed_when_flag_set():
    result = check_vars({"A": ""}, required=["A"], allow_empty=True)
    assert result.passed
    assert result.empty == []


def test_check_no_required_keys_passes():
    result = check_vars({"X": "val"})
    assert result.passed


def test_check_empty_vault_with_required_raises_missing():
    result = check_vars({}, required=["DB_URL", "SECRET"])
    assert sorted(result.missing) == ["DB_URL", "SECRET"]


# ---------------------------------------------------------------------------
# check_vars – allowed list / unexpected
# ---------------------------------------------------------------------------

def test_check_unexpected_key_flagged():
    result = check_vars({"A": "1", "Z": "2"}, allowed=["A"])
    assert "Z" in result.unexpected
    assert result.has_warnings


def test_check_no_unexpected_when_all_allowed():
    result = check_vars({"A": "1", "B": "2"}, allowed=["A", "B"])
    assert result.unexpected == []
    assert not result.has_warnings


def test_check_allowed_none_skips_unexpected_check():
    result = check_vars({"ANYTHING": "x"}, allowed=None)
    assert result.unexpected == []


def test_check_result_sorted():
    result = check_vars({}, required=["Z", "A", "M"])
    assert result.missing == sorted(result.missing)


# ---------------------------------------------------------------------------
# format_result
# ---------------------------------------------------------------------------

def test_format_result_all_passed():
    result = CheckResult()
    output = format_result(result)
    assert "All checks passed" in output


def test_format_result_shows_missing():
    result = CheckResult(missing=["DB_URL"])
    output = format_result(result)
    assert "DB_URL" in output
    assert "Missing" in output


def test_format_result_shows_empty():
    result = CheckResult(empty=["SECRET"])
    output = format_result(result)
    assert "SECRET" in output
    assert "empty" in output


def test_format_result_shows_unexpected():
    result = CheckResult(unexpected=["ROGUE_KEY"])
    output = format_result(result)
    assert "ROGUE_KEY" in output
    assert "Unexpected" in output


def test_format_result_combined():
    result = CheckResult(missing=["A"], empty=["B"], unexpected=["C"])
    output = format_result(result)
    assert "A" in output
    assert "B" in output
    assert "C" in output
