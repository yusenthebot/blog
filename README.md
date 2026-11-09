# YUSEN_BLOG

Personal blog of Yusen Xie: the 图文 versions of the robotics and AI explainer videos and the Xiaohongshu tech posts, each with paper-style block diagrams.
Live at https://yusenthebot.github.io/blog/ (look and fonts follow https://yusenthebot.github.io/).

## Stack

- Astro 6 static site, Markdown posts in `src/content/posts/<slug>/index.md` with their images beside them.
- Figures are drawn as code with the `block-diagram-drawer` kit: build scripts in `figures/src/`, output in `figures/`.
- Videos live on YouTube; `tools/youtube` uploads the films and writes the ids into the posts.

## Develop

```bash
npm install
npm run dev      # http://localhost:4321/blog/
npm run build    # static site in dist/
```

Pushing to `main` deploys to GitHub Pages through `.github/workflows/deploy.yml`.

## Writing a post

Posts are made with the `yusen-blog` Claude Code skill in `skills/yusen-blog/`: pipeline, writing rules, design notes and the scripts that scaffold a post, cut frames and check posts, links and the live site.
Install it with `ln -s "$PWD/skills/yusen-blog" ~/.claude/skills/yusen-blog`.

## Rebuilding a figure

```bash
cd figures/src
python3 fig_ep01_ekf.py
python3 qa_svg_figure.py ../ep01-ekf-figure.svg --png --strict-tidy
cp ../ep01-ekf-figure.png ../../src/content/posts/ep01-ekf/fig-ekf.png
```

The QA gate needs Chrome or Chromium (`CHROME_PATH` if it is not found).
