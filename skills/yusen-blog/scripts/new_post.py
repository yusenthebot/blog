#!/usr/bin/env python3
"""Scaffold a new blog post folder with its frontmatter and section skeleton.

  new_post.py SLUG --episode-dir DIR      a 科普 episode: reads 发布文案.md and the 横屏 film
  new_post.py SLUG --notes [--film FILE]  a 图文 post (from Xiaohongshu); --film adds a video

For an episode it fills title, tags, date (film mtime), duration (ffprobe) and episode number,
maps the film for the YouTube uploader, and writes contact sheets to .work/SLUG/.
Everything it cannot know is left as a TODO for the article pass; nothing is published.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

from blog_paths import EPISODES, FILM_MAP, POSTS, SLUG, WORK, check_root

SKELETON = """
<!-- TODO opening: the problem, why it is hard, what this article covers (no "这期视频") -->

## 问题与记号

<!-- TODO state, action, observation and objective as math -->

## 方法

<!-- TODO at least half the article: key equations, what each symbol means, the algorithm as ordered steps.
Place the block diagram here:
![alt](./fig-NAME.png "图注：先说图里是什么，再逐个面板解释；说明哪些部分是示意") -->

## 代表工作

<!-- TODO the line of papers, each linked inline: [Author et al., Year](https://arxiv.org/abs/...) -->

## 我们的实验

<!-- TODO setup (simulator, model, budget, seeds, hardware), a results table, interpretation, limitations.
Delete this section for a post without an experiment. -->

## 小结

<!-- TODO what to remember, open problems -->
"""


def section(md: str, name: str) -> str:
    m = re.search(rf"^##\s*{name}\s*\n(.*?)(?=^##\s|\Z)", md, re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else ""


def yaml_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def film_duration(film: Path) -> str:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(film)],
        capture_output=True,
        text=True,
        check=True,
    )
    secs = round(float(r.stdout.strip()))
    return f"{secs // 60}:{secs % 60:02d}"


def find_film(ep_dir: Path) -> Path:
    films = sorted((ep_dir / "成片").glob("*_横屏.mp4"))
    if len(films) != 1:
        raise SystemExit(f"expected one 成片/*_横屏.mp4 in {ep_dir}, found {len(films)}")
    return films[0]


def episode_meta(ep_dir: Path) -> dict:
    m = re.match(r"(\d+)_", ep_dir.name)
    if not m:
        raise SystemExit(f"episode folder should start with its number: {ep_dir.name}")
    copy = (ep_dir / "发布文案.md").read_text(encoding="utf-8")
    title = section(copy, "标题").splitlines()[0] if section(copy, "标题") else "TODO"
    tags = [t for t in re.findall(r"#(\S+)", section(copy, "话题标签")) if t != "科普"][:6]
    film = find_film(ep_dir)
    return {
        "episode": int(m.group(1)),
        "title": title,
        "description": "TODO 一到两句：这篇讲什么方法、哪些论文、我们的实验",
        "tags": tags or ["TODO"],
        "date": dt.date.fromtimestamp(film.stat().st_mtime).isoformat(),
        "duration": film_duration(film),
        "film": film,
    }


def frontmatter(meta: dict, series: str, video: bool) -> str:
    lines = [
        "---",
        f"title: {yaml_str(meta['title'])}",
        f"description: {yaml_str(meta['description'])}",
        f"date: {meta['date']}",
        f"series: {series}",
    ]
    if series == "kepu":
        lines.append(f"episode: {meta['episode']}")
    lines += [
        f"tags: [{', '.join(meta['tags'])}]",
        "cover: ./cover.jpg",
        "coverAlt: TODO 封面画面描述",
    ]
    if video and series == "notes":
        lines.append("video: true")
    if meta.get("duration"):
        lines.append(f'duration: "{meta["duration"]}"')
    lines.append("platforms: [douyin, tiktok]" if series == "kepu" else "platforms: [xiaohongshu]")
    lines += [
        "links:",
        '  - label: "TODO Authors (Year). Title."',
        "    url: https://arxiv.org/abs/0000.00000",
        "    note: TODO venue",
        "---",
    ]
    return "\n".join(lines) + "\n"


def map_film(slug: str, film: Path) -> None:
    films = json.loads(FILM_MAP.read_text(encoding="utf-8")) if FILM_MAP.is_file() else {}
    films[slug] = str(film)
    FILM_MAP.write_text(json.dumps(films, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"mapped film for YouTube: {FILM_MAP.relative_to(FILM_MAP.parents[2])}")


def contact_sheets(slug: str, film: Path) -> None:
    out = WORK / slug / "sheet-%02d.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(film),
            "-vf",
            "fps=1/4,scale=480:-1,tile=6x5",
            "-q:v",
            "4",
            str(out),
        ],
        check=True,
    )
    print(f"contact sheets: {out.parent}  (tile k is at k*4 s)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    kind = ap.add_mutually_exclusive_group(required=True)
    kind.add_argument("--episode-dir", type=Path, help=f"episode folder, e.g. {EPISODES}/07_...")
    kind.add_argument("--notes", action="store_true")
    ap.add_argument("--film", type=Path, help="notes: the post's film, if it has one")
    ap.add_argument("--date", help="notes: YYYY-MM-DD the post went out (default: today)")
    ap.add_argument("--title", help="notes: working title")
    a = ap.parse_args()

    check_root()
    if not SLUG.match(a.slug):
        raise SystemExit("slug must be lowercase words joined by hyphens, e.g. ep14-diffusion-policy")
    folder = POSTS / a.slug
    if folder.exists():
        raise SystemExit(f"{folder} already exists; edit it instead")

    if a.episode_dir:
        ep_dir = a.episode_dir.expanduser()
        if not ep_dir.is_dir():
            raise SystemExit(f"not a folder: {ep_dir}")
        meta, series, film = episode_meta(ep_dir), "kepu", None
        film = meta["film"]
    else:
        film = a.film.expanduser() if a.film else None
        if film and not film.is_file():
            raise SystemExit(f"film not found: {film}")
        meta = {
            "title": a.title or "TODO",
            "description": "TODO 一到两句：这篇讲什么方法、哪些论文、我们的结论",
            "tags": ["TODO"],
            "date": a.date or dt.date.today().isoformat(),
            "duration": film_duration(film) if film else None,
        }
        series = "notes"

    folder.mkdir(parents=True)
    (folder / "index.md").write_text(frontmatter(meta, series, bool(film)) + SKELETON, encoding="utf-8")
    print(f"created {folder / 'index.md'}")
    if film:
        map_film(a.slug, film)
        contact_sheets(a.slug, film)
    print(
        "next: cover.jpg and stills (frames.py), the figure (block-diagram-drawer), then the article", file=sys.stderr
    )


if __name__ == "__main__":
    main()
