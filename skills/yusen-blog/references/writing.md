# Writing the article

The author asked (2026-11-09) for articles that are more technical: methods, formulas, paper sources with hyperlinks, and normal, correct Chinese grammar.
The loose spoken shuorenhua voice used for 小红书 and TikTok copy does NOT apply to the blog.

## Language and tone

- Standard written Chinese (规范书面语) in complete, grammatical sentences, the register of a good technical blog or the introduction of a survey.
- No spoken fragments, no dropped subjects, no slang (硬堆, 搬到, 挺有意思), no rhetorical setups (不是……而是……, 说白了, 你以为……其实……), no em dashes, no "这期视频".
- One space between Chinese and Latin letters, digits or inline math (`在 MuJoCo 中训练 3 个种子`, `状态 $x_t$ 的`); none before or after Chinese punctuation. `fix_spacing.py` fixes this mechanically.
- English technical terms stay in English; the first use of an acronym gets its full name once: `扩展卡尔曼滤波（Extended Kalman Filter，EKF）`.
- Be precise: what is simulated, how many seeds, what a metric measures, what is schematic.
- One sentence per source line (the author's Markdown convention); the `rehype-cjk-linebreak` plugin removes the stray space a line break would otherwise leave between Chinese sentences.

## Structure

Use `##` for sections and `###` for parts; the page builds its contents list from them.

1. Opening paragraph: the problem, why it is hard, what the article covers.
2. Problem setup and notation: state, action, observation, objective, written as math.
3. The method, the core and at least half of the article: the key equations in LaTeX, a derivation or intuition for each, what every symbol means right after the equation, and the algorithm as an ordered list of steps or a short pseudo-code block.
4. Representative work: the line of papers, each introduced by what it changed and cited inline as a link, e.g. `[Schulman et al., 2017](https://arxiv.org/abs/1707.06347)`.
5. Our experiment, when there is one: setup (simulator, robot model, policy size, training budget, seeds, hardware), a Markdown results table, the interpretation, the limitations.
6. A short conclusion: what to remember and the open problems.

Length: 2500 to 5000 Chinese characters of running prose, not counting formulas, tables, code or captions (`check_post.py` counts this way).

## Math

- Inline `$...$`, display `$$...$$` on their own lines; KaTeX renders them at build time.
- Standard LaTeX works on the page: `\mathbf{x}`, `\hat{x}`, `\mathbb{E}`, `\nabla_\theta`, `\operatorname{clip}`, `\begin{aligned}`. (The figure kit is the one with a restricted subset.)
- Formulas are the standard ones from the cited paper or textbook. When the article uses a simplified or teaching form (the video's version, a generic form of a family of methods), say so in the sentence.
- Check every formula renders: `verify_site.py --dev` counts `katex-error` on every page.

## Citations and references

- Every paper, model or dataset named in the text is a link to its arXiv abs page, the official paper page or the official project page.
- Open every URL before using it and check the page title matches the paper (`check_links.py` prints the titles). Never guess an arXiv id; the episode's `策划/` notes already list most sources.
- The frontmatter `links` list becomes the numbered REFERENCES section, one entry per cited paper, our own repositories last:

  ```yaml
  links:
    - label: "Schulman et al. (2017). Proximal Policy Optimization Algorithms."
      url: https://arxiv.org/abs/1707.06347
      note: arXiv
  ```

  `label` is `Authors (Year). Title.` (first author et al. when more than three), `note` the venue or `arXiv`.
- No `credits` field and no credits section: the author removed credits from the site.

## Facts

- Experiment numbers only from the episode's own results files, with their conditions (seeds, simulated or real).
- Paper numbers only from the paper itself or the episode's fact-check notes; say in the final report which ones came from notes and were not rechecked.
- Do not add claims from memory that were not checked against a source.

## Frontmatter

The schema is `src/content.config.ts`. `new_post.py` writes the skeleton; fill it like this:

```yaml
title: 没人教它走路：用 PPO 训练四足机器人的步态    # names the concrete case, may tighten the 发布文案 title
description: 从 MDP、策略梯度……到我们在 Mac CPU 上的实验。   # one or two sentences: method, papers, our experiment
date: 2026-11-03            # kepu: the 横屏 film's mtime; notes: the day the post went out
series: kepu                # kepu = episode, notes = 图文
episode: 7                  # kepu only
tags: [强化学习, PPO, 四足机器人]   # 3 to 6
cover: ./cover.jpg
coverAlt: 画面描述
duration: "2:24"            # from ffprobe; kepu, or notes with `video: true`
platforms: [douyin, tiktok] # notes: [xiaohongshu]
links: [...]                # references, as above
```

Leave `youtube` out until the video is uploaded; the page shows a placeholder until then.
`draft: true` keeps a post out of the build.
