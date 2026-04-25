"""Export vault contents to various formats."""

import json
from typing import Optional


SUPPORTED_FORMATS = ("dotenv", "json", "shell")


def export_dotenv(variables: dict) -> str:
    """Export variables as a .env file format."""
    lines = []
    for key, value in sorted(variables.items()):
        # Escape double quotes in value
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + ("\n" if lines else "")


def export_json(variables: dict, indent: int = 2) -> str:
    """Export variables as a JSON object."""
    return json.dumps(variables, indent=indent, sort_keys=True) + "\n"


def export_shell(variables: dict) -> str:
    """Export variables as shell export statements."""
    lines = []
    for key, value in sorted(variables.items()):
        escaped = value.replace("'", "'\\''")
        lines.append(f"export {key}='{escaped}'")
    return "\n".join(lines) + ("\n" if lines else "")


def export_variables(variables: dict, fmt: str) -> str:
    """Export variables in the specified format.

    Args:
        variables: Dictionary of environment variable key-value pairs.
        fmt: Output format — one of 'dotenv', 'json', or 'shell'.

    Returns:
        Formatted string representation of the variables.

    Raises:
        ValueError: If the format is not supported.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )
    if fmt == "dotenv":
        return export_dotenv(variables)
    if fmt == "json":
        return export_json(variables)
    if fmt == "shell":
        return export_shell(variables)
