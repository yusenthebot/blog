# Images and the block diagram

A post folder `src/content/posts/<slug>/` holds `index.md`, `cover.jpg`, its figure PNGs (`fig-*.png`) and its film stills (`still-*.jpg`).
Images live beside the post (Astro optimises them into WebP at build time); never link remote images.

## Cover and stills (kepu posts, and notes posts with a film)

1. `new_post.py` writes contact sheets to `.work/<slug>/sheet-NN.jpg`, one tile every 4 s, 30 tiles per sheet (tile k of sheet n is at `(n-1)*120 + k*4` s, counting tiles from 0 row by row). Read them and choose times.
2. Cover: a clean, bright, recognisable frame that names the topic at a glance (a robot doing the task, not a slide of text).
   `frames.py cover FILM TIME .../cover.jpg` crops `1600:900:200:0` from the 1920 x 1080 film, which keeps the burned-in subtitle band out and trims 200 px from each side.
3. Stills: 2 to 4 frames that carry the explanation (a mechanism shot, the experiment, the result).
   `frames.py still FILM TIME .../still-<what>.jpg` crops `1920:930:0:0` and scales to 1600 wide.
4. Open every frame you keep. Move the time if anything is cut off at the side, a subtitle shows, or the frame is mid-transition.

A notes post without a film uses its figure on a white canvas as the cover (MacMimic does this).

## The block diagram

Every post gets one main figure drawn with the `block-diagram-drawer` skill: load it and read its `references/paper-figure-study.md` and `references/visual-contract.md` before the first figure of a session.
`figures/src/fig_ep01_ekf.py` is a complete figure that passes the gate; copy its idioms.

- Build script `figures/src/fig_<slug_with_underscores>.py`, image crops in `figures/src/assets/<slug>/`, output `figures/<slug>-figure.{svg,png}`; copy the PNG into the post as `fig-<name>.png`.
- `figures/src/figkit.py` and `qa_svg_figure.py` are vendored copies: never edit them.
- Canvas 1400 by 480 to 560, three or four panels `(a)` to `(d)`, text-width print target.
- Content: the episode's core mechanism plus our experiment and its real numbers when there is one. Numbers come from the planning files, never invented.
- Real imagery: crops of film frames in the panels via `f.image()` (crop subtitles and on-screen notes out).
- Labels are English technical names with symbols; one short Chinese word is fine where the film uses it. Explanations go in the caption.
- figkit math supports `\hat \bar \tilde \mathrm \mathbb \mathcal`, sub- and superscripts and the symbols in its table (`\partial \top \delta \lambda \mu ...`). It does not support `\mathbf`, `\nu`, `\left`, `\frac`; check a symbol renders before relying on it.
- Gate: `cd figures/src && python3 fig_<x>.py && python3 qa_svg_figure.py ../<slug>-figure.svg --png --strict-tidy` until it prints PASS, then open the PNG: no cut-off text in crops, no empty half-cards, arrows the right way. At least three gate-and-look cycles.
- Never put licence-restricted footage in a figure (MacMimic's rollout frames derive from LAFAN1, CC BY-NC-ND).

## In the Markdown

```markdown
![框图：一句话说图里有什么](./fig-rl.png "图注：先说这张图展示什么，再逐个面板解释，最后说明哪些部分是示意。")
```

- The alt text describes the image; the title slot is the caption, rendered as `<figcaption>`.
- A file named `fig-*` grows into the free left margin on wide screens (never to the right, where the contents list is); stills stay at text width.
- Put the block diagram where the method section starts; put each still next to the paragraph it illustrates.
- Captions follow the same language rules as the article (`writing.md`), including a space between Chinese and Latin text.
