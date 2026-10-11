import pytest

from vid2text import media
from vid2text.formats import MEDIA_EXTENSIONS


def test_discover_filters_by_extension_and_recurses(tmp_path):
    (tmp_path / "a.mp4").write_bytes(b"x")
    (tmp_path / "notes.txt").write_bytes(b"x")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.MKV").write_bytes(b"x")

    names = [p.name for p in media.discover(tmp_path)]
    assert names == ["a.mp4", "b.MKV"]


def test_discover_non_recursive(tmp_path):
    (tmp_path / "a.mp4").write_bytes(b"x")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.mp4").write_bytes(b"x")
    assert [p.name for p in media.discover(tmp_path, recursive=False)] == ["a.mp4"]


def test_common_formats_are_supported():
    for ext in (".mp4", ".mov", ".mkv", ".avi", ".webm", ".wmv", ".flv", ".mp3", ".wav"):
        assert ext in MEDIA_EXTENSIONS


@pytest.mark.parametrize("ext", [".mp4", ".mkv", ".avi", ".webm", ".mov"])
def test_extract_audio_from_real_containers(clip_factory, ext):
    clip = clip_factory(f"clip{ext}")
    wav = media.extract_audio(clip)
    try:
        assert wav.exists() and wav.stat().st_size > 1000
    finally:
        wav.unlink()


def test_extract_audio_reports_silent_video(clip_factory):
    clip = clip_factory("mute.mp4", with_audio=False)
    with pytest.raises(media.MediaError):
        media.extract_audio(clip)
