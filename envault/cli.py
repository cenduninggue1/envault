"""Main CLI entry-point for envault."""

from __future__ import annotations

import click

from envault.audit import record_event
from envault.cli_audit import audit_group
from envault.cli_rotate import rotate_group
from envault.cli_search import search_group
from envault.cli_share import share_group
from envault.cli_snapshot import snapshot_group
from envault.cli_tag import tag_group
from envault.cli_template import template_group
from envault.export import export_variables
from envault.import_env import import_variables
from envault.vault import init_vault, load_vault, save_vault


@click.group()
def cli() -> None:
    """envault — secure environment variable manager."""


# ---------------------------------------------------------------------------
# Sub-command groups
# ---------------------------------------------------------------------------
cli.add_command(audit_group)
cli.add_command(rotate_group)
cli.add_command(search_group)
cli.add_command(share_group)
cli.add_command(snapshot_group)
cli.add_command(tag_group)
cli.add_command(template_group)


# ---------------------------------------------------------------------------
# Core commands
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--vault-dir", default=None, hidden=True)
def init(password: str, vault_dir: str | None) -> None:
    """Initialise a new vault in the current directory."""
    from pathlib import Path
    vdir = Path(vault_dir) if vault_dir else Path.cwd()
    try:
        init_vault(vdir, password)
    except FileExistsError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo("Vault initialised.")


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--vault-dir", default=None, hidden=True)
def set_var(key: str, value: str, password: str, vault_dir: str | None) -> None:
    """Set a variable in the vault."""
    from pathlib import Path
    vdir = Path(vault_dir) if vault_dir else Path.cwd()
    try:
        variables = load_vault(vdir, password)
        variables[key] = value
        save_vault(vdir, password, variables)
        record_event(vdir, "set", {"key": key})
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Set {key}.")


@cli.command("get")
@click.argument("key")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--vault-dir", default=None, hidden=True)
def get_var(key: str, password: str, vault_dir: str | None) -> None:
    """Get a variable from the vault."""
    from pathlib import Path
    vdir = Path(vault_dir) if vault_dir else Path.cwd()
    try:
        variables = load_vault(vdir, password)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc
    if key not in variables:
        raise click.ClickException(f"Variable '{key}' not found.")
    click.echo(variables[key])


@cli.command("list")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--vault-dir", default=None, hidden=True)
def list_vars(password: str, vault_dir: str | None) -> None:
    """List all variable names in the vault."""
    from pathlib import Path
    vdir = Path(vault_dir) if vault_dir else Path.cwd()
    try:
        variables = load_vault(vdir, password)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc
    if not variables:
        click.echo("No variables stored.")
        return
    for k in sorted(variables):
        click.echo(k)


@cli.command("export")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--format", "fmt", default="dotenv", show_default=True)
@click.option("--vault-dir", default=None, hidden=True)
def export_cmd(password: str, fmt: str, vault_dir: str | None) -> None:
    """Export vault variables in the chosen format."""
    from pathlib import Path
    vdir = Path(vault_dir) if vault_dir else Path.cwd()
    try:
        variables = load_vault(vdir, password)
        output = export_variables(variables, fmt)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc
    click.echo(output)


@cli.command("import")
@click.argument("import_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--password", prompt=True, hide_input=True)
@click.option("--format", "fmt", default="dotenv", show_default=True)
@click.option("--vault-dir", default=None, hidden=True)
def import_cmd(import_file: str, password: str, fmt: str, vault_dir: str | None) -> None:
    """Import variables from a file into the vault."""
    from pathlib import Path
    vdir = Path(vault_dir) if vault_dir else Path.cwd()
    try:
        count = import_variables(vdir, password, import_file, fmt)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Imported {count} variable(s).")
