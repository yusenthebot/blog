import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

const posts = defineCollection({
  loader: glob({ pattern: "*/index.md", base: "./src/content/posts" }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      description: z.string(),
      date: z.coerce.date(),
      // "kepu" = the 科普视频 series, "notes" = 图文 posts
      series: z.enum(["kepu", "notes"]),
      episode: z.number().int().positive().optional(),
      tags: z.array(z.string()).default([]),
      cover: image(),
      coverAlt: z.string(),
      // YouTube video id (not the URL). Empty until the video is uploaded.
      youtube: z.string().regex(/^[A-Za-z0-9_-]{11}$/).optional(),
      // Title used on YouTube only, in the X post style; the page keeps `title`.
      youtubeTitle: z.string().max(100).optional(),
      duration: z.string().optional(),
      // notes posts that come with a film (kepu posts always show the player)
      video: z.boolean().default(false),
      platforms: z.array(z.enum(["douyin", "xiaohongshu", "tiktok", "youtube"])).default([]),
      // References: papers, code and project pages, rendered as a numbered list under the article.
      links: z
        .array(z.object({ label: z.string(), url: z.string().url(), note: z.string().optional() }))
        .default([]),
      draft: z.boolean().default(false),
    }),
});

export const collections = { posts };
