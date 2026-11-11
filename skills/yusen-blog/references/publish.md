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

The channel is https://www.youtube.com/@yusenthebot, linked from the header and the About page.
The uploader is `tools/youtube` (uv project `yt-upload`); its README has the one-time Google Cloud setup, which is done: the OAuth client and token are in `tools/youtube/.credentials/` (git-ignored; never read, print or copy them).
State on 2026-11-11: EP01 to EP14 are uploaded and public; the notes posts have no film (MacMimic's is excluded).
A private video cannot play in the blog's player, so upload as unlisted when the post is going live and public is not yet approved.

For a post:

1. Write `youtubeTitle` in the frontmatter (`writing.md` has the style); `check_post.py` warns when a kepu post has none.
2. `cd tools/youtube && uv run yt-upload plan` lists pending uploads without touching the network: posts with a film in `films.local.json` and no `youtube:` id. `new_post.py` adds the film mapping for new episodes.
3. `uv run yt-upload upload --privacy private` (the default), or `--only SLUG`, `--thumbnail` to set `cover.jpg`. It prints `Channel: ...` before sending anything: confirm it is @yusenthebot. Each finished upload writes its id into the post after `duration:` and is logged in `uploads.local.jsonl`.
4. Add `youtube` to the post's `platforms`, rebuild and push so the player replaces the placeholder. `verify_site.py` fails a page whose post has an id but no embed.
5. `uv run yt-upload sync [--only SLUG] [--privacy public]` pushes the post's current title, description and tags to videos that are already up, and optionally changes privacy. It lists every change (old title to new title, old privacy to new) and asks before applying. Use it after editing `youtubeTitle` or `description`; making videos public is the user's call.

What shapes the tool (YouTube Data API docs checked 2026-11-09, limits hit 2026-11-10):

- `videos.insert` has its own quota bucket of 100 uploads a day, but a channel that is not phone-verified stops at 10 uploads a day with `uploadLimitExceeded`. Rerun the next day; finished posts are skipped.
- Custom thumbnails need a phone-verified channel too; without it the upload still succeeds.
- The token has the full `youtube` scope (upload, read the channel, edit videos). A token from before a scope change is refused and `auth` asks for consent again.
- `videos.update` replaces the whole `status` part, so `sync` restates `containsSyntheticMedia: true` (the narration is the author's AI-cloned voice) and `selfDeclaredMadeForKids: false` every time. Keep that if the tool is edited.
- Behind an HTTP proxy (`HTTPS_PROXY`) the Google client needs PySocks, which is a dependency for that reason.
- The description is the post's `description`, a link to the blog post and three hashtags; there are no credits.

Never upload the MacMimic film (LAFAN1, CC BY-NC-ND); it is not in the film map on purpose.
EP1's Earth texture is CC BY 4.0 and its video went up without an attribution line; raise it with the user if descriptions are edited.
