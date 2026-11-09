from pathlib import Path

import pytest

from yt_upload.manifest import (
    ManifestError,
    build_description,
    build_title,
    pending_jobs,
    read_post,
    write_video_id,
)

POST = """---
title: 200次观星：扩展卡尔曼滤波怎样把人送上月球
description: 先按模型猜，再拿传感器看，按信任程度改。
date: 2026-10-27
series: kepu
episode: 1
tags: [卡尔曼滤波, EKF, state estimation]
cover: ./cover.jpg
coverAlt: alt
duration: "1:33"
credits: |
  音乐 Mixkit
---

正文 <b>不动</b>
"""


def make_post(tmp_path: Path, slug: str = "ep01-ekf", text: str = POST) -> Path:
    d = tmp_path / slug
    d.mkdir()
    (d / "index.md").write_text(text, encoding="utf-8")
    return d / "index.md"


def test_title_and_description(tmp_path):
    post = read_post(make_post(tmp_path))
    assert build_title(post) == "200次观星：扩展卡尔曼滤波怎样把人送上月球 | EP01"
    desc = build_description(post)
    assert "https://yusenthebot.github.io/blog/posts/ep01-ekf/" in desc
    assert "音乐 Mixkit" in desc
    assert "#stateestimation" in desc


def test_pending_skips_uploaded_and_unmapped(tmp_path):
    film = tmp_path / "f.mp4"
    film.write_bytes(b"x")
    a = read_post(make_post(tmp_path, "a"))
    b = read_post(make_post(tmp_path, "b", POST.replace("duration:", "youtube: abcdefghijk\nduration:")))
    c = read_post(make_post(tmp_path, "c"))
    jobs = pending_jobs([a, b, c], {"a": film, "b": film})
    assert [j.slug for j in jobs] == ["a"]


def test_missing_film_is_an_error(tmp_path):
    post = read_post(make_post(tmp_path))
    with pytest.raises(ManifestError):
        pending_jobs([post], {"ep01-ekf": tmp_path / "nope.mp4"})


def test_write_video_id_keeps_body_and_lines(tmp_path):
    md = make_post(tmp_path)
    write_video_id(md, "dQw4w9WgXcQ")
    text = md.read_text(encoding="utf-8")
    assert 'duration: "1:33"\nyoutube: dQw4w9WgXcQ\n' in text
    assert text.endswith("正文 <b>不动</b>\n")
    write_video_id(md, "AAAAAAAAAAA")
    assert text.count("youtube:") == 1
    assert "youtube: AAAAAAAAAAA" in md.read_text(encoding="utf-8")


def test_rejects_bad_id(tmp_path):
    with pytest.raises(ManifestError):
        write_video_id(make_post(tmp_path), "short")
