import json
from pathlib import Path

from .engine import Transcript


def _stamp(seconds: float) -> str:
    total = int(seconds)
    return f"{total // 3600:02d}:{total % 3600 // 60:02d}:{total % 60:02d}"


def write_txt(transcript: Transcript, target: Path, timestamps: bool = False) -> None:
    lines = []
    for seg in transcript.segments:
        text = seg.text.strip()
        if not text:
            continue
        lines.append(f"[{_stamp(seg.start)}] {text}" if timestamps else text)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json(transcript: Transcript, target: Path, source: Path) -> None:
    payload = {
        "source": source.name,
        "language": transcript.language,
        "duration": round(transcript.duration, 2),
        "text": transcript.text,
        "segments": [
            {"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()}
            for s in transcript.segments
        ],
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
