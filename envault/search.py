"""Search and filter environment variables within a vault."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from typing import Dict, List, Optional


class SearchError(Exception):
    """Raised when a search operation fails."""


@dataclass
class SearchResult:
    key: str
    value: str
    match_type: str  # 'key', 'value', or 'both'


def search_vars(
    variables: Dict[str, str],
    pattern: str,
    *,
    search_keys: bool = True,
    search_values: bool = False,
    use_regex: bool = False,
    case_sensitive: bool = False,
) -> List[SearchResult]:
    """Search variables by key and/or value using glob or regex patterns."""
    if not pattern:
        raise SearchError("Search pattern must not be empty.")

    flags = 0 if case_sensitive else re.IGNORECASE

    def _matches(text: str) -> bool:
        if use_regex:
            try:
                return bool(re.search(pattern, text, flags))
            except re.error as exc:
                raise SearchError(f"Invalid regex pattern: {exc}") from exc
        needle = pattern if case_sensitive else pattern.lower()
        haystack = text if case_sensitive else text.lower()
        return fnmatch.fnmatch(haystack, needle) or needle in haystack

    results: List[SearchResult] = []
    for key, value in sorted(variables.items()):
        key_hit = search_keys and _matches(key)
        val_hit = search_values and _matches(value)
        if key_hit and val_hit:
            results.append(SearchResult(key=key, value=value, match_type="both"))
        elif key_hit:
            results.append(SearchResult(key=key, value=value, match_type="key"))
        elif val_hit:
            results.append(SearchResult(key=key, value=value, match_type="value"))

    return results


def format_results(results: List[SearchResult], *, show_match_type: bool = False) -> str:
    """Format search results as a human-readable string."""
    if not results:
        return "No matches found."
    lines = []
    for r in results:
        line = f"{r.key}={r.value}"
        if show_match_type:
            line += f"  [{r.match_type}]"
        lines.append(line)
    return "\n".join(lines)
