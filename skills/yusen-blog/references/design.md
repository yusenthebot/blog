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

- Home: hero (prompt line, `YUSEN_BLOG`, pixel tagline, English lede, POSTS / VIDEOS / UPDATED stats), filter buttons (all, 科普视频, 图文; synced to `?s=`), then a card grid of 3 columns (2 below 960 px, 1 below 640 px). The first visible card is a full-width feature card.
- Post: title, lede, meta and tags; the video block (click-to-load youtube-nocookie, or the "即将上传到 YouTube" placeholder); the article in a 46 rem column with a sticky 13 rem contents list on the right above 1120 px; `fig-*` images grow into the free left margin (up to 10 rem, never to the right, where the sticky contents list sits); the contents list scrolls on its own when taller than the window; display math scrolls sideways when it overflows; a numbered REFERENCES list; prev/next pager.
- Header: `YUSEN_BLOG` with a blinking cursor, nav posts / about / ~/home. Footer: rss / github / home.

## Where things are

| File | Holds |
| --- | --- |
| `src/styles/global.css` | all styles and tokens |
| `src/layouts/Base.astro` | head, fonts, header, footer |
| `src/pages/index.astro` | home and the filter script |
| `src/pages/posts/[slug].astro` | the post page, contents list, references |
| `src/components/PostCard.astro`, `Video.astro` | card and video block |
| `src/lib/rehype-figure.mjs` | image-only paragraphs with a title become `<figure>` with `<figcaption>`; `fig-` files get the wide class |
| `src/lib/rehype-cjk-linebreak.mjs` | removes the space a source line break leaves between Chinese sentences |
| `src/lib/site.ts` | site name, title, description, series labels |

## Changing the design

Keep the terminal vocabulary (prompts, monospace, hairline boxes) and the one accent.
After any change: check the home page, one kepu post and one notes post at desktop width and at 375 px (no horizontal scroll), and confirm the pixel fonts loaded (`document.fonts` has "Pixel CJK" and "Pixel ZH" with status loaded).
The user is picky about pixel-level detail: misaligned baselines, uneven gaps and blurry pixel type count as bugs.
