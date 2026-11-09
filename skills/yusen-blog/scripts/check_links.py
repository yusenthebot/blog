#!/usr/bin/env python3
"""Fetch every URL a post cites and print its HTTP status and page title.

  check_links.py SLUG [SLUG ...]
  check_links.py --all

Compare each printed title with the paper the text cites; a 200 on the wrong paper is still wrong.
Hosts that block scripts (doi.org, X, some publishers) come back 403/402/429 and are marked
CHECK BY HAND: open them in a browser or confirm the paper through its arXiv or publisher page.
Exit 1 when a link is dead (404, 410, 5xx, DNS or TLS failure).
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from blog_paths import POSTS, check_root, split_post

# A plain client name; never put the user's contact details in request headers.
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
BLOCKED_STATUS = {401, 402, 403, 405, 429, 999}
TIMEOUT = 20
URL = re.compile(r"https?://[^\s)\"'<>\]]+")


def urls_of(slug: str) -> list[str]:
    fm, body = split_post((POSTS / slug / "index.md").read_text(encoding="utf-8"))
    found = URL.findall(fm) + URL.findall(body)
    return list(dict.fromkeys(u.rstrip(".,;") for u in found))


def fetch(url: str) -> tuple[str, int | str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            head = r.read(200_000).decode("utf-8", "replace")
            m = re.search(r"<title[^>]*>(.*?)</title>", head, re.DOTALL | re.IGNORECASE)
            title = html.unescape(re.sub(r"\s+", " ", m.group(1))).strip() if m else ""
            return url, r.status, title
    except urllib.error.HTTPError as e:
        return url, e.code, ""
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        return url, f"ERR {getattr(e, 'reason', e)}", ""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    check_root()
    slugs = sorted(p.name for p in POSTS.iterdir() if (p / "index.md").is_file()) if a.all else a.slugs
    if not slugs:
        ap.error("give a slug or --all")

    dead = 0
    for slug in slugs:
        urls = urls_of(slug)
        print(f"\n{slug}: {len(urls)} links")
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(fetch, urls))
        for url, status, title in results:
            if status == 200:
                tag = "ok  "
            elif status in BLOCKED_STATUS:
                tag = "HAND"
            else:
                tag = "DEAD"
                dead += 1
            print(
                f"  {tag} {status!s:>4} {url}\n            {title[:110]}" if title else f"  {tag} {status!s:>4} {url}"
            )
    print(f"\n{dead} dead link(s); HAND = blocked for scripts, check by hand", file=sys.stderr)
    sys.exit(1 if dead else 0)


if __name__ == "__main__":
    main()
