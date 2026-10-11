import os
from collections.abc import Callable
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .. import __version__
from ..engine import MODEL_CHOICES, Engine, WhisperEngine
from ..formats import MEDIA_EXTENSIONS, OUTPUT_FORMATS
from ..jobs import JobManager
from ..pipeline import Options

STATIC_DIR = Path(__file__).parent / "static"


class JobRequest(BaseModel):
    input_dir: str
    output_dir: str
    formats: list[str] = ["txt", "json"]
    model: str = "base"
    language: str | None = None
    recursive: bool = True
    timestamps: bool = False
    overwrite: bool = False


def _allowed_roots() -> list[Path]:
    raw = os.environ.get("VID2TEXT_ROOTS", "")
    return [Path(p).resolve() for p in raw.split(os.pathsep) if p]


def _inside_roots(path: Path, roots: list[Path]) -> bool:
    return not roots or any(path == r or r in path.parents for r in roots)


def _check_allowed(path: Path) -> Path:
    path = path.expanduser().resolve()
    if not _inside_roots(path, _allowed_roots()):
        raise HTTPException(403, "That location is not available in this setup.")
    return path


def create_app(engine_factory: Callable[[str], Engine] | None = None) -> FastAPI:
    model_dir = os.environ.get("VID2TEXT_MODEL_DIR")
    factory = engine_factory or (lambda name: WhisperEngine(name, model_dir))
    jobs = JobManager(factory)
    app = FastAPI(title="vid2text", version=__version__)

    @app.get("/api/config")
    def config():
        roots = _allowed_roots()
        return {
            "version": __version__,
            "models": list(MODEL_CHOICES),
            "extensions": sorted(MEDIA_EXTENSIONS),
            "input_dir": os.environ.get("VID2TEXT_INPUT", ""),
            "output_dir": os.environ.get("VID2TEXT_OUTPUT", ""),
            "home": str(roots[0] if roots else Path.home()),
        }

    @app.get("/api/browse")
    def browse(path: str = ""):
        roots = _allowed_roots()
        start = Path(path) if path else (roots[0] if roots else Path.home())
        folder = _check_allowed(start)
        if not folder.is_dir():
            raise HTTPException(404, "Folder not found.")
        try:
            children = list(folder.iterdir())
        except PermissionError:
            raise HTTPException(403, "No permission to open this folder.") from None
        entries = sorted(
            (p for p in children if p.is_dir() and not p.name.startswith(".")),
            key=lambda p: p.name.lower(),
        )
        media_count = sum(
            1 for p in children if p.is_file() and p.suffix.lower() in MEDIA_EXTENSIONS
        )
        parent = folder.parent if folder.parent != folder else None
        if parent is not None and not _inside_roots(parent, roots):
            parent = None
        return {
            "path": str(folder),
            "parent": str(parent) if parent else None,
            "dirs": [{"name": p.name, "path": str(p)} for p in entries],
            "media_files": media_count,
        }

    @app.post("/api/jobs", status_code=202)
    def start_job(req: JobRequest):
        if req.model not in MODEL_CHOICES:
            raise HTTPException(400, f"Unknown model: {req.model}")
        if not req.input_dir.strip() or not req.output_dir.strip():
            raise HTTPException(400, "Please choose both an input and an output folder.")
        formats = tuple(f for f in req.formats if f in OUTPUT_FORMATS)
        opts = Options(
            input_dir=_check_allowed(Path(req.input_dir)),
            output_dir=_check_allowed(Path(req.output_dir)),
            formats=formats,
            language=(req.language or None),
            recursive=req.recursive,
            timestamps=req.timestamps,
            overwrite=req.overwrite,
        )
        try:
            jobs.start(opts, req.model)
        except (ValueError, RuntimeError) as exc:
            raise HTTPException(400, str(exc)) from None
        return jobs.snapshot()

    @app.get("/api/jobs/current")
    def current_job():
        return jobs.snapshot()

    @app.post("/api/jobs/cancel")
    def cancel_job():
        jobs.cancel()
        return jobs.snapshot()

    @app.get("/")
    def index():
        return FileResponse(STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.state.jobs = jobs
    return app
