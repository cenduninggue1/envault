"""CLI commands for vault sharing (export-bundle / import-bundle)."""

import os
import sys
import click

from envault.share import export_bundle, import_bundle, ShareError


def _resolve_vault_dir(vault_dir: str) -> str:
    return vault_dir or os.getcwd()


@click.group(name="share")
def share_group():
    """Export and import encrypted vault bundles."""


@share_group.command("export")
@click.option("--vault-dir", default="", help="Path to vault directory.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--bundle-password", default=None, hide_input=True, help="Override bundle encryption password.")
@click.option("--output", "-o", default=None, help="Write bundle to file instead of stdout.")
def export_bundle_cmd(vault_dir, password, bundle_password, output):
    """Export vault as a portable encrypted bundle."""
    vault_dir = _resolve_vault_dir(vault_dir)
    try:
        bundle = export_bundle(vault_dir, password, bundle_password)
    except ShareError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if output:
        with open(output, "w") as fh:
            fh.write(bundle)
        click.echo(f"Bundle written to {output}")
    else:
        click.echo(bundle)


@share_group.command("import")
@click.argument("bundle_source")
@click.option("--vault-dir", default="", help="Path to vault directory.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--bundle-password", default=None, hide_input=True, help="Bundle decryption password if different.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
def import_bundle_cmd(bundle_source, vault_dir, password, bundle_password, overwrite):
    """Import variables from an encrypted bundle (file path or raw string)."""
    vault_dir = _resolve_vault_dir(vault_dir)

    if os.path.isfile(bundle_source):
        with open(bundle_source) as fh:
            bundle = fh.read().strip()
    else:
        bundle = bundle_source.strip()

    try:
        count = import_bundle(vault_dir, bundle, password, bundle_password, overwrite)
    except ShareError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    click.echo(f"Imported {count} variable(s) into vault at {vault_dir}")
