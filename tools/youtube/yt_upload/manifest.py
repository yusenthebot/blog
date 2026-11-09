"""Build YouTube upload jobs from the blog's posts and a local map of film files.

The posts are the source of truth for title, description and tags; the
local map (git-ignored, machine-specific) only says where each film lives on disk.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

BLOG_URL = "https://yusenthebot.github.io/blog/posts/{slug}/"
TITLE_MAX = 100
DESCRIPTION_MAX_BYTES = 5000
TAGS_MAX_CHARS = 500
CATEGORY_SCIENCE_TECH = "28"
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
FORBIDDEN = re.compile(r"[<>]")


class ManifestError(ValueError):
    """A post or the local film map cannot produce a valid upload job."""


@dataclass(frozen=True)
class Post:
    slug: str
    path: Path
    data: dict


@dataclass(frozen=True)
class UploadJob:
    slug: str
    film: Path
    cover: Path | None
    title: str
    description: str
    tags: tuple[str, ...]
    category_id: str = CATEGORY_SCIENCE_TECH
    # The narration is the author's AI-cloned voice, which YouTube asks creators to disclose.
    synthetic_media: bool = True


def read_post(index_md: Path) -> Post:
    text = index_md.read_text(encoding="utf-8")
    m = FRONTMATTER.match(text)
    if not m:
        raise ManifestError(f"{index_md}: no frontmatter block")
    data = yaml.safe_load(m.group(1)) or {}
    if not isinstance(data, dict):
        raise ManifestError(f"{index_md}: frontmatter is not a mapping")
    return Post(slug=index_md.parent.name, path=index_md, data=data)


def load_posts(posts_dir: Path) -> list[Post]:
    return [read_post(p) for p in sorted(posts_dir.glob("*/index.md"))]


def load_film_map(path: Path) -> dict[str, Path]:
    """`{"<slug>": "/abs/path/film.mp4", ...}`; a missing file is an empty map."""
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not all(isinstance(v, str) for v in raw.values()):
        raise ManifestError(f"{path}: expected an object of slug -> film path")
    return {slug: Path(p).expanduser() for slug, p in raw.items()}


def _clean(s: str) -> str:
    return FORBIDDEN.sub("", s).strip()


def build_title(post: Post) -> str:
    title = _clean(str(post.data.get("title", "")))
    if not title:
        raise ManifestError(f"{post.slug}: empty title")
    ep = post.data.get("episode")
    if ep:
        title = f"{title} | EP{int(ep):02d}"
    if len(title) > TITLE_MAX:
        raise ManifestError(f"{post.slug}: title is {len(title)} chars, YouTube allows {TITLE_MAX}")
    return title


def build_tags(post: Post) -> tuple[str, ...]:
    tags: list[str] = []
    total = 0
    for t in post.data.get("tags", []) or []:
        t = _clean(str(t))
        cost = len(t) + (2 if " " in t else 0) + (1 if tags else 0)  # quotes for spaces, comma between
        if not t or total + cost > TAGS_MAX_CHARS:
            continue
        tags.append(t)
        total += cost
    return tuple(tags)


def build_description(post: Post) -> str:
    parts = [_clean(str(post.data.get("description", "")))]
    parts.append(f"图文版和框图：{BLOG_URL.format(slug=post.slug)}")
    credits = _clean(str(post.data.get("credits", "") or ""))
    if credits:
        parts.append(credits)
    hashtags = " ".join(f"#{t.replace(' ', '')}" for t in build_tags(post)[:3])
    if hashtags:
        parts.append(hashtags)
    desc = "\n\n".join(p for p in parts if p)
    if len(desc.encode("utf-8")) > DESCRIPTION_MAX_BYTES:
        raise ManifestError(f"{post.slug}: description exceeds {DESCRIPTION_MAX_BYTES} bytes")
    return desc


def build_job(post: Post, film: Path) -> UploadJob:
    if not film.is_file():
        raise ManifestError(f"{post.slug}: film not found at {film}")
    cover = post.path.parent / "cover.jpg"
    return UploadJob(
        slug=post.slug,
        film=film,
        cover=cover if cover.is_file() else None,
        title=build_title(post),
        description=build_description(post),
        tags=build_tags(post),
    )


def pending_jobs(posts: list[Post], films: dict[str, Path], only: set[str] | None = None) -> list[UploadJob]:
    """Jobs for posts that have a film and no `youtube` id yet; `only` narrows to some slugs."""
    jobs = []
    for post in posts:
        if only is not None and post.slug not in only:
            continue
        if post.data.get("youtube") or post.data.get("draft"):
            continue
        film = films.get(post.slug)
        if film is None:
            continue
        jobs.append(build_job(post, film))
    return jobs


def write_video_id(index_md: Path, video_id: str) -> None:
    """Insert `youtube: <id>` into the frontmatter, keeping every other line as written."""
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise ManifestError(f"not a YouTube video id: {video_id!r}")
    text = index_md.read_text(encoding="utf-8")
    m = FRONTMATTER.match(text)
    if not m:
        raise ManifestError(f"{index_md}: no frontmatter block")
    lines = m.group(1).split("\n")
    if any(line.startswith("youtube:") for line in lines):
        lines = [f"youtube: {video_id}" if line.startswith("youtube:") else line for line in lines]
    else:
        anchor = next((i for i, line in enumerate(lines) if line.startswith("duration:")), None)
        if anchor is None:
            anchor = next(i for i, line in enumerate(lines) if line.startswith("coverAlt:"))
        lines.insert(anchor + 1, f"youtube: {video_id}")
    index_md.write_text("---\n" + "\n".join(lines) + "\n---\n" + text[m.end() :], encoding="utf-8")
