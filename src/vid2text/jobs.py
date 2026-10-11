import threading
from collections.abc import Callable
from dataclasses import asdict, dataclass, field

from . import pipeline
from .engine import Engine
from .pipeline import Options


@dataclass
class JobState:
    status: str = "idle"  # idle | running | finished | cancelled | error
    done: int = 0
    total: int = 0
    current: str = ""
    error: str = ""
    results: list[dict] = field(default_factory=list)


class JobManager:
    """Runs one conversion at a time in a background thread so the UI stays responsive."""

    def __init__(self, engine_factory: Callable[[str], Engine]):
        self._engine_factory = engine_factory
        self._lock = threading.Lock()
        self._state = JobState()
        self._cancel = threading.Event()
        self._thread: threading.Thread | None = None

    def snapshot(self) -> dict:
        with self._lock:
            return asdict(self._state)

    def start(self, opts: Options, model: str) -> None:
        with self._lock:
            if self._state.status == "running":
                raise RuntimeError("A conversion is already running.")
            pipeline.validate(opts)
            self._state = JobState(status="running")
            self._cancel.clear()
        self._thread = threading.Thread(target=self._work, args=(opts, model), daemon=True)
        self._thread.start()

    def cancel(self) -> None:
        self._cancel.set()

    def wait(self, timeout: float | None = None) -> None:
        if self._thread:
            self._thread.join(timeout)

    def _progress(self, done: int, total: int, current: str) -> None:
        with self._lock:
            self._state.done, self._state.total, self._state.current = done, total, current

    def _work(self, opts: Options, model: str) -> None:
        try:
            engine = self._engine_factory(model)
            report = pipeline.run(opts, engine, self._progress, self._cancel)
            with self._lock:
                self._state.results = [asdict(r) for r in report.results]
                self._state.current = ""
                self._state.status = "cancelled" if self._cancel.is_set() else "finished"
        except Exception as exc:
            with self._lock:
                self._state.status = "error"
                self._state.error = str(exc)
