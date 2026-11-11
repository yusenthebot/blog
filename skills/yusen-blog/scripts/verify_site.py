#!/usr/bin/env python3
"""Check a running copy of the blog: every page loads, formulas render, every asset resolves.

  verify_site.py                 the live site (https://yusenthebot.github.io/blog)
  verify_site.py --dev           the dev server (http://localhost:4321/blog)
  verify_site.py --base URL      any other copy, e.g. `npm run preview`

Pages come from the repository's posts, not from the home page, so a post that failed to
build shows up as a 404 here. Exit 1 on any non-200 page or asset, any KaTeX error, or a post
with a youtube id whose page has no player.
Fresh deploys can take a minute to reach the CDN; rerun before calling a 404 real.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from blog_paths import DEV_BASE, LIVE_BASE, POSTS, check_root

PAGES = ("/", "/about/", "/rss.xml", "/sitemap-index.xml")
ASSET = re.compile(r'(?:src|href)="([^"]+)"|srcset="([^"]+)"')
TIMEOUT = 20


def get(url: str) -> tuple[int | str, str]:
    """GET with up to two retries on network errors (TLS resets happen on the Pages CDN)."""
    for attempt in range(3):
        status, body = _get_once(url)
        if not (isinstance(status, str) and status.startswith("ERR")):
            break
        time.sleep(1 + attempt)
    return status, body


def _get_once(url: str) -> tuple[int | str, str]:
    try:
        with urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": "yusen-blog-verify"}), timeout=TIMEOUT
        ) as r:
            body = r.read()
            ctype = r.headers.get("content-type", "")
            return r.status, body.decode("utf-8", "replace") if "html" in ctype or "xml" in ctype else ""
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        return f"ERR {getattr(e, 'reason', e)}", ""


def assets_of(page_url: str, html: str, origin: str, base_path: str) -> set[str]:
    found = set()
    for src, srcset in ASSET.findall(html):
        for ref in [src] if src else [part.strip().split(" ")[0] for part in srcset.split(",")]:
            if not ref or ref.startswith(("#", "mailto:", "data:")):
                continue
            url = urllib.parse.urljoin(page_url, ref)
            # Only this site's own files (pages are checked separately); external links are check_links.py's job.
            if url.startswith(origin + base_path) and not url.endswith("/"):
                found.add(url)
    return found


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dev", action="store_true")
    ap.add_argument("--base")
    a = ap.parse_args()
    check_root()
    base = (a.base or (DEV_BASE if a.dev else LIVE_BASE)).rstrip("/")
    parts = urllib.parse.urlsplit(base)
    origin, base_path = f"{parts.scheme}://{parts.netloc}", parts.path

    drafts = {
        p.parent.name for p in POSTS.glob("*/index.md") if re.search(r"^draft:\s*true", p.read_text(), re.MULTILINE)
    }
    slugs = sorted(p.parent.name for p in POSTS.glob("*/index.md") if p.parent.name not in drafts)
    # The sitemap only exists in a build; `astro dev` does not serve it.
    fixed = [p for p in PAGES if not (a.dev and p.startswith("/sitemap"))]
    pages = [base + p for p in fixed] + [f"{base}/posts/{s}/" for s in slugs]

    # A post with a youtube id must show its player (not the "coming soon" placeholder).
    videos = {}
    for s in slugs:
        m = re.search(r"^youtube:\s*([A-Za-z0-9_-]{11})\s*$", (POSTS / s / "index.md").read_text(), re.MULTILINE)
        if m:
            videos[f"{base}/posts/{s}/"] = m.group(1)

    failures, assets, katex_errors = 0, set(), 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        for url, (status, html) in zip(pages, pool.map(get, pages)):
            errs = html.count("katex-error")
            katex_errors += errs
            assets |= assets_of(url, html, origin, base_path)
            video = videos.get(url)
            no_player = bool(video) and f"embed/{video}" not in html
            bad = status != 200 or errs or no_player
            failures += bool(bad)
            print(
                f"  {'ok  ' if not bad else 'FAIL'} {status} {url.removeprefix(base)}"
                + (f"  katex-error x{errs}" if errs else "")
                + (f"  no player for youtube id {video}" if no_player else "")
            )
        asset_results = list(pool.map(get, sorted(assets)))
    broken = [(u, s) for u, (s, _) in zip(sorted(assets), asset_results) if s != 200]
    for u, s in broken:
        print(f"  FAIL {s} asset {u.removeprefix(origin)}")
    failures += len(broken)
    print(
        f"\n{len(pages)} pages, {len(assets)} assets, {katex_errors} KaTeX errors, {failures} failure(s)"
        + (f"; drafts skipped: {', '.join(sorted(drafts))}" if drafts else ""),
        file=sys.stderr,
    )
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
