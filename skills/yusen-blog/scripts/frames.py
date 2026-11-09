#!/usr/bin/env python3
"""Pull frames from an episode film with the blog's standard crops.

  frames.py sheet FILM [OUT]         contact sheet, one frame every 4 s, 6 x 5 tiles per sheet
  frames.py cover FILM TIME OUT      16:9 cover, 1600 x 900, subtitle band cropped away
  frames.py still FILM TIME OUT      article still, 1600 wide, subtitle band cropped away

TIME is seconds or mm:ss. The crops assume the series' 1920 x 1080 landscape films with
burned-in subtitles in the bottom band; look at every frame you keep.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from blog_paths import WORK

CROPS = {
    "cover": "crop=1600:900:200:0",
    "still": "crop=1920:930:0:0,scale=1600:-2",
}
SHEET = "fps=1/{every},scale=480:-1,tile=6x5"


def parse_time(t: str) -> float:
    if ":" in t:
        m, s = t.split(":", 1)
        return int(m) * 60 + float(s)
    return float(t)


def ffmpeg(args: list[str]) -> None:
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg not found on PATH")
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], capture_output=True, text=True, check=False
    )
    if r.returncode != 0:
        raise SystemExit(f"ffmpeg failed: {r.stderr.strip()}")


def video_size(film: Path) -> tuple[int, int]:
    r = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0:s=x",
            str(film),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    w, h = r.stdout.strip().split("x")
    return int(w), int(h)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=("sheet", "cover", "still"))
    ap.add_argument("film", type=Path)
    ap.add_argument("rest", nargs="*")
    ap.add_argument("--every", type=float, default=4, help="sheet: seconds between frames")
    a = ap.parse_args()

    film = a.film.expanduser()
    if not film.is_file():
        raise SystemExit(f"film not found: {film}")
    if video_size(film) != (1920, 1080):
        print(f"warning: {film.name} is {video_size(film)}, the crops assume 1920x1080", file=sys.stderr)

    if a.mode == "sheet":
        out = Path(a.rest[0]) if a.rest else WORK / film.stem / "sheet-%02d.jpg"
        out.parent.mkdir(parents=True, exist_ok=True)
        ffmpeg(["-i", str(film), "-vf", SHEET.format(every=a.every), "-q:v", "4", str(out)])
        print(
            f"sheets in {out.parent}: tile k (from 0, row by row) is at k*{a.every:g} s, {int(a.every * 30)} s per sheet"
        )
        return

    if len(a.rest) != 2:
        raise SystemExit(f"{a.mode} needs TIME OUT")
    t, out = parse_time(a.rest[0]), Path(a.rest[1]).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg(["-ss", f"{t:.3f}", "-i", str(film), "-frames:v", "1", "-vf", CROPS[a.mode], "-q:v", "3", str(out)])
    print(out)


if __name__ == "__main__":
    main()
