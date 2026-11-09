import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";
import { unified } from "@astrojs/markdown-remark";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { rehypeFigure } from "./src/lib/rehype-figure.mjs";
import { rehypeCjkLinebreak } from "./src/lib/rehype-cjk-linebreak.mjs";

// Served from GitHub Pages as a project site: https://yusenthebot.github.io/blog/
export default defineConfig({
  site: "https://yusenthebot.github.io",
  base: "/blog",
  trailingSlash: "always",
  integrations: [sitemap()],
  markdown: {
    processor: unified({ remarkPlugins: [remarkMath], rehypePlugins: [rehypeKatex, rehypeFigure, rehypeCjkLinebreak] }),
    shikiConfig: { theme: "github-light" },
  },
});
