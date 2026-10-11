from vid2text import cli
from vid2text.cli import build_parser, main


def test_parser_defaults():
    args = build_parser().parse_args(["run", "in", "out"])
    assert args.model == "base" and args.formats is None and not args.overwrite


def test_run_command_end_to_end(tmp_path, clip_factory, fake_engine, monkeypatch, capsys):
    clip_factory("a.mp4")
    monkeypatch.setattr(cli, "WhisperEngine", lambda model: fake_engine)

    code = main(["run", str(tmp_path / "in"), str(tmp_path / "out"), "-f", "txt"])

    assert code == 0
    assert (tmp_path / "out" / "a.txt").exists()
    assert "1 converted" in capsys.readouterr().out


def test_missing_folder_exits_with_error(tmp_path, capsys, monkeypatch, fake_engine):
    monkeypatch.setattr(cli, "WhisperEngine", lambda model: fake_engine)
    assert main(["run", str(tmp_path / "nope"), str(tmp_path / "out")]) == 2
    assert "does not exist" in capsys.readouterr().err
