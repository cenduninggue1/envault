"""CLI commands for searching vault variables."""

from __future__ import annotations

import os
from pathlib import Path

import click

from envault.search import SearchError, format_results, search_vars
from envault.vault import load_vault


def _resolve_vault_dir(vault_dir: Optional[str]) -> Path:
    if vault_dir:
        return Path(vault_dir)
    return Path(os.environ.get("ENVAULT_DIR", "."))


@click.group("search")
def search_group() -> None:
    """Search environment variables in the vault."""


@search_group.command("find")
@click.argument("pattern")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--vault-dir", default=None, help="Path to vault directory.")
@click.option("--keys/--no-keys", default=True, show_default=True, help="Search in keys.")
@click.option("--values/--no-values", default=False, show_default=True, help="Search in values.")
@click.option("--regex", is_flag=True, default=False, help="Treat pattern as a regular expression.")
@click.option("--case-sensitive", is_flag=True, default=False, help="Case-sensitive matching.")
@click.option("--show-match-type", is_flag=True, default=False, help="Show where the match occurred.")
def find_cmd(
    pattern: str,
    password: str,
    vault_dir: str | None,
    keys: bool,
    values: bool,
    regex: bool,
    case_sensitive: bool,
    show_match_type: bool,
) -> None:
    """Search vault variables matching PATTERN."""
    resolved = _resolve_vault_dir(vault_dir)
    try:
        variables = load_vault(resolved, password)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc

    if not keys and not values:
        raise click.ClickException("At least one of --keys or --values must be enabled.")

    try:
        results = search_vars(
            variables,
            pattern,
            search_keys=keys,
            search_values=values,
            use_regex=regex,
            case_sensitive=case_sensitive,
        )
    except SearchError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(format_results(results, show_match_type=show_match_type))
    if results:
        click.echo(f"\n{len(results)} match(es) found.", err=True)


# Allow Optional import without full typing import at module level
from typing import Optional  # noqa: E402
