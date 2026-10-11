import argparse
import sys
import threading
import webbrowser
from pathlib import Path

from . import __version__
from .engine import MODEL_CHOICES, WhisperEngine
from .formats import OUTPUT_FORMATS
from .pipeline import Options, Report, run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vid2text", description="Convert video and audio files into text transcripts."
    )
    parser.add_argument("--version", action="version", version=f"vid2text {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    ui = sub.add_parser("serve", help="Start the web interface (default for most people).")
    ui.add_argument("--host", default="127.0.0.1")
    ui.add_argument("--port", type=int, default=8000)
    ui.add_argument("--no-browser", action="store_true", help="Do not open a browser tab.")

    batch = sub.add_parser("run", help="Convert a folder from the command line.")
    batch.add_argument("input_dir", type=Path)
    batch.add_argument("output_dir", type=Path)
    batch.add_argument("-f", "--format", action="append", choices=OUTPUT_FORMATS, dest="formats",
                       help="Output format; repeat for both. Default: txt and json.")
    batch.add_argument("-m", "--model", default="base", choices=MODEL_CHOICES)
    batch.add_argument("-l", "--language",
                       help="Language code such as en or ru. Default: auto-detect.")
    batch.add_argument("--no-recursive", action="store_true", help="Ignore sub-folders.")
    batch.add_argument("--timestamps", action="store_true",
                       help="Add [hh:mm:ss] to each TXT line.")
    batch.add_argument("--overwrite", action="store_true",
                       help="Redo files that already have output.")
    return parser


def _serve(args) -> int:
    import uvicorn

    from .web.app import create_app

    url = f"http://{args.host}:{args.port}"
    print(f"vid2text is running at {url}  (press Ctrl+C to stop)")
    if not args.no_browser:
        threading.Timer(1.0, webbrowser.open, args=(url,)).start()
    uvicorn.run(create_app(), host=args.host, port=args.port, log_level="warning")
    return 0


def _print_summary(report: Report) -> None:
    for r in report.results:
        mark = {"done": "ok", "skipped": "skip", "failed": "FAIL"}[r.status]
        extra = f" - {r.message}" if r.message else ""
        print(f"[{mark}] {r.source}{extra}")
    print(f"\n{report.count('done')} converted, {report.count('skipped')} skipped, "
          f"{report.count('failed')} failed")


def _batch(args) -> int:
    opts = Options(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        formats=tuple(args.formats or OUTPUT_FORMATS),
        language=args.language,
        recursive=not args.no_recursive,
        timestamps=args.timestamps,
        overwrite=args.overwrite,
    )

    def show(done: int, total: int, name: str) -> None:
        if name:
            print(f"({done + 1}/{total}) {name}", flush=True)

    try:
        report = run(opts, WhisperEngine(args.model), show)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    _print_summary(report)
    return 1 if report.count("failed") else 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return _serve(args) if args.command == "serve" else _batch(args)
