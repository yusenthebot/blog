import rss from "@astrojs/rss";
import type { APIContext } from "astro";
import { getPosts, postPath } from "../lib/posts";
import { SITE } from "../lib/site";

export async function GET(context: APIContext) {
  const posts = await getPosts();
  const base = import.meta.env.BASE_URL.replace(/\/$/, "");
  return rss({
    title: SITE.title,
    description: SITE.description,
    site: context.site ?? SITE.home,
    items: posts.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.date,
      link: `${base}${postPath(post)}`,
      categories: post.data.tags,
    })),
  });
}
