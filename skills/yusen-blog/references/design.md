# The look

A light terminal look (CLI / retro-computing type on white paper): the type system of https://yusenthebot.github.io/ (VT323 for display, JetBrains Mono for text) without its dark CRT effects.
The author chose (2026-11-09): white background, no credits, Chinese display text in a pixel font that matches the English, a cleaner layout.

## Tokens (`src/styles/global.css`)

| Token | Value | Use |
| --- | --- | --- |
| `--bg` | `#ffffff` | page |
| `--paper`, `--surface` | `#fafaf8`, `#f4f4f1` | code blocks, the video frame, quiet panels |
| `--line`, `--line-strong` | `#e8e8e3`, `#d6d6cf` | hairlines and card borders |
| `--text`, `--body`, `--muted`, `--dim` | `#1c1c1c`, `#2b2b2b`, `#5d6066`, `#8b8e94` | headings, body, meta, faint |
| `--accent` | `#d9622b` | the series orange: episode numbers, link underlines, the active filter; nothing else |
| `--ok` | `#1a8f4c` | the prompt's green and the cursor bar |

One accent only; no gradients, glows, scanlines or shadows.

## Type

- `--font-pixel` = VT323 + "Pixel CJK": the brand, nav, prompts, numbers.
- `--font-pixel-zh` = "Pixel ZH": Chinese headlines (post titles, card titles, `h2`/`h3`, filters, pager). Its own pixel Latin keeps mixed lines like `VLA上` in one family.
- `--font-body` = JetBrains Mono + PingFang SC: running text. Long Chinese text with formulas stays in a smooth font for readability; the author was offered pixel body text and has not asked for it.
- Fusion Pixel 12px (OFL) is drawn on a 12 px grid: set it only at multiples of 12 px (24, 36) with `-webkit-font-smoothing: none`, or the pixels blur.
- The font file is subset at build time to the characters in `src/**` (`scripts/subset-fonts.mjs`); both `@font-face` rules point at the same `src/assets/fonts/pixel-12.woff2`, imported with `?url` in `Base.astro` for the preload.

## Layout

The live layout is the one on `origin/main`; this section was checked against it on 2026-11-11.

- Home: hero (prompt line, `YUSEN_BLOG`, pixel tagline, English lede, POSTS / VIDEOS / UPDATED stats), filter buttons (all, 科普视频, 图文; synced to `?s=`), then a card grid of 3 columns (2 below 960 px, 1 below 640 px). The first visible card is a full-width feature card.
- Post: title, lede, meta and tags; the video block (click-to-load youtube-nocookie player, or the "即将上传到 YouTube" placeholder when the post has no id); the article; a numbered REFERENCES list; prev/next pager.
- The article column (46 rem) is centred on the page at every width. The contents list no longer takes a grid column:
  - From 1200 px up it is a rail docked to the right edge of the page (`.toc-rail`, absolutely positioned, `clamp(10rem, 14vw, 13rem)` wide) with the list sticky inside it and scrolling on its own when taller than the window.
  - Below 1200 px it is a collapsed `<details>` box above the article ("文章目录 N 节") that the reader opens; a script opens it on wide screens and closes it on narrow ones.
- `fig-*` images grow equally on both sides, by at most 5 rem and only as far as leaves 24 px clear of the rail (`--grow`); stills stay at text width. Display math scrolls sideways when it overflows.
- Header: `YUSEN_BLOG` with a blinking cursor, nav posts / about / YouTube / ~/home. Below 520 px the brand shrinks and the nav wraps to the right. Footer: rss / github / home.

## Motion

Motion is small, functional and off under `prefers-reduced-motion`.

- Reading cursor: the contents list marks the section being read (`aria-current="location"`, found on scroll through one `requestAnimationFrame` per frame) and a 6 px orange square slides along the list's left rule to it in 170 ms. The list scrolls itself to keep the current entry in view.
- Arriving at a heading from the contents list turns its `##` marker orange, fading back over 720 ms.
- Home to post: a cross-document view transition (`@view-transition { navigation: auto }`) moves only the `EPnn` badge from the clicked card to the article header in 200 ms; the rest of the page swaps with no fade. The inline script in `Base.astro` names the badge on `pageswap` / `pagereveal` and skips the transition for any other navigation.
- Keep to this vocabulary: one moving element per interaction, 170 to 200 ms with `cubic-bezier(0.22, 0.7, 0.3, 1)`, the accent colour only. No page fades, parallax or scroll-triggered reveals.

## Typesetting rules

- Chinese headlines (post and card titles, `h2`/`h3`, pager) use `word-break: keep-all` plus `text-wrap: balance`, and break only at the `<wbr>` that `src/lib/cjk-words.mjs` inserts between Chinese words (Intl.Segmenter, single characters merged into their neighbours, punctuation attached to the word before it). Titles render through `wbrHtml()`; Markdown headings get the same through the `rehypeCjkHeadings` plugin. Result: no line ends inside a word like 训练 and no lone character on a last line.
- Running text uses `text-wrap: pretty`.
- Tables sit in a `.table-wrap` scroll box at full column width; cells of 24 characters or fewer get class `nw` and never wrap, so values like `94.5 / 71.1 / 81.6%` stay on one line.
- Straight quotes in Chinese prose render as ”…” through smartypants; posts use “…” (`fix_spacing.py` converts them).
- Phones: the three filter buttons fit one row (tighter padding below 640 px).

## Where things are

| File | Holds |
| --- | --- |
| `src/styles/global.css` | all styles and tokens |
| `src/layouts/Base.astro` | head, fonts, header, footer, the view-transition script |
| `src/pages/index.astro` | home and the filter script |
| `src/pages/posts/[slug].astro` | the post page, contents rail and its reading-cursor script, references |
| `src/components/PostCard.astro`, `Video.astro` | card and video block |
| `src/lib/rehype-figure.mjs` | image-only paragraphs with a title become `<figure>` with `<figcaption>`; `fig-` files get the wide class; tables get the scroll wrapper and `nw` cells |
| `src/lib/cjk-words.mjs` | word-level `<wbr>` for Chinese headlines (`wbrHtml`, `rehypeCjkHeadings`) |
| `src/lib/rehype-cjk-linebreak.mjs` | removes the space a source line break leaves between Chinese sentences |
| `src/lib/site.ts` | site name, title, description, series labels |

## Changing the design

Keep the terminal vocabulary (prompts, monospace, hairline boxes) and the one accent.
After any change: run `scripts/layout_check.js` in the browser pane (every page at 375, 1000, 1199, 1200, 1440 and 1920 px: nothing under the contents rail, no horizontal scroll, no orphaned headline characters), look at the home page, one kepu post and one notes post, and confirm the pixel fonts loaded (`document.fonts` has "Pixel CJK" and "Pixel ZH" with status loaded).
The user is picky about pixel-level detail: misaligned baselines, uneven gaps and blurry pixel type count as bugs.
