#!/usr/bin/env python3
"""Fix Chinese/Latin spacing in post bodies (dry run unless --write).

  fix_spacing.py SLUG [SLUG ...] [--write]
  fix_spacing.py --all [--write]

Adds one space between Chinese characters and Latin letters or digits, removes the space
after Chinese closing punctuation before more Chinese (the `）](url) 和` case after a link),
and turns straight "..." quotes into Chinese “...” (smartypants renders them as ”...”).
Math, code, URLs, HTML comments and the frontmatter are left untouched; captions are fixed.
"""

from __future__ import annotations

import argparse
import difflib
import re

from blog_paths import FRONTMATTER, POSTS, check_root

CJK = r"㐀-䶿一-鿿"
CLOSE = "）」』》，。；：？！、"
PROTECT = re.compile(
    r"```.*?```"  # fenced code
    r"|\$\$.*?\$\$"  # display math
    r"|(?<!\\)\$[^$\n]+?(?<!\\)\$"  # inline math
    r"|`[^`\n]+`"  # inline code
    r"|<!--.*?-->"  # comments
    r"|\]\([^)\s]+"  # link and image targets
    r"|https?://\S+",  # bare URLs
    re.DOTALL,
)
RULES = (
    (re.compile(rf"([{CJK}])([A-Za-z0-9])"), r"\1 \2"),
    (re.compile(rf"([A-Za-z0-9])([{CJK}])"), r"\1 \2"),
    (re.compile(rf"([{CLOSE}]) +(?=[{CJK}])"), r"\1"),
)


def fix_text(s: str) -> str:
    for pattern, repl in RULES:
        s = pattern.sub(repl, s)
    return s


# Image titles ("caption") are Markdown syntax: never turn their quotes into curly ones.
PROTECT_QUOTES = re.compile(PROTECT.pattern + r'|"[^"\n]*"\)', re.DOTALL)
STRAIGHT_PAIR = re.compile(r'"([^"\n]{1,80}?)"')


def fix_quotes(body: str) -> str:
    """Turn straight "..." in Chinese prose into “...”; smartypants otherwise renders both as closing quotes."""
    out, last = [], 0
    for m in PROTECT_QUOTES.finditer(body):
        out.append(STRAIGHT_PAIR.sub(r"“\1”", body[last : m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(STRAIGHT_PAIR.sub(r"“\1”", body[last:]))
    return "".join(out)


def fix_body(body: str) -> str:
    out, last = [], 0
    for m in PROTECT.finditer(body):
        out.append(fix_text(body[last : m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(fix_text(body[last:]))
    joined = fix_quotes("".join(out))
    # A link target ends the protected span, so `）](url) 和` is fixed here, after re-joining.
    return re.sub(rf"([{CLOSE}])\]\(([^)\s]+)\) +(?=[{CJK}])", r"\1](\2)", joined)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    check_root()
    slugs = sorted(p.name for p in POSTS.iterdir() if (p / "index.md").is_file()) if a.all else a.slugs
    if not slugs:
        ap.error("give a slug or --all")
    changed = 0
    for slug in slugs:
        path = POSTS / slug / "index.md"
        text = path.read_text(encoding="utf-8")
        m = FRONTMATTER.match(text)
        if not m:
            raise SystemExit(f"{path}: no frontmatter")
        new = text[: m.end()] + fix_body(text[m.end() :])
        if new == text:
            continue
        changed += 1
        diff = difflib.unified_diff(text.splitlines(), new.splitlines(), f"{slug}/index.md", "fixed", lineterm="", n=0)
        print("\n".join(diff))
        if a.write:
            path.write_text(new, encoding="utf-8")
    print(f"\n{changed} post(s) {'fixed' if a.write else 'would change'}")


if __name__ == "__main__":
    main()
