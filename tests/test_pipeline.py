import json
import threading

import pytest

from conftest import FakeEngine
from vid2text.pipeline import Options, run


def opts(tmp_path, **kw):
    return Options(input_dir=tmp_path / "in", output_dir=tmp_path / "out", **kw)


def test_converts_to_both_formats_and_mirrors_folders(tmp_path, clip_factory, fake_engine):
    clip_factory("one.mp4")
    clip_factory("nested/two.mkv")

    report = run(opts(tmp_path), fake_engine)

    assert report.count("done") == 2
    assert (tmp_path / "out" / "one.txt").read_text(encoding="utf-8").startswith("Hello world.")
    data = json.loads((tmp_path / "out" / "nested" / "two.json").read_text(encoding="utf-8"))
    assert data["source"] == "two.mkv"


def test_only_requested_formats_are_written(tmp_path, clip_factory, fake_engine):
    clip_factory("one.mp4")
    run(opts(tmp_path, formats=("json",)), fake_engine)
    assert (tmp_path / "out" / "one.json").exists()
    assert not (tmp_path / "out" / "one.txt").exists()


def test_existing_output_is_skipped_unless_overwrite(tmp_path, clip_factory, fake_engine):
    clip_factory("one.mp4")
    run(opts(tmp_path), fake_engine)
    assert fake_engine.calls == 1

    second = run(opts(tmp_path), fake_engine)
    assert second.count("skipped") == 1 and fake_engine.calls == 1

    run(opts(tmp_path, overwrite=True), fake_engine)
    assert fake_engine.calls == 2


def test_one_bad_file_does_not_stop_the_batch(tmp_path, clip_factory):
    clip_factory("good.mp4")
    (tmp_path / "in" / "broken.mp4").write_bytes(b"not a video")

    report = run(opts(tmp_path), FakeEngine())

    assert report.count("done") == 1
    assert report.count("failed") == 1


def test_cancel_stops_before_next_file(tmp_path, clip_factory, fake_engine):
    clip_factory("a.mp4")
    clip_factory("b.mp4")
    cancel = threading.Event()
    cancel.set()
    report = run(opts(tmp_path), fake_engine, cancel=cancel)
    assert report.results == []


def test_progress_is_reported(tmp_path, clip_factory, fake_engine):
    clip_factory("a.mp4")
    seen = []
    run(opts(tmp_path), fake_engine, lambda d, t, n: seen.append((d, t, n)))
    assert seen[0] == (0, 1, "a.mp4")
    assert seen[-1] == (1, 1, "")


def test_missing_input_folder_is_rejected(tmp_path, fake_engine):
    with pytest.raises(ValueError):
        run(opts(tmp_path), fake_engine)


def test_requires_at_least_one_format(tmp_path, fake_engine):
    (tmp_path / "in").mkdir()
    with pytest.raises(ValueError):
        run(opts(tmp_path, formats=()), fake_engine)
