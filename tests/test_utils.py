import sys

from xautic.main import _all_possible_paths
from xautic.main import _get_args_for_reloading


def test_ignore_patterns():
    paths = _all_possible_paths(set(), set())
    assert any(p.startswith(sys.prefix) for p in paths)
    paths = _all_possible_paths(set(), {f"{sys.prefix}*"})
    assert not any(p.startswith(sys.prefix) for p in paths)


def test_get_args_for_reloading(monkeypatch, tmp_path):
    argv = [str(tmp_path / "test.exe"), "run"]
    monkeypatch.setattr("sys.executable", str(tmp_path / "python.exe"))
    monkeypatch.setattr("sys.argv", argv)
    monkeypatch.setattr("__main__.__package__", None)
    monkeypatch.setattr("os.name", "nt")
    args = _get_args_for_reloading()
    assert args == argv
