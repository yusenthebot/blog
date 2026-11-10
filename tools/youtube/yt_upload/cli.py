"""yt-upload: plan, authorize and run YouTube uploads for the blog's films.

uv run yt-upload plan                       # dry run, no network
uv run yt-upload auth                       # one-time Google consent in the browser
uv run yt-upload upload --privacy unlisted  # upload pending films, write ids into posts
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from .manifest import (
    ManifestError,
    UploadJob,
    build_description,
    build_tags,
    build_title,
    load_film_map,
    load_posts,
    pending_jobs,
    uploaded_posts,
    write_video_id,
)

log = logging.getLogger("yt_upload")

TOOL_DIR = Path(__file__).resolve().parent.parent
REPO = TOOL_DIR.parent.parent
POSTS_DIR = REPO / "src" / "content" / "posts"
CRED_DIR = TOOL_DIR / ".credentials"
FILM_MAP = TOOL_DIR / "films.local.json"
UPLOAD_LOG = TOOL_DIR / "uploads.local.jsonl"

# Full `youtube` scope: upload, name the target channel before sending, and edit
# titles and privacy of videos already uploaded (`sync`).
SCOPES = ["https://www.googleapis.com/auth/youtube"]
CHUNK = 8 * 1024 * 1024
RETRY_STATUS = {500, 502, 503, 504}
MAX_RETRIES = 8


def _credentials(client_secret: Path, token: Path):
    # Imported lazily so `plan` works without the Google libraries' network stack.
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if token.exists():
        creds = Credentials.from_authorized_user_file(str(token))
        if not creds.has_scopes(SCOPES):
            creds = None  # token predates a scope change; ask for consent again
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        if not client_secret.exists():
            raise SystemExit(
                f"Missing OAuth client file: {client_secret}\n"
                "Create a 'Desktop app' OAuth client in Google Cloud Console (YouTube Data API v3 enabled), "
                "download its JSON and save it there. See tools/youtube/README.md."
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(client_secret), SCOPES)
        creds = flow.run_local_server(port=0, open_browser=True)
    token.parent.mkdir(parents=True, exist_ok=True)
    token.write_text(creds.to_json(), encoding="utf-8")
    token.chmod(0o600)
    return creds


def _service(args):
    from googleapiclient.discovery import build

    creds = _credentials(args.client_secret, args.token)
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def _channel_line(youtube) -> str:
    items = youtube.channels().list(part="id,snippet", mine=True).execute().get("items", [])
    if not items:
        raise SystemExit("The authorized Google account has no YouTube channel.")
    ch = items[0]
    parts = [
        ch["snippet"]["title"],
        ch["snippet"].get("customUrl"),
        f"https://www.youtube.com/channel/{ch['id']}",
    ]
    return " ".join(p for p in parts if p)


def _body(job: UploadJob, privacy: str) -> dict:
    return {
        "snippet": {
            "title": job.title,
            "description": job.description,
            "tags": list(job.tags),
            "categoryId": job.category_id,
            "defaultLanguage": "zh-Hans",
            "defaultAudioLanguage": "zh-Hans",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": job.synthetic_media,
        },
    }


def _upload_one(youtube, job: UploadJob, privacy: str) -> str:
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    media = MediaFileUpload(str(job.film), mimetype="video/mp4", chunksize=CHUNK, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=_body(job, privacy), media_body=media)
    response, retries = None, 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                log.info("  %s: %d%%", job.slug, int(status.progress() * 100))
            retries = 0
        except HttpError as e:
            reason = _reason(e)
            if e.resp.status in RETRY_STATUS:
                retries = _backoff(job.slug, retries, f"HTTP {e.resp.status}")
                continue
            if reason in {"quotaExceeded", "uploadLimitExceeded", "rateLimitExceeded"}:
                raise SystemExit(
                    f"Stopped: YouTube says {reason}. Pending posts stay pending; rerun later."
                ) from e
            raise
        except (ConnectionError, TimeoutError, OSError) as e:
            retries = _backoff(job.slug, retries, type(e).__name__)
    video_id = response.get("id")
    if not video_id:
        raise RuntimeError(f"{job.slug}: upload finished without a video id: {response}")
    return video_id


def _reason(e) -> str:
    try:
        return json.loads(e.content)["error"]["errors"][0]["reason"]
    except (ValueError, KeyError, IndexError, TypeError):
        return ""


def _backoff(slug: str, retries: int, why: str) -> int:
    retries += 1
    if retries > MAX_RETRIES:
        raise SystemExit(f"{slug}: giving up after {MAX_RETRIES} retries ({why})")
    wait = min(64, 2**retries) + random.random()
    log.warning("  %s: %s, retry %d in %.0f s", slug, why, retries, wait)
    time.sleep(wait)
    return retries


def _set_thumbnail(youtube, job: UploadJob, video_id: str) -> None:
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    if job.cover is None:
        return
    try:
        youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(job.cover))).execute()
    except HttpError as e:
        # Custom thumbnails need a phone-verified channel; the upload itself still counts.
        log.warning("  %s: thumbnail not set (%s); YouTube keeps an auto frame", job.slug, _reason(e) or e)


def _jobs(args) -> list[UploadJob]:
    films = load_film_map(args.films)
    if not films:
        raise SystemExit(f"No films mapped. Create {args.films} (see films.example.json).")
    only = set(args.only) if args.only else None
    return pending_jobs(load_posts(POSTS_DIR), films, only)


def cmd_plan(args) -> int:
    jobs = _jobs(args)
    if not jobs:
        print("Nothing to upload: every mapped post already has a youtube id.")
        return 0
    for j in jobs:
        size = j.film.stat().st_size / 1e6
        print(
            f"{j.slug}\n  title: {j.title}\n  film:  {j.film.name} ({size:.0f} MB)\n  tags:  {', '.join(j.tags)}"
        )
        print("  description:\n    " + j.description.replace("\n", "\n    "))
    print(f"\n{len(jobs)} upload(s) pending. Daily upload quota is 100 calls; this uses {len(jobs)}.")
    return 0


def cmd_auth(args) -> int:
    youtube = _service(args)
    print(f"Authorized. Token saved to {args.token}")
    print(f"Channel: {_channel_line(youtube)}")
    return 0


def cmd_upload(args) -> int:
    jobs = _jobs(args)
    if not jobs:
        print("Nothing to upload.")
        return 0
    youtube = _service(args)
    print(f"Channel: {_channel_line(youtube)}")
    print(f"{len(jobs)} film(s) will be uploaded as {args.privacy}:")
    for j in jobs:
        print(f"  - {j.slug}: {j.title}")
    if not args.yes and input("Proceed? [y/N] ").strip().lower() != "y":
        print("Cancelled.")
        return 1
    for j in jobs:
        log.info("uploading %s", j.slug)
        video_id = _upload_one(youtube, j, args.privacy)
        write_video_id(POSTS_DIR / j.slug / "index.md", video_id)
        with UPLOAD_LOG.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "slug": j.slug,
                        "id": video_id,
                        "privacy": args.privacy,
                        "at": datetime.now(UTC).isoformat(),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
        if args.thumbnail:
            _set_thumbnail(youtube, j, video_id)
        print(f"  {j.slug} -> https://youtu.be/{video_id}")
    return 0


def cmd_sync(args) -> int:
    """Push each uploaded post's title, description and tags to YouTube, optionally its privacy."""
    posts = uploaded_posts(load_posts(POSTS_DIR), set(args.only) if args.only else None)
    if not posts:
        print("No uploaded posts to sync.")
        return 0
    youtube = _service(args)
    print(f"Channel: {_channel_line(youtube)}")
    by_id = {str(p.data["youtube"]): p for p in posts}
    items = youtube.videos().list(part="snippet,status", id=",".join(by_id)).execute().get("items", [])
    missing = set(by_id) - {v["id"] for v in items}
    if missing:
        raise SystemExit(f"Not found on this channel: {', '.join(sorted(missing))}")
    changes = []
    for v in items:
        post = by_id[v["id"]]
        snippet = dict(v["snippet"])
        snippet.update(
            title=build_title(post), description=build_description(post), tags=list(build_tags(post))
        )
        status = dict(v["status"])
        if args.privacy:
            status["privacyStatus"] = args.privacy
        changes.append((post.slug, v, snippet, status))
        print(
            f"  {post.slug}: {v['snippet']['title']!r} -> {snippet['title']!r}, "
            f"{v['status']['privacyStatus']} -> {status['privacyStatus']}"
        )
    if not args.yes and input("Apply? [y/N] ").strip().lower() != "y":
        print("Cancelled.")
        return 1
    for slug, v, snippet, status in changes:
        keep = ("title", "description", "tags", "categoryId", "defaultLanguage", "defaultAudioLanguage")
        # videos.update replaces the whole status part: restate the AI-voice disclosure and the
        # audience flag every time, or they fall back to YouTube's defaults.
        body_status = {
            "privacyStatus": status["privacyStatus"],
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,
        }
        body_status.update(
            {k: status[k] for k in ("embeddable", "license", "publicStatsViewable") if k in status}
        )
        youtube.videos().update(
            part="snippet,status",
            body={
                "id": v["id"],
                "snippet": {k: snippet[k] for k in keep if k in snippet},
                "status": body_status,
            },
        ).execute()
        print(f"  {slug} updated: https://youtu.be/{v['id']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    p = argparse.ArgumentParser(
        prog="yt-upload", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--films", type=Path, default=FILM_MAP, help="slug -> film path map (JSON)")
    p.add_argument("--client-secret", type=Path, default=CRED_DIR / "client_secret.json")
    p.add_argument("--token", type=Path, default=CRED_DIR / "token.json")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("plan", "upload", "sync"):
        s = sub.add_parser(name)
        s.add_argument("--only", nargs="+", metavar="SLUG", help="limit to these posts")
    sub.add_parser("auth")
    up = sub.choices["upload"]
    up.add_argument("--privacy", choices=("private", "unlisted", "public"), default="private")
    up.add_argument("--thumbnail", action="store_true", help="also set cover.jpg as the thumbnail")
    up.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    sy = sub.choices["sync"]
    sy.add_argument("--privacy", choices=("private", "unlisted", "public"), help="also set privacy")
    sy.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    args = p.parse_args(argv)
    try:
        return {"plan": cmd_plan, "auth": cmd_auth, "upload": cmd_upload, "sync": cmd_sync}[args.cmd](args)
    except ManifestError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
