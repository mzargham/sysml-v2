"""Tests for ``sysml validate``."""

from pathlib import Path

from click.testing import CliRunner

from sysml_v2.cli import main


def _write_sysml(tmp_path: Path, name: str, content: str) -> Path:
    """Write a .sysml file to tmp_path and return its path."""
    models_dir = tmp_path / "models"
    models_dir.mkdir(exist_ok=True)
    f = models_dir / name
    f.write_text(content)
    return f


def test_validate_no_files(tmp_path, monkeypatch):
    """sysml validate on an empty directory should report no files."""
    empty = tmp_path / "empty"
    empty.mkdir()
    runner = CliRunner()
    result = runner.invoke(main, ["validate", str(empty)])

    assert result.exit_code == 0
    assert "No .sysml files found" in result.output


def test_validate_finds_sysml_files(tmp_path):
    """sysml validate should discover .sysml files recursively."""
    from sysml_v2.parsing.loader import find_models

    models = tmp_path / "models"
    models.mkdir()
    (models / "a.sysml").write_text("package A {}")
    sub = models / "sub"
    sub.mkdir()
    (sub / "b.sysml").write_text("package B {}")

    found = find_models(models)
    assert len(found) == 2
    assert all(f.suffix == ".sysml" for f in found)
