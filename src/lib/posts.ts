import { getCollection, type CollectionEntry } from "astro:content";

export type Post = CollectionEntry<"posts">;

/** Published posts, newest first; ties (same day) fall back to episode order. */
export async function getPosts(): Promise<Post[]> {
  const posts = await getCollection("posts", ({ data }) => !data.draft);
  return posts.sort(
    (a, b) =>
      b.data.date.getTime() - a.data.date.getTime() || (b.data.episode ?? 0) - (a.data.episode ?? 0),
  );
}

export function postPath(post: Post): string {
  return `/posts/${post.id}/`;
}
