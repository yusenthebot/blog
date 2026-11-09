"""Shared paths for the yusen-blog scripts.

The skill lives inside the blog repository (skills/yusen-blog/), and Claude Code reaches it through
a symlink, so the repository root is found from this file's resolved location.
BLOG_ROOT overrides it when the scripts are copied elsewhere.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("BLOG_ROOT", Path(__file__).resolve().parents[3])).expanduser()
POSTS = ROOT / "src" / "content" / "posts"
FIGURES = ROOT / "figures"
FILM_MAP = ROOT / "tools" / "youtube" / "films.local.json"
WORK = ROOT / ".work"
LIVE_BASE = "https://yusenthebot.github.io/blog"
DEV_BASE = "http://localhost:4321/blog"
EPISODES = Path.home() / "Desktop" / "03_视频与录屏" / "02_主题视频" / "科普视频 2"

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def check_root() -> None:
    if not (ROOT / "astro.config.mjs").is_file():
        raise SystemExit(f"blog repository not found at {ROOT}; set BLOG_ROOT")


def split_post(text: str) -> tuple[str, str]:
    """Return (frontmatter, body) of a post's index.md."""
    m = FRONTMATTER.match(text)
    if not m:
        raise ValueError("index.md has no frontmatter block")
    return m.group(1), text[m.end() :]
