export const SITE = {
  name: "YUSEN_BLOG",
  title: "Yusen Xie · Blog",
  description: "Robotics and AI, explained with real experiments. 机器人与 AI 技术文章：方法、公式、论文和实验。",
  author: "Yusen Xie",
  home: "https://yusenthebot.github.io/",
  github: "https://github.com/yusenthebot",
  youtube: "https://www.youtube.com/@yusenthebot",
} as const;

export const SERIES = {
  kepu: { label: "科普视频", short: "VIDEO" },
  notes: { label: "图文", short: "NOTE" },
} as const;

export function withBase(path: string): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, "");
  return `${base}${path.startsWith("/") ? path : `/${path}`}`;
}

export function formatDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}
