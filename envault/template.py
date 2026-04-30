"""Template rendering: substitute vault variables into template strings or files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List


class TemplateError(Exception):
    """Raised when template rendering fails."""


_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


@dataclass
class RenderResult:
    output: str
    resolved: List[str]
    missing: List[str]


def render_template(template: str, variables: Dict[str, str], strict: bool = False) -> RenderResult:
    """Replace ``{{ KEY }}`` placeholders with values from *variables*.

    Args:
        template: The template string containing ``{{ KEY }}`` placeholders.
        variables: Mapping of variable names to values.
        strict: If *True*, raise :class:`TemplateError` when a placeholder has
                no matching variable.  Otherwise leave it unchanged.

    Returns:
        A :class:`RenderResult` with the rendered output and lists of resolved
        and missing variable names.
    """
    resolved: List[str] = []
    missing: List[str] = []

    def _replace(match: re.Match) -> str:  # type: ignore[type-arg]
        key = match.group(1)
        if key in variables:
            resolved.append(key)
            return variables[key]
        missing.append(key)
        if strict:
            raise TemplateError(f"Template variable not found in vault: '{key}'")
        return match.group(0)

    output = _PLACEHOLDER_RE.sub(_replace, template)
    return RenderResult(output=output, resolved=resolved, missing=missing)


def list_placeholders(template: str) -> List[str]:
    """Return a deduplicated, ordered list of placeholder names in *template*."""
    seen: dict[str, None] = {}
    for match in _PLACEHOLDER_RE.finditer(template):
        seen[match.group(1)] = None
    return list(seen)
