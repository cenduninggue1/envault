"""CLI entry point for envault."""

import click

from envault.vault import init_vault, load_vault, save_vault
from envault.export import export_variables, SUPPORTED_FORMATS as EXPORT_FORMATS
from envault.import_env import import_from_file, ImportError as EnvImportError

DEFAULT_VAULT = ".envault"


@click.group()
def cli():
    """envault — secure environment variable manager."""


@cli.command()
@click.option("--vault", default=DEFAULT_VAULT, help="Path to vault file.")
@click.password_option(prompt="Master password")
def init(vault, password):
    """Initialize a new vault."""
    try:
        init_vault(vault, password)
        click.echo(f"Vault initialized at {vault}")
    except FileExistsError:
        click.echo(f"Error: Vault already exists at {vault}", err=True)
        raise SystemExit(1)


@cli.command(name="set")
@click.argument("key")
@click.argument("value")
@click.option("--vault", default=DEFAULT_VAULT, help="Path to vault file.")
@click.password_option(prompt="Master password")
def set_var(key, value, vault, password):
    """Set an environment variable in the vault."""
    data = load_vault(vault, password)
    data[key] = value
    save_vault(vault, password, data)
    click.echo(f"Set {key}")


@cli.command(name="get")
@click.argument("key")
@click.option("--vault", default=DEFAULT_VAULT, help="Path to vault file.")
@click.password_option(prompt="Master password")
def get_var(key, vault, password):
    """Get an environment variable from the vault."""
    data = load_vault(vault, password)
    if key not in data:
        click.echo(f"Key not found: {key}", err=True)
        raise SystemExit(1)
    click.echo(data[key])


@cli.command(name="list")
@click.option("--vault", default=DEFAULT_VAULT, help="Path to vault file.")
@click.password_option(prompt="Master password")
def list_vars(vault, password):
    """List all variable names in the vault."""
    data = load_vault(vault, password)
    if not data:
        click.echo("No variables stored.")
    for key in sorted(data):
        click.echo(key)


@cli.command(name="export")
@click.option("--vault", default=DEFAULT_VAULT, help="Path to vault file.")
@click.option(
    "--format", "fmt", default="dotenv",
    type=click.Choice(list(EXPORT_FORMATS)), show_default=True,
    help="Output format.",
)
@click.password_option(prompt="Master password")
def export_vars(vault, fmt, password):
    """Export vault variables in the chosen format."""
    data = load_vault(vault, password)
    click.echo(export_variables(data, fmt))


@cli.command(name="import")
@click.argument("filepath")
@click.option("--vault", default=DEFAULT_VAULT, help="Path to vault file.")
@click.option(
    "--format", "fmt", default=None,
    type=click.Choice(["dotenv", "json", "shell"]),
    help="Source file format (auto-detected from extension if omitted).",
)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
@click.password_option(prompt="Master password")
def import_vars(filepath, vault, fmt, overwrite, password):
    """Import environment variables from a file into the vault."""
    try:
        incoming = import_from_file(filepath, fmt=fmt)
    except EnvImportError as exc:
        click.echo(f"Import error: {exc}", err=True)
        raise SystemExit(1)

    data = load_vault(vault, password)
    skipped = []
    for key, value in incoming.items():
        if key in data and not overwrite:
            skipped.append(key)
            continue
        data[key] = value

    save_vault(vault, password, data)
    imported = set(incoming) - set(skipped)
    click.echo(f"Imported {len(imported)} variable(s).")
    if skipped:
        click.echo(f"Skipped {len(skipped)} existing key(s): {', '.join(skipped)}")
        click.echo("Use --overwrite to replace existing keys.")
