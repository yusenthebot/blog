# Post playbook

How one post is made.
`src/content/posts/ep01-ekf/` is the reference: read its `index.md` and look at `figures/ep01-ekf-figure.png` before starting.

## Layout

Each post is one folder `src/content/posts/<slug>/` holding `index.md`, `cover.jpg`, its figure PNGs (`fig-*.png`) and its film stills (`still-*.jpg`).
Figure build scripts live in `figures/src/fig_<slug-with-underscores>.py`, their image crops in `figures/src/assets/<slug>/`, and the built SVG and PNG in `figures/<slug>-<name>-figure.{svg,png}`; copy the PNG into the post folder as `fig-<name>.png`.
`figures/src/figkit.py` and `figures/src/qa_svg_figure.py` are shared and vendored: never edit them.

## Frontmatter

The schema is in `src/content.config.ts`.

```yaml
---
title: 短标题：一句话说清这期讲什么        # from the episode's 发布文案.md title, may be tightened
description: 一到两句，读者为什么要看       # rewritten from the 发布文案 简介 in the author's voice
date: 2026-10-27                          # day the final film was rendered (mtime of 成片/*_横屏.mp4)
series: kepu                              # kepu = video episode, notes = 图文 post
episode: 1                                # kepu only
tags: [卡尔曼滤波, EKF]                    # 3 to 6, from the 话题标签 without "#"
cover: ./cover.jpg
coverAlt: 画面描述
duration: "1:33"                          # kepu only, from ffprobe of the 横屏 film
platforms: [douyin, tiktok]               # kepu; notes posts use [xiaohongshu]
links:                                    # references, see the Article section
  - label: "Authors (Year). Title."
    url: https://...
    note: venue
---
```

A notes post that comes with a film sets `video: true` and `duration`, and gets a cover from the film like a kepu post.
Leave `youtube` out: videos are not uploaded yet, and the page shows a placeholder.

## Images

- Cover (kepu): a clean, bright, recognizable 16:9 frame from the 横屏 film, `crop=1600:900:200:0` (that keeps the burned-in subtitle band out), saved as `cover.jpg` at `-q:v 3`.
  Check the crop by looking at it; move the time or the crop if any subtitle pixels show.
- Stills (kepu): 2 to 4 frames that carry the explanation (a mechanism shot, the experiment, the result), `crop=1920:930:0:0,scale=1600:-2`, `-q:v 3`, named `still-<what>.jpg`.
  Make a contact sheet first (`fps=1/4,scale=480:-1,tile=6x5`) and read it, then pick exact times.
- Never put a still with a half-cut subtitle in a post; look at every frame you keep.

## Figure (block-diagram-drawer)

Every post gets one main block diagram, drawn with the `block-diagram-drawer` skill (load the skill and read its `references/paper-figure-study.md` and `references/visual-contract.md` before the first figure).
`figures/src/fig_ep01_ekf.py` is a complete figure that passes the gate: copy its idioms.

- Canvas 1400 by 480 to 560, three or four panels, text-width print target.
- Content is the episode's core mechanism plus the author's own experiment and its real numbers when the episode has one; the numbers must come from the planning files (`策划/`, `实验/结果.md`, README, STORYLINES), never invented.
- Use real imagery: crops of film frames go in the panels via `f.image()` (crop the caption band and on-screen notes out where possible).
- Labels are English technical names with symbols; one short Chinese word is fine where the film uses it (as EP1 does with 猜 看 改). Explanations go in the caption, not on the canvas.
- `figkit` math supports `\hat \bar \tilde \mathrm \mathbb \mathcal`, sub/superscripts and the symbols listed in its table (`\partial \top \delta \lambda \mu ...`). It does NOT support `\mathbf`, `\nu`, `\left`, `\frac`; check a symbol renders before relying on it.
- Run `python3 qa_svg_figure.py ../<name>-figure.svg --png --strict-tidy` from `figures/src` until it prints PASS, then open the PNG and inspect it: no cut-off text in crops, no empty half-cards, arrows in the right direction. Do at least three gate-and-look cycles.
- The figure caption (the Markdown image title) explains every panel in Chinese, starting with what the figure shows; say which parts are schematic.

## Article (technical rewrite, 2026-11-09)

The author asked for articles that are more technical: methods, formulas, paper sources with hyperlinks, and normal, correct Chinese grammar. The loose spoken "shuorenhua" voice does NOT apply to the blog any more.

