"""Tests for envault.export module."""

import json
import pytest

from envault.export import (
    export_variables,
    export_dotenv,
    export_json,
    export_shell,
    SUPPORTED_FORMATS,
)


SAMPLE_VARS = {
    "DATABASE_URL": "postgres://localhost/mydb",
    "SECRET_KEY": "s3cr3t",
    "DEBUG": "true",
}


def test_supported_formats_contains_expected():
    assert "dotenv" in SUPPORTED_FORMATS
    assert "json" in SUPPORTED_FORMATS
    assert "shell" in SUPPORTED_FORMATS


def test_export_dotenv_format():
    result = export_dotenv(SAMPLE_VARS)
    assert 'DATABASE_URL="postgres://localhost/mydb"' in result
    assert 'SECRET_KEY="s3cr3t"' in result
    assert result.endswith("\n")


def test_export_dotenv_escapes_double_quotes():
    result = export_dotenv({"MSG": 'say "hello"'})
    assert 'MSG="say \\"hello\\""' in result


def test_export_json_valid():
    result = export_json(SAMPLE_VARS)
    parsed = json.loads(result)
    assert parsed["SECRET_KEY"] == "s3cr3t"
    assert parsed["DEBUG"] == "true"


def test_export_json_sorted_keys():
    result = export_json(SAMPLE_VARS)
    parsed = json.loads(result)
    assert list(parsed.keys()) == sorted(parsed.keys())


def test_export_shell_format():
    result = export_shell(SAMPLE_VARS)
    assert "export SECRET_KEY='s3cr3t'" in result
    assert "export DEBUG='true'" in result
    assert result.endswith("\n")


def test_export_shell_escapes_single_quotes():
    result = export_shell({"VAR": "it's alive"})
    assert "export VAR='it'\\''s alive'" in result


def test_export_variables_dispatches_correctly():
    for fmt in SUPPORTED_FORMATS:
        result = export_variables(SAMPLE_VARS, fmt)
        assert isinstance(result, str)
        assert len(result) > 0


def test_export_variables_invalid_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        export_variables(SAMPLE_VARS, "xml")


def test_export_empty_variables():
    for fmt in SUPPORTED_FORMATS:
        result = export_variables({}, fmt)
        assert isinstance(result, str)
