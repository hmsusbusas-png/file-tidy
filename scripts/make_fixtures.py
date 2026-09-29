#!/usr/bin/env python3
"""Create a messy folder of sample files for tidy.py (default: ./tidy-demo)."""

import os
import sys
import time
from pathlib import Path

FILES = {
    "photo_vacation.jpg": (2023, 5, 14),
    "screenshot.png": (2024, 1, 3),
    "wallpaper.bmp": (2022, 11, 20),
    "resume.pdf": (2024, 3, 8),
    "notes.txt": (2023, 7, 21),
    "budget.xlsx": (2024, 6, 30),
    "report.docx": (2022, 2, 11),
    "song.mp3": (2023, 9, 5),
    "podcast_ep12.wav": (2024, 2, 18),
    "clip.mp4": (2023, 12, 1),
    "movie.mkv": (2024, 4, 22),
    "backup.zip": (2022, 8, 9),
    "photos_raw.7z": (2024, 5, 17),
    "script.py": (2023, 3, 27),
    "index.html": (2024, 7, 4),
    "data.json": (2023, 10, 12),
    "style.css": (2022, 5, 25),
    "mystery.xyz": (2024, 8, 15),
}


def main() -> None:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tidy-demo")
    target.mkdir(parents=True, exist_ok=True)
    for name, (y, m, d) in FILES.items():
        p = target / name
        p.write_bytes(b"placeholder")
        ts = time.mktime((y, m, d, 12, 0, 0, 0, 0, -1))
        os.utime(p, (ts, ts))
    print(f"Created {len(FILES)} files in {target.resolve()}")


if __name__ == "__main__":
    main()
