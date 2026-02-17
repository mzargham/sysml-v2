"""Tests for project config loading."""

from sysml_v2.config import find_config, load_config


def test_find_config_returns_none_when_missing(tmp_path):
    assert find_config(tmp_path) is None


def test_find_config_finds_sysml_toml(tmp_path):
    (tmp_path / "sysml.toml").write_text("[server]\nbackend = 'flexo'\n")

    result = find_config(tmp_path)

    assert result is not None
    assert result.name == "sysml.toml"


def test_find_config_walks_up(tmp_path):
    (tmp_path / "sysml.toml").write_text("[server]\nbackend = 'flexo'\n")
    child = tmp_path / "models" / "sub"
    child.mkdir(parents=True)

    result = find_config(child)

    assert result is not None
    assert result.parent == tmp_path


def test_load_config_defaults(tmp_path):
    cfg = load_config(tmp_path)

    assert cfg.server.backend == "flexo"
    assert cfg.server.url == "http://localhost:8083"
    assert cfg.library.path == "lib/SysML-v2-Release"
    assert cfg.validate.mode == "local"


def test_load_config_reads_toml(tmp_path):
    (tmp_path / "sysml.toml").write_text(
        '[server]\nbackend = "gearshift"\nurl = "http://localhost:8080"\n'
    )

    cfg = load_config(tmp_path)

    assert cfg.server.backend == "gearshift"
    assert cfg.server.url == "http://localhost:8080"
