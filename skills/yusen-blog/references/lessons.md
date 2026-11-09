# Lessons

Each of these cost a round on the first build (2026-11-09).

## Site and tooling

- The site lives under `/blog` (a GitHub Pages project site). `http://localhost:4321/` is a 404 in dev; open `/blog/`. Redirecting `/` to `/blog/` in dev loops, because Astro mounts the dev app under the base: do not try again.
- Astro 7 needs Node 22.23.4 or newer and the machine has 22.22.3, so the repo pins Astro 6.4.8. Upgrade Node first if Astro ever moves.
- Markdown plugins go in `markdown.processor: unified({...})`; the old `markdown.rehypePlugins` option is deprecated.
- The dev server does not always pick up a new post folder: restart it. After deleting images a post referenced, a 500 `ImageNotFound` comes from stale caches: `rm -rf .astro node_modules/.vite` and restart.
- The pixel font must be in `src/assets/fonts/` (imported, hashed); from `public/` Vite warns it "didn't resolve at build time".
- `astro dev` does not serve the sitemap; `verify_site.py --dev` skips it.

## Writing

- One sentence per line in the source left a visible gap after "。" until `rehype-cjk-linebreak` was added; keep that plugin.
- Spaces next to Chinese punctuation and missing spaces between Chinese and Latin text crept in through captions and through links written as `[名称（作者, 年）](url) 和`; `check_post.py` flags both and `fix_spacing.py` fixes them.
- The first rewrite in the social-post voice was rejected: the blog wants standard written Chinese with formulas and paper links, not spoken style.
- Agents rewriting posts in parallel must not run `npm run build`, `npm install`, `astro sync` or git; the owner of the repo builds and commits once.

## Facts and licences

- MacMimic's README forbids publishing its rollout footage (derived from LAFAN1, CC BY-NC-ND): no frames in the post or figure, no video, no film-map entry.
- EP1's Earth texture is CC BY 4.0. With credits removed from the site, its attribution only survives if the YouTube description keeps a source line; ask the user before uploading EP1.
- Some hosts answer scripts with 403/402 (doi.org, aerospaceamerica.aiaa.org, ntrs.nasa.gov, X): they are not dead links, verify them by hand.
- Numbers that came only from an episode's narration or STORYLINES (EP1's Apollo 8 figures, for example) are reported as unverified until checked against a primary source.

## Figures

- figkit math breaks on `\mathbf`, `\nu` and `\partialx` (write `\partial x`); use plain symbols and `\delta`.
- The gate fails on word budget, overlaps and half-in-panel elements: cut labels and move explanations to the caption before resizing anything.

## Layout

- Wide figures once had `margin: 0 -7rem`: the right side ran 56 px under the sticky contents list and the left side overflowed near 1121 px. They now grow left only, by the margin that is actually free. After any layout change, measure every post at 375, 1000, 1140, 1280, 1440 and 1920 px for elements crossing the contents list and for horizontal scroll, not just one screenshot.
- `text-wrap: balance` alone split a title inside a word (训 / 练), and `keep-all` alone left a lone character (级) after a long run without spaces; word-level `<wbr>` from Intl.Segmenter fixed both. After a headline change, scan every headline at 375, 1000 and 1440 px for a last line under 18 % of the box.
- Headless Chrome cannot go below a 500 px viewport (`--window-size=390,...` still lays out at 500): check phones in the browser pane with the mobile preset, not with headless screenshots.
- A cover cut mid-transition (EP13's first cover) shows half-drawn text; always look at the cover at full size.
- Changing Markdown, rehype plugins or captions while `astro dev` runs often serves stale HTML: stop the server, `rm -rf .astro node_modules/.vite`, start it again, then check with curl before screenshots.