Language and tone:

- Standard written Chinese (规范书面语) with complete, grammatical sentences, the register of a good technical blog or a survey's introduction. No spoken fragments, no dropped subjects, no slang ("硬堆", "搬到", "挺有意思"), no rhetorical setups ("不是……而是……", "说白了", "你以为……其实……"), no em dashes.
- Put one space between Chinese and Latin letters or numbers (`在 MuJoCo 中训练 3 个种子`), none before Chinese punctuation.
- English technical terms stay in English; the first use of an acronym gets its full name once: `扩展卡尔曼滤波（Extended Kalman Filter，EKF）`.
- Be precise: say what is simulated, how many seeds, what the metric measures, what is schematic.

Structure (use `##` for sections and `###` where a section has parts; the page builds a table of contents from them):

1. A short opening paragraph: the problem, why it is hard, and what the article covers. No "这期视频".
2. Problem setup and notation: state, action, observation, objective, written as math.
3. The method, the core of the article and at least half of it: the key equations in LaTeX, a derivation or intuition for each, and the algorithm as an ordered list of steps (or a short pseudo-code block). Explain what each symbol means right after the equation.
4. Representative work: the line of papers the episode covers, each introduced with what it changed, cited inline as a hyperlink, e.g. `[Schulman et al., 2017](https://arxiv.org/abs/1707.06347)`.
5. Our experiment (when the episode has one): setup (simulator, robot model, policy size, training budget, seeds, hardware), a Markdown results table, an interpretation, and the limitations.
6. A short conclusion: what to remember and open problems.

Length: 2500 to 5000 Chinese characters, not counting formulas and tables.

Math: inline `$...$`, display `$$...$$` on its own lines (KaTeX renders it; use standard LaTeX such as `\mathbf{x}`, `\hat{x}`, `\mathbb{E}`, `\nabla_\theta`, `\operatorname{clip}`, aligned blocks with `\begin{aligned}`). Formulas must be the standard ones from the cited paper or textbook; if the article uses the video's simplified form, say so. Check every formula renders on the page (no red KaTeX error text).

Citations and links:

- Every paper, model or dataset named in the text is a hyperlink to its arXiv abs page, the official paper page or the official project page.
- Verify every URL with WebFetch before using it: the page must exist and its title must match the paper you cite. Never guess an arXiv id. The planning folders (`策划/资料*`, `事实核查.md`, `STORYLINES.md`) already list most sources; start there.
- The frontmatter `links` list becomes the numbered REFERENCES section: one entry per cited paper, `label` = `Authors (Year). Title.` (first author et al. when more than three), `url`, and `note` = venue or `arXiv` when known, for example:
  ```yaml
  links:
    - label: "Schulman et al. (2017). Proximal Policy Optimization Algorithms."
      url: https://arxiv.org/abs/1707.06347
      note: arXiv
  ```
  Our own code repositories go last.
- No `credits` field: the author removed credits from the site.

Facts: experiment numbers only from the episode's own results files (`策划/实验/结果.md` and similar) with their conditions; paper numbers only from the paper (check it) or the episode's fact-check notes. Do not add claims from memory that you have not checked against a source.

Images: keep the post's existing figure and stills and their captions (update a caption only if the text around it changed meaning). Place the block diagram where the method is introduced. Every image keeps alt text and a one-line caption in the title slot.

## Where the source material is

Video episodes: `~/Desktop/03_视频与录屏/02_主题视频/科普视频 2/NN_*/`.
Each has `README.md`, `发布文案.md`, `成片/` (the films and the vertical TikTok cover), `工程_横屏/` (narration script at `assets/vo/script.txt` or a similar path, STORYLINES, SPEC) and `策划/` (research, fact checks, experiment code and results; EP03's `策划` is a link to EP02's).
Set `LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8` before shell commands on these paths, and quote them (the folder name has a space).

## Checking your post

The dev server runs at `http://localhost:4321/blog/` and picks up new posts on its own.
Check `curl -s -o /dev/null -w '%{http_code}' http://localhost:4321/blog/posts/<slug>/` returns 200 and that the page text has no frontmatter error.
Do not run `npm run build`, `astro sync`, `npm install` or git commands: other posts are being written in parallel and the owner of the repo builds and commits.
