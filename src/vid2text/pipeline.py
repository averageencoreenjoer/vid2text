import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from . import media
from .engine import Engine
from .formats import OUTPUT_FORMATS
from .writers import write_json, write_txt


@dataclass
class Options:
    input_dir: Path
    output_dir: Path
    formats: tuple[str, ...] = ("txt", "json")
    language: str | None = None
    recursive: bool = True
    timestamps: bool = False
    overwrite: bool = False


@dataclass
class FileResult:
    source: str
    status: str  # done | skipped | failed
    message: str = ""


@dataclass
class Report:
    results: list[FileResult] = field(default_factory=list)

    def count(self, status: str) -> int:
        return sum(1 for r in self.results if r.status == status)


# Called with (files_done, files_total, current_file_name)
ProgressFn = Callable[[int, int, str], None]


def validate(opts: Options) -> None:
    if not opts.input_dir.is_dir():
        raise ValueError(f"Input folder does not exist: {opts.input_dir}")
    if not opts.formats or any(f not in OUTPUT_FORMATS for f in opts.formats):
        raise ValueError("Choose at least one output format: txt and/or json.")
    opts.output_dir.mkdir(parents=True, exist_ok=True)


def run(
    opts: Options,
    engine: Engine,
    on_progress: ProgressFn | None = None,
    cancel: threading.Event | None = None,
) -> Report:
    validate(opts)
    files = media.discover(opts.input_dir, opts.recursive)
    report = Report()
    notify = on_progress or (lambda *_: None)

    for index, source in enumerate(files):
        if cancel is not None and cancel.is_set():
            break
        notify(index, len(files), source.name)
        report.results.append(_convert_one(source, opts, engine))
    notify(len(report.results), len(files), "")
    return report


def _convert_one(source: Path, opts: Options, engine: Engine) -> FileResult:
    relative = source.relative_to(opts.input_dir)
    base = opts.output_dir / relative.with_suffix("")
    targets = {fmt: base.with_name(f"{base.name}.{fmt}") for fmt in opts.formats}

    if not opts.overwrite and all(t.exists() for t in targets.values()):
        return FileResult(str(relative), "skipped", "output already exists")

    audio = None
    try:
        audio = media.extract_audio(source)
        transcript = engine.transcribe(audio, opts.language)
        base.parent.mkdir(parents=True, exist_ok=True)
        if "txt" in targets:
            write_txt(transcript, targets["txt"], opts.timestamps)
        if "json" in targets:
            write_json(transcript, targets["json"], source)
        return FileResult(str(relative), "done")
    except Exception as exc:
        return FileResult(str(relative), "failed", str(exc))
    finally:
        if audio is not None:
            audio.unlink(missing_ok=True)
