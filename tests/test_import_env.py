"""Tests for envault/import_env.py"""

import json
import pytest
from pathlib import Path

from envault.import_env import (
    parse_dotenv,
    parse_json,
    parse_shell,
    import_variables,
    import_from_file,
    SUPPORTED_FORMATS,
    ImportError,
)


def test_supported_formats_contains_expected():
    assert "dotenv" in SUPPORTED_FORMATS
    assert "json" in SUPPORTED_FORMATS
    assert "shell" in SUPPORTED_FORMATS


def test_parse_dotenv_basic():
    content = "KEY=value\nANOTHER=hello"
    result = parse_dotenv(content)
    assert result == {"KEY": "value", "ANOTHER": "hello"}


def test_parse_dotenv_strips_quotes():
    content = 'KEY="quoted value"\nOTHER=\'single\''
    result = parse_dotenv(content)
    assert result["KEY"] == "quoted value"
    assert result["OTHER"] == "single"


def test_parse_dotenv_ignores_comments_and_blanks():
    content = "# comment\n\nKEY=value"
    result = parse_dotenv(content)
    assert result == {"KEY": "value"}


def test_parse_dotenv_invalid_line_raises():
    with pytest.raises(ImportError, match="Invalid syntax"):
        parse_dotenv("BADLINE")


def test_parse_json_basic():
    content = json.dumps({"DB_HOST": "localhost", "PORT": 5432})
    result = parse_json(content)
    assert result == {"DB_HOST": "localhost", "PORT": "5432"}


def test_parse_json_invalid_raises():
    with pytest.raises(ImportError, match="Invalid JSON"):
        parse_json("not json")


def test_parse_json_non_dict_raises():
    with pytest.raises(ImportError, match="root must be"):
        parse_json(json.dumps(["a", "b"]))


def test_parse_shell_with_export():
    content = "export DB_URL=postgres://localhost/mydb\nexport SECRET=abc123"
    result = parse_shell(content)
    assert result == {"DB_URL": "postgres://localhost/mydb", "SECRET": "abc123"}


def test_parse_shell_without_export():
    content = "KEY=value"
    result = parse_shell(content)
    assert result == {"KEY": "value"}


def test_import_variables_unsupported_format():
    with pytest.raises(ImportError, match="Unsupported format"):
        import_variables("KEY=val", "xml")


def test_import_from_file_dotenv(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("APP_ENV=production\nDEBUG=false")
    result = import_from_file(str(env_file))
    assert result == {"APP_ENV": "production", "DEBUG": "false"}


def test_import_from_file_json(tmp_path):
    json_file = tmp_path / "vars.json"
    json_file.write_text(json.dumps({"HOST": "127.0.0.1"}))
    result = import_from_file(str(json_file))
    assert result == {"HOST": "127.0.0.1"}


def test_import_from_file_not_found():
    with pytest.raises(ImportError, match="File not found"):
        import_from_file("/nonexistent/path/.env")


def test_import_from_file_unknown_extension(tmp_path):
    txt_file = tmp_path / "vars.txt"
    txt_file.write_text("KEY=val")
    with pytest.raises(ImportError, match="Cannot auto-detect"):
        import_from_file(str(txt_file))


def test_import_from_file_explicit_format(tmp_path):
    txt_file = tmp_path / "vars.txt"
    txt_file.write_text("KEY=val")
    result = import_from_file(str(txt_file), fmt="dotenv")
    assert result == {"KEY": "val"}
