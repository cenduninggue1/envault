"""Validate vault variables against expected schemas or required key sets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class CheckError(Exception):
    """Raised when a check operation fails unexpectedly."""


@dataclass
class CheckResult:
    missing: List[str] = field(default_factory=list)
    unexpected: List[str] = field(default_factory=list)
    empty: List[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not (self.missing or self.empty)

    @property
    def has_warnings(self) -> bool:
        return bool(self.unexpected)


def check_vars(
    variables: Dict[str, str],
    required: Optional[List[str]] = None,
    allowed: Optional[List[str]] = None,
    allow_empty: bool = False,
) -> CheckResult:
    """Check *variables* against *required* keys and an optional *allowed* allow-list.

    Args:
        variables: Mapping of key -> value currently in the vault.
        required: Keys that MUST be present (and non-empty unless *allow_empty*).
        allowed: If provided, keys NOT in this list are flagged as unexpected.
        allow_empty: When True, empty string values are not flagged.

    Returns:
        A :class:`CheckResult` describing any issues found.
    """
    required = list(required or [])
    result = CheckResult()

    for key in required:
        if key not in variables:
            result.missing.append(key)
        elif not allow_empty and variables[key] == "":
            result.empty.append(key)

    if allowed is not None:
        allowed_set = set(allowed)
        for key in variables:
            if key not in allowed_set:
                result.unexpected.append(key)

    result.missing.sort()
    result.unexpected.sort()
    result.empty.sort()
    return result


def format_result(result: CheckResult) -> str:
    """Return a human-readable summary of a :class:`CheckResult`."""
    lines: List[str] = []
    if result.passed and not result.has_warnings:
        lines.append("All checks passed.")
        return "\n".join(lines)

    if result.missing:
        lines.append("Missing required keys:")
        for k in result.missing:
            lines.append(f"  - {k}")

    if result.empty:
        lines.append("Keys present but empty:")
        for k in result.empty:
            lines.append(f"  - {k}")

    if result.unexpected:
        lines.append("Unexpected keys (not in allowed list):")
        for k in result.unexpected:
            lines.append(f"  ~ {k}")

    return "\n".join(lines)
