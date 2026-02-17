"""Tests for ``sysml init``."""

from click.testing import CliRunner

from sysml_v2.cli import main


def test_init_creates_project_structure(tmp_path):
    """sysml init should create the expected directory structure."""
    dest = tmp_path / "my-project"
    runner = CliRunner()
    result = runner.invoke(main, ["init", str(dest), "-y"])

    assert result.exit_code == 0, result.output

    # Core directories
    assert (dest / "models").is_dir()
    assert (dest / "models" / "examples").is_dir()
    assert (dest / "docker").is_dir()
    assert (dest / "notebooks").is_dir()
    assert (dest / ".vscode").is_dir()

    # Key files
    assert (dest / "pyproject.toml").is_file()
    assert (dest / "sysml.toml").is_file()
    assert (dest / ".gitignore").is_file()
    assert (dest / "Makefile").is_file()
    assert (dest / "docker" / "docker-compose.yml").is_file()
    assert (dest / "docker" / "cluster.trig").is_file()
    assert (dest / ".vscode" / "settings.json").is_file()
    assert (dest / ".vscode" / "extensions.json").is_file()
    assert (dest / "models" / "package.sysml").is_file()
    assert (dest / "models" / "examples" / "vehicle.sysml").is_file()
    assert (dest / "models" / "examples" / "requirements.sysml").is_file()


def test_init_substitutes_project_name(tmp_path):
    """The generated pyproject.toml should contain the project name."""
    dest = tmp_path / "satellite-model"
    runner = CliRunner()
    result = runner.invoke(main, ["init", str(dest), "-y"])

    assert result.exit_code == 0, result.output

    content = (dest / "pyproject.toml").read_text()
    assert 'name = "satellite-model"' in content


def test_init_default_flexo_backend(tmp_path):
    """sysml init should use the Flexo compose file by default."""
    dest = tmp_path / "flexo-project"
    runner = CliRunner()
    result = runner.invoke(main, ["init", str(dest), "-y"])

    assert result.exit_code == 0, result.output

    compose = dest / "docker" / "docker-compose.yml"
    assert compose.is_file()
    content = compose.read_text()
    assert "flexo" in content.lower()

    # Flexo compose should NOT include gearshift
    assert not (dest / "docker" / "docker-compose.gearshift.yml").exists()


def test_init_gearshift_backend(tmp_path):
    """sysml init --backend gearshift should use the gearshift compose file."""
    dest = tmp_path / "gs-project"
    runner = CliRunner()
    result = runner.invoke(main, ["init", str(dest), "--backend", "gearshift", "-y"])

    assert result.exit_code == 0, result.output

    compose = dest / "docker" / "docker-compose.yml"
    assert compose.is_file()
    content = compose.read_text()
    assert "gearshift" in content.lower()


def test_init_default_cwd(tmp_path, monkeypatch):
    """sysml init with no path should scaffold in the current directory."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["init", "-y"])

    assert result.exit_code == 0, result.output
    assert (tmp_path / "pyproject.toml").is_file()
    assert (tmp_path / "sysml.toml").is_file()
