# yt-upload

Uploads the blog's episode films to YouTube and writes each video id back into the post's frontmatter, so the page swaps its placeholder for the player on the next build.

Titles, descriptions, tags and credits come from the posts themselves.
The description links back to the post on the blog.
Every upload is marked `containsSyntheticMedia` because the narration is an AI-cloned voice.

## One-time setup

1. In [Google Cloud Console](https://console.cloud.google.com/), create a project (or reuse one) and enable **YouTube Data API v3**.
2. Configure the OAuth consent screen as **External**, and add your own Google account under **Test users**.
3. Create credentials of type **OAuth client ID**, application type **Desktop app**, and download the JSON.
4. Save it as `tools/youtube/.credentials/client_secret.json`. The folder is git-ignored.
5. Copy `films.example.json` to `films.local.json` and map each post slug to its landscape film. This file is git-ignored too, since it holds paths on your machine.
6. Run `uv run yt-upload auth`. A browser window opens, you pick the channel's Google account and allow uploads; the token is saved to `.credentials/token.json` (mode 600).

## Use

```bash
cd tools/youtube
uv run yt-upload plan                          # dry run: shows every pending upload, no network
uv run yt-upload upload --privacy private      # uploads, asks before starting
uv run yt-upload upload --only ep01-ekf --privacy unlisted --thumbnail
```

Posts that already have a `youtube:` id are skipped, so a run that stops halfway can simply be repeated.
Each finished upload is appended to `uploads.local.jsonl`.
After uploading, rebuild and deploy the blog so the players appear.

## Limits worth knowing

- Uploads use their own quota bucket: 1 unit per upload, 100 uploads a day by default (YouTube Data API docs, checked 2026-11-09).
- The channel has its own daily cap on top of that: a channel that is not phone-verified stopped at 10 uploads on 2026-11-10 with `uploadLimitExceeded`. Rerun the next day; finished posts are skipped.
- Behind an HTTP proxy (`HTTPS_PROXY`), the Google client needs PySocks, which is a dependency for that reason.
- Custom thumbnails (`--thumbnail`) need a phone-verified channel; without it the upload still succeeds and YouTube picks a frame.
- Default privacy is `private`; switch videos to public in YouTube Studio, or rerun with `--privacy public` for new uploads.
