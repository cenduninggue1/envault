"""Import environment variables from external sources into the vault."""

import json
import os
from pathlib import Path
from typing import Dict, Optional


class ImportError(Exception):
    """Raised when an import operation fails."""


def parse_dotenv(content: str) -> Dict[str, str]:
    """Parse a .env file content into a dictionary of key-value pairs."""
    variables = {}
    for line_num, line in enumerate(content.splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ImportError(f"Invalid syntax on line {line_num}: {line!r}")
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if not key:
            raise ImportError(f"Empty key on line {line_num}")
        # Strip surrounding quotes if present
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        variables[key] = value
    return variables


def parse_json(content: str) -> Dict[str, str]:
    """Parse a JSON file content into a dictionary of key-value pairs."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ImportError(f"Invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ImportError("JSON root must be an object/dictionary")
    result = {}
    for key, value in data.items():
        if not isinstance(key, str):
            raise ImportError(f"JSON keys must be strings, got: {type(key).__name__}")
        result[key] = str(value)
    return result


def parse_shell(content: str) -> Dict[str, str]:
    """Parse a shell export file into a dictionary of key-value pairs."""
    variables = {}
    for line_num, line in enumerate(content.splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            raise ImportError(f"Invalid syntax on line {line_num}: {line!r}")
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        variables[key] = value
    return variables


SUPPORTED_FORMATS = {
    "dotenv": parse_dotenv,
    "json": parse_json,
    "shell": parse_shell,
}


def import_variables(source: str, fmt: str) -> Dict[str, str]:
    """Parse environment variables from a string in the given format."""
    if fmt not in SUPPORTED_FORMATS:
        raise ImportError(
            f"Unsupported format: {fmt!r}. Choose from: {list(SUPPORTED_FORMATS)}"
        )
    return SUPPORTED_FORMATS[fmt](source)


def import_from_file(path: str, fmt: Optional[str] = None) -> Dict[str, str]:
    """Read and parse a file, auto-detecting format from extension if not given."""
    file_path = Path(path)
    if not file_path.exists():
        raise ImportError(f"File not found: {path}")
    if fmt is None:
        ext = file_path.suffix.lower()
        fmt = {'.env': 'dotenv', '.json': 'json', '.sh': 'shell'}.get(ext)
        if fmt is None:
            raise ImportError(
                f"Cannot auto-detect format for extension {ext!r}. Specify --format."
            )
    content = file_path.read_text(encoding="utf-8")
    return import_variables(content, fmt)
