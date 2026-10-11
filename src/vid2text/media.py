import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .formats import MEDIA_EXTENSIONS


class MediaError(RuntimeError):
    pass


def find_ffmpeg() -> str:
    """Prefer an ffmpeg already on PATH, otherwise use the copy bundled with imageio-ffmpeg."""
    system = shutil.which("ffmpeg")
    if system:
        return system
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:
        raise MediaError("ffmpeg not found. Install it or `pip install imageio-ffmpeg`.") from exc


def discover(folder: Path, recursive: bool = True) -> list[Path]:
    """Return every supported media file under `folder`, sorted for stable ordering."""
    walker = folder.rglob("*") if recursive else folder.glob("*")
    found = [p for p in walker if p.is_file() and p.suffix.lower() in MEDIA_EXTENSIONS]
    return sorted(found, key=lambda p: str(p).lower())


def extract_audio(source: Path) -> Path:
    """Decode the audio track to a 16 kHz mono WAV, the format speech models expect."""
    fd, name = tempfile.mkstemp(suffix=".wav", prefix="vid2text_")
    os.close(fd)
    target = Path(name)
    cmd = [
        find_ffmpeg(), "-y", "-v", "error", "-i", str(source),
        "-vn", "-ac", "1", "-ar", "16000", "-f", "wav", str(target),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or target.stat().st_size == 0:
        target.unlink(missing_ok=True)
        lines = result.stderr.strip().splitlines()
        detail = lines[-1] if lines else "no audio track?"
        raise MediaError(f"Could not read audio from {source.name}: {detail}")
    return target
