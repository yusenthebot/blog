#!/usr/bin/env python3
"""Lint blog posts against the house rules, without building the site.

  check_post.py SLUG [SLUG ...]    check these posts
  check_post.py --all              check every post

Errors (exit 1): missing frontmatter fields, a credits field, missing or uncaptioned images,
em dashes, a space before Chinese punctuation, TODO markers left in.
Warnings: length outside 2500 to 5000 Chinese characters, fewer than 3 display equations,
no inline paper links, spoken or rhetorical phrasing, Chinese and Latin text without a space.
Formulas still need a render check (verify_site.py), and links a fetch check (check_links.py).
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from blog_paths import POSTS, SLUG, check_root, split_post

REQUIRED = ("title", "description", "date", "series", "tags", "cover", "coverAlt", "platforms", "links")
REQUIRED_KEPU = ("episode", "duration")
LENGTH = (2500, 5000)
MIN_DISPLAY_EQ = 3

CJK = r"㐀-䶿一-鿿"
CJK_PUNCT = "，。、；：？！）」』》"
# Phrases the author ruled out for the blog (2026-11-09): spoken fillers and rhetorical setups.
SPOKEN = {
    "这期视频": "write about the method, not the video",
    "说白了": "spoken filler",
    "说穿了": "spoken filler",
    "挺有意思": "spoken judgement",
    "硬堆": "slang",
    "你以为": "rhetorical setup",
    "答案恰恰相反": "rhetorical setup",
}
NOT_BUT = re.compile(r"不是[^。！？\n]{1,24}而是")


@dataclass
class Report:
    slug: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict[str, int] = field(default_factory=dict)


def strip_non_prose(body: str) -> str:
    """Remove what is not running prose: comments, code, math, tables, images, link targets, HTML."""
    s = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
    s = re.sub(r"```.*?```", "", s, flags=re.DOTALL)
    s = re.sub(r"\$\$.*?\$\$", "", s, flags=re.DOTALL)
    # Inline math and code become one Latin letter, so the spacing rules still see their edges.
    s = re.sub(r"(?<!\\)\$[^$\n]+?(?<!\\)\$", "x", s)
    s = re.sub(r"`[^`\n]+`", "c", s)
    s = re.sub(r"^\|.*\|\s*$", "", s, flags=re.MULTILINE)
    s = re.sub(r'!\[[^\]]*\]\([^)\s]+(?:\s+"[^"]*")?\)', "", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"<[^>]+>", "", s)
    return s


def frontmatter_keys(fm: str) -> set[str]:
    return set(re.findall(r"^([A-Za-z]+):", fm, flags=re.MULTILINE))


def check_frontmatter(fm: str, folder: Path, r: Report) -> None:
    keys = frontmatter_keys(fm)
    series = re.search(r"^series:\s*(\w+)", fm, flags=re.MULTILINE)
    need = REQUIRED + (REQUIRED_KEPU if series and series.group(1) == "kepu" else ())
    for k in need:
        if k not in keys:
            r.errors.append(f"frontmatter: missing `{k}`")
    if "credits" in keys:
        r.errors.append("frontmatter: `credits` was removed from the site; drop it")
    cover = re.search(r"^cover:\s*(\S+)", fm, flags=re.MULTILINE)
    if cover and not (folder / cover.group(1)).is_file():
        r.errors.append(f"cover not found: {cover.group(1)}")
    yt = re.search(r"^youtube:\s*(\S+)", fm, flags=re.MULTILINE)
    if yt and not re.fullmatch(r"[A-Za-z0-9_-]{11}", yt.group(1).strip("\"'")):
        r.errors.append("youtube must be the 11-character video id, not a URL")
    refs = len(re.findall(r"^\s*-\s*label:", fm, flags=re.MULTILINE))
    r.stats["refs"] = refs
    if refs == 0:
        r.warnings.append("no references in `links`")
    if "TODO" in fm:
        r.errors.append("frontmatter still has TODO")


def check_images(body: str, folder: Path, r: Report) -> None:
    for alt, src, title in re.findall(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)', body):
        if src.startswith("http"):
            r.warnings.append(f"remote image {src}; keep images in the post folder")
            continue
        if not (folder / src).is_file():
            r.errors.append(f"image not found: {src}")
        if not alt.strip():
            r.errors.append(f"image without alt text: {src}")
        if not title:
            r.errors.append(f"image without a caption (the title slot): {src}")


def check_prose(body: str, r: Report) -> None:
    captions = "\n".join(re.findall(r'!\[[^\]]*\]\([^)\s]+\s+"([^"]*)"\)', body))
    prose = strip_non_prose(body) + "\n" + strip_non_prose(captions)
    for i, line in enumerate(prose.splitlines(), 1):
        if "—" in line:
            r.errors.append(f"em dash: {line.strip()[:40]}")
        if re.search(rf" [{CJK_PUNCT}]|（ |[{CJK_PUNCT}] [{CJK}]", line):
            r.errors.append(f"space next to Chinese punctuation: {line.strip()[:40]}")
    for phrase, why in SPOKEN.items():
        if phrase in prose:
            r.warnings.append(f"「{phrase}」: {why}")
    for m in NOT_BUT.finditer(prose):
        r.warnings.append(f"「{m.group(0)}」: 不是…而是 setup, state it directly")
    unspaced = re.findall(rf"[{CJK}][A-Za-z0-9]|[A-Za-z0-9][{CJK}]", prose)
    if unspaced:
        r.warnings.append(f"{len(unspaced)} places with Chinese next to Latin/digits and no space")
    if re.search(r"TODO", body.replace("<!--", "").replace("-->", "")):
        r.errors.append("article still has TODO")

    chars = len(re.findall(rf"[{CJK}]", strip_non_prose(body)))  # captions do not count
    display = len(re.findall(r"\$\$.*?\$\$", body, flags=re.DOTALL))
    links = len(re.findall(r"(?<!!)\[[^\]]+\]\(https?://", re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)))
    headings = len(re.findall(r"^##\s", body, flags=re.MULTILINE))
    r.stats.update(chars=chars, display_eq=display, inline_links=links, sections=headings)
    if not LENGTH[0] <= chars <= LENGTH[1]:
        r.warnings.append(f"{chars} Chinese characters, target {LENGTH[0]} to {LENGTH[1]}")
    if display < MIN_DISPLAY_EQ:
        r.warnings.append(f"{display} display equations, aim for {MIN_DISPLAY_EQ}+")
    if links == 0:
        r.warnings.append("no inline links; cite papers where they are named")
    if headings < 3:
        r.warnings.append(f"{headings} `##` sections; the page builds its contents list from them")


def check(slug: str) -> Report:
    r = Report(slug)
    folder = POSTS / slug
    if not SLUG.match(slug):
        r.errors.append("slug must be lowercase words joined by hyphens")
    index = folder / "index.md"
    if not index.is_file():
        r.errors.append(f"{index} not found")
        return r
    try:
        fm, body = split_post(index.read_text(encoding="utf-8"))
    except ValueError as e:
        r.errors.append(str(e))
        return r
    check_frontmatter(fm, folder, r)
    check_images(re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL), folder, r)
    check_prose(body, r)
    return r


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("-q", "--quiet", action="store_true", help="only print posts with errors or warnings")
    a = ap.parse_args()
    check_root()
    slugs = sorted(p.name for p in POSTS.iterdir() if (p / "index.md").is_file()) if a.all else a.slugs
    if not slugs:
        ap.error("give a slug or --all")

    failed = 0
    for slug in slugs:
        r = check(slug)
        failed += bool(r.errors)
        if a.quiet and not (r.errors or r.warnings):
            continue
        stats = "  ".join(f"{k}={v}" for k, v in r.stats.items())
        print(f"{'FAIL' if r.errors else 'ok  '} {slug}  {stats}")
        for e in r.errors:
            print(f"     error: {e}")
        for w in r.warnings:
            print(f"     warn:  {w}")
    print(f"\n{len(slugs) - failed}/{len(slugs)} posts pass", file=sys.stderr)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
