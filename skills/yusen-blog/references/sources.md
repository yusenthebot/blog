# Where the source material is

A post is written from the material behind the video or the social post, never from memory.
Read all of it before the scaffold; the facts, numbers and papers are already collected there.

## 科普 episodes (series `kepu`)

Episodes live in `~/Desktop/03_视频与录屏/02_主题视频/科普视频 2/NN_<短标题>_<主题>/`.
Set `LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8` before shell commands on these paths and quote them: the folder name has a space.

| Path | What it gives the post |
| --- | --- |
| `README.md` | What the episode is, its experiments and where everything is |
| `发布文案.md` | Title, 简介, hashtags (`new_post.py` reads 标题 and 话题标签 from it) |
| `成片/*_横屏.mp4` | The landscape film: cover, stills, duration, date (its mtime), the YouTube upload |
| `工程_横屏/` | Narration script (`assets/vo/script.txt` or similar), `STORYLINES.md` (the 核心 of the episode), `SPEC.md` |
| `策划/` | Research notes, `事实核查.md`, paper lists, experiment code and `实验/结果.md` with the real numbers and their conditions |

EP03's `策划` is a link to EP02's.
`~/Desktop/科普视频` is a broken link (it points at a folder named `科普视频`, the real one is `科普视频 2`): use the full path.

Since EP13 the folders also hold:

- `发布文案.md` with a `## 封面大字` section before `## 标题`, and a title of the form `outsider line｜technical line` (the series now writes titles for viewers outside the field). `new_post.py` keeps the part before `｜` as the working title; the blog title is still rewritten as `具体案例：方法` (see `writing.md`).
- `成片/仿真实拍_*.mp4`: a short clip of our own simulation at real speed, and `*_横屏_手机版.mp4`. The upload and the frames still come from `*_横屏.mp4`.
- `成片/旧版_*` folders: old cuts, never use them.

Episode numbers changed on 2026-11-10: the old EP13 (真机强化学习) was shelved to be redone and never published as a video, EP13 is now 机器人打球 and EP14 is 视觉编码器.
The blog still has `ep13-real-world-rl` from the old numbering; check with the user before adding a new `ep13-*` post (two posts would carry `episode: 13`).
The same episodes are also in the `kepu-video` skill's examples (`~/Developer/kepu-video-skill/`), which hold copies of the storylines, specs and post copy.
New episodes are made with the `kepu-video` skill; when an episode is finished there, its blog post is the next step here.

## 图文 posts (series `notes`)

Xiaohongshu tech posts have no single home; each one came from its own project:

| Post | Source |
| --- | --- |
| `jev-typesafe` | `~/Desktop/02_图片与3D素材/03_技术图稿/jev-figures/post/` (`xiaohongshu-post.md`, the figures, the X article) |
| `deepseek-super-agent` | `~/Downloads/superagent-study/` and the approved post in the shuorenhua skill's `references/superagent-approved-post.md` |
| `macmimic` | `~/macmimic` (README, results) and `~/Desktop/01_开发项目/03_研究与实验/macmimic/deliverables/宣传片/` |
| `stanford-agent-skill` | `~/Documents/Codex/2026-08-05/stanford-ai-agent-skill/` (`POST.zh-CN.md`, the repo) |

For a new notes post, ask the user where the post and its material are if it is not obvious, and use the post's publish date as `date`.

## Scope

Only the author's personal account (the 科普 series and personal tech posts).
Zeno company material (`~/Desktop/00_Zeno/`, the company 抖音/小红书) does not go on this blog.
