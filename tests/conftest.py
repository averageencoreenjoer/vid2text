import shutil
import subprocess
from pathlib import Path

import pytest

from vid2text.engine import Segment, Transcript
from vid2text.media import find_ffmpeg


class FakeEngine:
    """Stands in for the speech model so tests run in milliseconds and need no download."""

    def __init__(self, fail_on: str | None = None):
        self.fail_on = fail_on
        self.calls = 0

    def transcribe(self, audio, language):
        self.calls += 1
        if self.fail_on and self.fail_on in str(audio):
            raise RuntimeError("boom")
        return Transcript(
            language=language or "en",
            duration=4.0,
            segments=[Segment(0.0, 2.0, "Hello world."), Segment(2.0, 4.0, "Second line.")],
        )


@pytest.fixture
def fake_engine():
    return FakeEngine()


def make_clip(path: Path, with_audio: bool = True) -> Path:
    """Generate a one second test clip. The container is chosen by the file extension."""
    path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [find_ffmpeg(), "-y", "-v", "error", "-f", "lavfi", "-i", "color=c=blue:s=64x64:d=1"]
    if with_audio:
        cmd += ["-f", "lavfi", "-i", "sine=frequency=440:duration=1"]
    cmd += ["-shortest", str(path)]
    subprocess.run(cmd, check=True)
    return path


@pytest.fixture
def clip_factory(tmp_path):
    if not shutil.which("ffmpeg"):
        try:
            find_ffmpeg()
        except Exception:
            pytest.skip("ffmpeg is not available")
    return lambda name, **kw: make_clip(tmp_path / "in" / name, **kw)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    # The Docker image sets these; tests must not depend on where they run.
    for name in ("VID2TEXT_ROOTS", "VID2TEXT_INPUT", "VID2TEXT_OUTPUT", "VID2TEXT_MODEL_DIR"):
        monkeypatch.delenv(name, raising=False)
