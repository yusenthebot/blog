---
name: yusen-blog
description: >
  Write, revise and publish posts on Yusen Xie's personal blog (YUSEN_BLOG, https://yusenthebot.github.io/blog/,
  repo ~/Developer/blog): technical Chinese articles about robotics and AI with formulas, methods and linked papers,
  one block-diagram-drawer figure each, film stills, and the episode video on YouTube. Use this skill whenever the
  user wants a new blog post or 博客/图文 article, wants a 科普视频 episode or a 小红书/抖音 post turned into a blog post,
  asks to rewrite, fix, extend or re-check a post, to add references or formulas, to change the blog's look or layout,
  to publish or deploy the blog, or to upload the episode films to YouTube, even if they only say "the blog" or "博客".
---

# YUSEN_BLOG (yusen-blog)

The blog holds the written versions of the author's 科普视频 episodes (series `kepu`) and Xiaohongshu tech posts (series `notes`).
Each post is a technical article in standard written Chinese with LaTeX formulas, the method as ordered steps, papers cited as hyperlinks, our own experiment with real numbers, one paper-style block diagram, and the film on YouTube.
The site is Astro 6 on GitHub Pages under `/blog`, in a light terminal look: white paper, VT323 and Fusion Pixel for display type, JetBrains Mono for text, one orange accent.

The repository is the source of truth: `src/content/posts/ep07-quadruped-rl/` is a complete episode post and `src/content/posts/stanford-agent-skill/` a complete notes post; read one before writing.
Scripts in this skill find the repository from their own location (set `BLOG_ROOT` if they are copied elsewhere) and need only Python 3 and ffmpeg.

## The standard, in one paragraph

The author asked for articles that are technical: methods, formulas, paper sources with links, and normal, correct Chinese grammar; the loose spoken shuorenhua voice of the social posts does not apply here.
An article states the problem as math, spends at least half its length on the method (equations, what each symbol means, the algorithm as steps), introduces the papers that changed the field with links, reports our experiment with its setup and a results table, and ends with what to remember.
Every number comes from a paper we checked or from the episode's own results files; every link was opened and its title matches the citation; anything simplified or schematic says so.
No credits anywhere on the site (the author removed them on 2026-11-09).

## Before touching the repo

Other sessions (Claude Code, Codex, temporary worktrees) edit and push this repo, so the local checkout is often not what is live.
Run this first and read the result:

```bash
cd ~/Developer/blog && git fetch -q && git status -sb && git log --oneline HEAD..origin/main
```

- `origin/main` is what is live. If the checkout is behind, read what landed (`git diff HEAD origin/main --stat`) before judging the site from local files.
- Uncommitted changes you did not make belong to another session: do not edit, stage, stash or discard those files, and say they are there. If your task needs one of them, ask the user first.
- When the checkout is behind and dirty, do not pull or rebase over it. Work that touches other files can be committed locally and rebased later; work on the same files waits for the user's call.

## Pipeline

| Stage | What happens | Read or run |
| --- | --- | --- |
| 1. Source | Read the episode folder (`README.md`, `发布文案.md`, script, `策划/` research, fact checks and results) or the original post | `references/sources.md` |
| 2. Scaffold | Create the post folder, frontmatter, section skeleton, film map and contact sheets | `scripts/new_post.py` |
| 3. Images | Cover and 2 to 4 stills from the film, picked from the contact sheets and looked at | `scripts/frames.py`, `references/images-and-figure.md` |
| 4. Figure | One block diagram with `block-diagram-drawer`, gated with `--strict-tidy`, placed where the method starts | `references/images-and-figure.md` |
| 5. Article | Write the technical article and the `links` references | `references/writing.md` |
| 6. Check | House-rule lint, spacing fix, link fetch with titles, render check on the dev server | `scripts/check_post.py`, `scripts/fix_spacing.py`, `scripts/check_links.py`, `scripts/verify_site.py --dev` |
| 7. Publish | Build, commit, push to `main` (Actions deploys), verify the live site | `references/publish.md`, `scripts/verify_site.py` |
| 8. Video | Write the `youtubeTitle`, upload the film to YouTube (id is written back into the post), `sync` later title or privacy changes | `references/publish.md` (YouTube section), `tools/youtube/` |

Site design changes (fonts, colours, layout, components) follow `references/design.md`.
Traps that each cost a round before are in `references/lessons.md`; skim it before a session on this repo.

## Commands

```bash
S=~/.claude/skills/yusen-blog/scripts
python3 $S/new_post.py ep14-some-topic --dry-run --episode-dir "$HOME/Desktop/03_视频与录屏/02_主题视频/科普视频 2/14_..."
python3 $S/new_post.py some-topic --notes --date 2026-11-20 --title "工作标题"
python3 $S/frames.py cover FILM 0:42 src/content/posts/SLUG/cover.jpg
python3 $S/frames.py still FILM 1:05 src/content/posts/SLUG/still-NAME.jpg
python3 $S/check_post.py SLUG            # or --all
python3 $S/fix_spacing.py SLUG --write   # dry run without --write
python3 $S/check_links.py SLUG
python3 $S/verify_site.py --dev          # dev server; no flag = live site
```

Drop `--dry-run` once the printed frontmatter looks right.
`scripts/layout_check.js` is a snippet for the browser pane (javascript_tool): it measures every page at several widths for elements under the contents rail, horizontal scroll and orphaned headline characters.

The dev server is the `yusen-blog` entry in `~/Desktop/.claude/launch.json` (preview_start `{name: "yusen-blog"}`), at `http://localhost:4321/blog/`.

## Gates (stop and ask the user)

- Before `git push` (it deploys the public site), unless the user already said to publish this change.
- Before any YouTube upload or `sync`, and before making an uploaded video public. The tool prints the target channel first: read it.
- Before touching files another session left uncommitted, and before pulling or rebasing over them.
- Before publishing anything whose licence forbids it (the MacMimic rollout footage derives from LAFAN1, CC BY-NC-ND: no frames, no video).
- Before a new npm or Python dependency, or a change to the post schema (`src/content.config.ts`).

## Done means

The checkout was compared with `origin/main` first, `check_post.py` passes with no errors, `check_links.py` has no dead links and every title matches its citation, `verify_site.py --dev` shows 0 KaTeX errors, the page was looked at in the browser (figure, stills, formulas, contents list, references), and for a publish `npm run build` is clean and `verify_site.py` passes on the live site.
Report what is unverified (numbers taken from the episode's notes, formulas we simplified, links only checked by hand).
