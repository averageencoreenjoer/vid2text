import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

MODEL_CHOICES = ("tiny", "base", "small", "medium", "large-v3")


@dataclass(frozen=True)
class Segment:
    start: float
    end: float
    text: str


@dataclass(frozen=True)
class Transcript:
    language: str
    duration: float
    segments: list[Segment]

    @property
    def text(self) -> str:
        return " ".join(s.text.strip() for s in self.segments if s.text.strip())


class Engine(Protocol):
    def transcribe(self, audio: Path, language: str | None) -> Transcript: ...


class WhisperEngine:
    """Thin wrapper around faster-whisper. The model is loaded on first use and then reused."""

    def __init__(self, model_name: str = "base", model_dir: str | None = None):
        self.model_name = model_name
        self.model_dir = model_dir
        self._model = None

    def _load(self):
        if self._model is None:
            from faster_whisper import WhisperModel
            self._model = WhisperModel(
                self.model_name, device="auto", compute_type="auto", download_root=self.model_dir
            )
        return self._model

    def transcribe(self, audio: Path, language: str | None = None) -> Transcript:
        model = self._load()
        samples = _read_wav(audio)
        raw_segments, info = model.transcribe(samples, language=language, vad_filter=True)
        # raw_segments is a generator: the model actually runs while we iterate
        segments = [Segment(s.start, s.end, s.text.strip()) for s in raw_segments]
        return Transcript(info.language, info.duration, segments)



def _read_wav(path: Path):
    """Load the 16 kHz mono WAV made by media.extract_audio as float samples in [-1, 1].

    Handing the model an array avoids its built-in decoder, which breaks on some PyAV versions.
    """
    import numpy as np

    with wave.open(str(path), "rb") as handle:
        frames = handle.readframes(handle.getnframes())
    return np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
