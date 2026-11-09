# Check, publish and upload

## Check a post

```bash
S=~/.claude/skills/yusen-blog/scripts
python3 $S/check_post.py SLUG          # house rules; errors must be zero
python3 $S/fix_spacing.py SLUG         # dry run, then --write
python3 $S/check_links.py SLUG         # status + title of every cited URL
python3 $S/verify_site.py --dev        # every page 200, 0 KaTeX errors, assets resolve
```

- `check_links.py` marks hosts that block scripts (doi.org, X, AIAA, NASA NTRS) as `HAND`: open them in the browser or confirm the paper through its arXiv or publisher page, and say so in the report.
- A 200 is not enough: read the printed title and compare it with the citation.
- Then look at the page in the browser pane (preview_start `{name: "yusen-blog"}`, open `/blog/posts/<slug>/`): the figure, the stills, the formulas, the contents list on the right (wide screens), the REFERENCES list, and the page at 375 px wide with no horizontal scroll.

## Build

```bash
cd ~/Developer/blog
npm run build                     # runs the font subset first; must finish with no warnings
grep -rl katex-error dist | wc -l # 0
```

The build subsets the pixel font to the characters the site uses (`scripts/subset-fonts.mjs`, about 45 KB); a new post with new characters needs this rebuild, which `predev` and `prebuild` do on their own.

## Publish (gate: the user says go)

- Repository: `github.com/yusenthebot/blog`, public, branch `main` only. Commits use the repo-local noreply email `89848950+yusenthebot@users.noreply.github.com`; keep it, so the personal email never lands in a public commit.
- Commit messages: Conventional Commits, no co-author or attribution lines.
- Never commit `tools/youtube/films.local.json`, `tools/youtube/.credentials/`, `.work/`, `.env`, `dist/` (all git-ignored; check `git status` anyway).
- `git push` deploys: `.github/workflows/deploy.yml` builds on Node 22 and publishes with GitHub Pages (Actions source). Watch it with `gh run watch <id> --exit-status`.
- Then `python3 $S/verify_site.py` against the live site. A brand-new page can 404 for a minute while the CDN catches up; rerun before calling it broken.

## YouTube (gate: the user says upload)

The uploader is `tools/youtube` (uv project `yt-upload`); its README has the one-time Google Cloud setup.

1. The user creates a Desktop-app OAuth client and saves it as `tools/youtube/.credentials/client_secret.json`; never ask for or handle the secret's contents.
2. `cd tools/youtube && uv run yt-upload auth` once (browser consent, token saved with mode 600).
3. `uv run yt-upload plan` lists pending uploads: posts with a film in `films.local.json` and no `youtube:` id. `new_post.py` adds the film mapping for new episodes.
4. `uv run yt-upload upload --privacy private` (default), or `--only SLUG`, `--thumbnail` to set `cover.jpg`. It writes each video id into the post's frontmatter after `duration:`.
5. Rebuild and push so the player replaces the placeholder; switching videos to public is the user's call in YouTube Studio.

Facts that shape the uploader (YouTube Data API docs, checked 2026-11-09): `videos.insert` uses its own quota bucket of 100 uploads a day, uploads from unverified projects are no longer forced private, and every upload is flagged `containsSyntheticMedia` because the narration is the author's AI-cloned voice.
Never upload the MacMimic film (LAFAN1, CC BY-NC-ND); it is not in the film map on purpose.
