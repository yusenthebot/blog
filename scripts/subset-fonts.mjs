// Subsets the pixel CJK fonts to the characters the site actually uses, so a page
// downloads tens of kilobytes instead of the full 600 KB font. Runs before dev and build.
import { readFile, writeFile, mkdir, readdir } from "node:fs/promises";
import { join, extname } from "node:path";
import subsetFont from "subset-font";

const ROOT = new URL("..", import.meta.url).pathname;
const SCAN_DIRS = ["src"];
const SCAN_EXT = new Set([".md", ".mdx", ".astro", ".ts", ".mjs"]);
const FONTS = [
  {
    src: "node_modules/@fontsource/fusion-pixel-12px-proportional-sc/files/fusion-pixel-12px-proportional-sc-latin-400-normal.woff2",
    out: "src/assets/fonts/pixel-12.woff2",
  },
];
// Always keep ASCII, common CJK punctuation and digits, so short UI strings never fall back.
const BASE = Array.from({ length: 95 }, (_, i) => String.fromCharCode(32 + i)).join("") + "，。、；：？！“”‘’（）《》【】—…·「」";

async function* walk(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const p = join(dir, entry.name);
    if (entry.isDirectory()) yield* walk(p);
    else if (SCAN_EXT.has(extname(entry.name))) yield p;
  }
}

const chars = new Set(BASE);
for (const d of SCAN_DIRS) {
  for await (const file of walk(join(ROOT, d))) {
    for (const ch of await readFile(file, "utf8")) chars.add(ch);
  }
}
const text = [...chars].join("");

await mkdir(join(ROOT, "src/assets/fonts"), { recursive: true });
for (const { src, out } of FONTS) {
  const full = await readFile(join(ROOT, src));
  const subset = await subsetFont(full, text, { targetFormat: "woff2" });
  await writeFile(join(ROOT, out), subset);
  console.log(`[fonts] ${out}: ${chars.size} chars, ${(subset.length / 1024).toFixed(0)} KB`);
}
