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
    p.add_argument("-V", "--version", action="version", version=f"tidy {VERSION}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.mode:
        build_parser().print_help()
        return 0
    print("sorting is not implemented yet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
