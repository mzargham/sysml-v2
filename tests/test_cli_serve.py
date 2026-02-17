"""Tests for ``sysml serve``."""

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from sysml_v2.cli import main


def _make_project(tmp_path: Path) -> Path:
    """Create a minimal project directory with a docker-compose file."""
    docker_dir = tmp_path / "docker"
    docker_dir.mkdir()
    (docker_dir / "docker-compose.yml").write_text("services: {}")
    return tmp_path


def test_serve_status_no_compose(tmp_path, monkeypatch):
    """sysml serve status should error when no compose file is found."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["serve", "status"])

    assert result.exit_code != 0
    assert "No docker-compose file found" in result.output


@patch("sysml_v2.cli.serve.subprocess.run")
def test_serve_up_calls_docker_compose(mock_run, tmp_path, monkeypatch):
    """sysml serve up should call docker compose up -d."""
    project = _make_project(tmp_path)
    monkeypatch.chdir(project)
    mock_run.return_value.returncode = 0

    runner = CliRunner()
    runner.invoke(main, ["serve", "up"])

    mock_run.assert_called_once()
    cmd = mock_run.call_args[0][0]
    assert cmd[0:2] == ["docker", "compose"]
    assert "up" in cmd
    assert "-d" in cmd


@patch("sysml_v2.cli.serve.subprocess.run")
def test_serve_down_calls_docker_compose(mock_run, tmp_path, monkeypatch):
    """sysml serve down should call docker compose down."""
    project = _make_project(tmp_path)
    monkeypatch.chdir(project)
    mock_run.return_value.returncode = 0

    runner = CliRunner()
    runner.invoke(main, ["serve", "down"])

    mock_run.assert_called_once()
    cmd = mock_run.call_args[0][0]
    assert "down" in cmd
