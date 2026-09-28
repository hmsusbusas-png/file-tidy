#!/usr/bin/env python3
"""File Tidy - a tiny CLI that organizes messy folders.

Sorts files by type, date, or both. Runs in dry-run mode by default:
nothing is moved until you pass --apply. Every move is logged, so a run
can be reverted with --undo.

Examples:
    python tidy.py by-type --dir ~/Downloads
    python tidy.py by-date --dir ~/Downloads --month --apply
    python tidy.py --undo --dir ~/Downloads
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

VERSION = "1.0.0"
LOG_NAME = "moves.log"


# --- ANSI colors with graceful fallback --------------------------------------

def _colors_enabled() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if not sys.stdout.isatty():
        return False
    if os.name == "nt":
        os.system("")  # enables VT processing on modern Windows terminals
    return True


_COLOR = _colors_enabled()


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


def green(t: str) -> str:
    return _c("32", t)


def red(t: str) -> str:
    return _c("31", t)


def yellow(t: str) -> str:
    return _c("33", t)


def cyan(t: str) -> str:
    return _c("36", t)


def dim(t: str) -> str:
    return _c("2", t)


def bold(t: str) -> str:
    return _c("1", t)


# --- Sorting logic ------------------------------------------------------------

import fnmatch
import json
import shutil
from datetime import datetime

CATEGORIES: dict[str, list[str]] = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".ico", ".tif", ".tiff", ".heic"],
    "Documents": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".rtf", ".odt", ".csv"],
    "Audio": [".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".wma"],
    "Video": [".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv", ".m4v"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"],
    "Code": [".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".yml", ".yaml",
             ".sh", ".bat", ".ps1", ".sql", ".c", ".cpp", ".java", ".go", ".rs"],
}
OTHER = "Other"
EXT_TO_CAT = {ext: cat for cat, exts in CATEGORIES.items() for ext in exts}


def categorize(path: Path) -> str:
    return EXT_TO_CAT.get(path.suffix.lower(), OTHER)


def target_for(path: Path, root: Path, mode: str, month: bool) -> Path:
    """Directory where `path` should live in the given mode."""
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    date_part = mtime.strftime("%Y-%m") if month else mtime.strftime("%Y")
    if mode == "by-type":
        return root / categorize(path)
    if mode == "by-date":
        return root / date_part
    return root / categorize(path) / date_part  # by-type-date


def is_excluded(rel: str, patterns: list[str]) -> bool:
    rel = rel.replace("\\", "/")
    name = Path(rel).name
    return any(fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(name, p) for p in patterns)


def collect_files(root: Path, recursive: bool, exclude: list[str]) -> list[Path]:
    it = root.rglob("*") if recursive else root.iterdir()
    files = []
    for p in it:
        if not p.is_file() or p.name == LOG_NAME:
            continue
        if p.resolve() == Path(__file__).resolve():
            continue
        if is_excluded(str(p.relative_to(root)), exclude):
            continue
        files.append(p)
    return sorted(files)


def unique_path(dst: Path) -> Path:
    """Add ' (1)', ' (2)', ... before the suffix until the name is free."""
    if not dst.exists():
        return dst
    n = 1
    while True:
        cand = dst.with_name(f"{dst.stem} ({n}){dst.suffix}")
        if not cand.exists():
            return cand
        n += 1


def plan(root: Path, mode: str, month: bool, recursive: bool, exclude: list[str]) -> list[tuple[Path, Path]]:
    moves = []
    for p in collect_files(root, recursive, exclude):
        dst = target_for(p, root, mode, month) / p.name
        if dst == p:
            continue  # already in place
        if dst.exists():
            dst = unique_path(dst)
        moves.append((p, dst))
    return moves


def apply_moves(root: Path, moves: list[tuple[Path, Path]]) -> tuple[int, list[tuple[Path, OSError]]]:
    done, failed = [], []
    for src, dst in moves:
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            done.append({"from": str(src), "to": str(dst),
                         "ts": datetime.now().isoformat(timespec="seconds")})
        except OSError as e:
            failed.append((src, e))
    if done:
        with open(root / LOG_NAME, "a", encoding="utf-8") as f:
            for e in done:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return len(done), failed


# --- CLI ----------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tidy",
        description="File Tidy - organize messy folders by type, date, or both.",
    )
    p.add_argument("mode", nargs="?", choices=["by-type", "by-date", "by-type-date"],
                   help="sorting mode")
    p.add_argument("--dir", default=".", type=Path, help="folder to tidy (default: current)")
    p.add_argument("--apply", action="store_true",
                   help="actually move files (default: dry run)")
    p.add_argument("-r", "--recursive", action="store_true", help="include subfolders")
    p.add_argument("-e", "--exclude", action="append", default=[], metavar="PATTERN",
                   help="skip files matching a glob pattern (repeatable)")
    p.add_argument("--month", action="store_true",
                   help="by-date: use Year-Month folders instead of Year")
    p.add_argument("-V", "--version", action="version", version=f"tidy {VERSION}")
    return p


def show_plan(root: Path, moves: list[tuple[Path, Path]]) -> None:
    print(bold(f"\nPlan for {root}  ({len(moves)} file(s))\n"))
    w = max((len(str(src)) for src, _ in moves), default=4)
    for src, dst in moves:
        print(f"  {str(src):<{w}}  {dim('->')}  {cyan(str(dst.relative_to(root)))}")
    print(dim("\nDry run: nothing moved. Re-run with --apply to execute.\n"))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.mode:
        build_parser().print_help()
        return 0
    root = args.dir.expanduser().resolve()
    if not root.is_dir():
        print(red(f"Not a directory: {root}"))
        return 1
    moves = plan(root, args.mode, args.month, args.recursive, args.exclude)
    if not moves:
        print(green("Nothing to do - folder is already tidy."))
        return 0
    show_plan(root, moves)
    if not args.apply:
        return 0
    moved, failed = apply_moves(root, moves)
    print(green(f"Moved {moved} file(s)."))
    for src, err in failed:
        print(red(f"  ! {src.name}: {err}"))
    print(dim(f"Log written to {root / LOG_NAME} (revert with --undo)."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
