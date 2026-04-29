"""Tests for envault.share (export/import bundle)."""

import os
import pytest
from click.testing import CliRunner

from envault.vault import init_vault, save_vault, load_vault
from envault.share import export_bundle, import_bundle, ShareError
from envault.cli_share import share_group


PASSWORD = "test-secret"


@pytest.fixture()
def vault_dir(tmp_path):
    d = str(tmp_path)
    init_vault(d, PASSWORD)
    save_vault(d, PASSWORD, {"KEY1": "value1", "KEY2": "value2"})
    return d


def test_export_bundle_returns_string(vault_dir):
    bundle = export_bundle(vault_dir, PASSWORD)
    assert isinstance(bundle, str)
    assert len(bundle) > 0


def test_export_import_roundtrip(vault_dir, tmp_path):
    bundle = export_bundle(vault_dir, PASSWORD)

    dest = str(tmp_path / "dest")
    os.makedirs(dest)
    init_vault(dest, PASSWORD)

    count = import_bundle(dest, bundle, PASSWORD)
    assert count == 2
    variables = load_vault(dest, PASSWORD)
    assert variables["KEY1"] == "value1"
    assert variables["KEY2"] == "value2"


def test_import_with_different_bundle_password(vault_dir, tmp_path):
    bundle_pw = "bundle-only-pw"
    bundle = export_bundle(vault_dir, PASSWORD, bundle_password=bundle_pw)

    dest = str(tmp_path / "dest")
    os.makedirs(dest)
    init_vault(dest, PASSWORD)

    count = import_bundle(dest, bundle, PASSWORD, bundle_password=bundle_pw)
    assert count == 2


def test_import_wrong_bundle_password_raises(vault_dir, tmp_path):
    bundle = export_bundle(vault_dir, PASSWORD, bundle_password="correct")
    dest = str(tmp_path / "dest")
    os.makedirs(dest)
    init_vault(dest, PASSWORD)

    with pytest.raises(ShareError, match="decrypt"):
        import_bundle(dest, bundle, PASSWORD, bundle_password="wrong")


def test_import_overwrite_false_preserves_existing(vault_dir, tmp_path):
    dest = str(tmp_path / "dest")
    os.makedirs(dest)
    init_vault(dest, PASSWORD)
    save_vault(dest, PASSWORD, {"KEY1": "original"})

    bundle = export_bundle(vault_dir, PASSWORD)
    import_bundle(dest, bundle, PASSWORD, overwrite=False)

    variables = load_vault(dest, PASSWORD)
    assert variables["KEY1"] == "original"  # not overwritten
    assert variables["KEY2"] == "value2"    # new key added


def test_import_overwrite_true_replaces_existing(vault_dir, tmp_path):
    dest = str(tmp_path / "dest")
    os.makedirs(dest)
    init_vault(dest, PASSWORD)
    save_vault(dest, PASSWORD, {"KEY1": "original"})

    bundle = export_bundle(vault_dir, PASSWORD)
    import_bundle(dest, bundle, PASSWORD, overwrite=True)

    variables = load_vault(dest, PASSWORD)
    assert variables["KEY1"] == "value1"  # overwritten


def test_import_malformed_bundle_raises(vault_dir):
    with pytest.raises(ShareError, match="Malformed"):
        import_bundle(vault_dir, "not-a-valid-bundle!!", PASSWORD)


def test_cli_export_and_import(vault_dir, tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        share_group,
        ["export", "--vault-dir", vault_dir, "--password", PASSWORD],
    )
    assert result.exit_code == 0
    bundle = result.output.strip()

    dest = str(tmp_path / "dest")
    os.makedirs(dest)
    init_vault(dest, PASSWORD)

    result2 = runner.invoke(
        share_group,
        ["import", bundle, "--vault-dir", dest, "--password", PASSWORD],
    )
    assert result2.exit_code == 0
    assert "2 variable(s)" in result2.output
