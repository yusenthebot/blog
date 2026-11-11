// Layout check for the blog, to paste into the browser pane (javascript_tool) on any page of the
// site (dev server or live). It loads every page in a hidden iframe at each width and reports:
//   under-rail  an article element that reaches under or past the contents rail
//   off-page    an element that leaves the viewport sideways
//   h-scroll    the page scrolls horizontally
//   orphan      a headline whose last line is under 18 % of its box (a lone character)
//   overflow    a headline wider than its box
// One width per call keeps each call under the tool's time limit:
//   await layoutCheck(375)   then 1000, 1199, 1200, 1440, 1920
// On the dev server, load this file without pasting it:
//   (0, eval)((await import("/blog/@fs/<absolute path of this file>?raw")).default)
// (1199 and 1200 are the two sides of the breakpoint where the contents list becomes a rail.)
// A clean run returns { width, pages, count: 0, problems: [] }. The same problems at every width
// mean the check itself is broken, not the site.

window.layoutCheck = async (width) => {
  const base = location.pathname.startsWith("/blog") ? "/blog" : "";
  const home = await fetch(`${base}/`).then((r) => r.text());
  const posts = [...new Set([...home.matchAll(/href="([^"]*\/posts\/[^"#?]+\/)"/g)].map((m) => m[1]))];
  const pages = [`${base}/`, `${base}/about/`, ...posts];

  const frame = document.createElement("iframe");
  // max-width:none because the site's own CSS caps iframes at the page width.
  frame.style.cssText = `position:fixed;left:0;top:0;width:${width}px;max-width:none;height:900px;opacity:0;pointer-events:none`;
  document.body.appendChild(frame);
  if (Math.round(frame.getBoundingClientRect().width) !== width) {
    frame.remove();
    throw new Error(`the iframe is ${frame.offsetWidth}px wide, not ${width}px: results would be meaningless`);
  }
  const problems = [];
  const name = (url) => url.split("/").filter(Boolean).pop() ?? "home";

  try {
    for (const url of pages) {
      frame.src = url;
      await new Promise((resolve) => (frame.onload = resolve));
      await new Promise((resolve) => setTimeout(resolve, 250));
      const doc = frame.contentDocument;
      const page = name(url);

      // The rail only limits content when it is docked beside the article (wide screens).
      const rail = doc.querySelector(".toc-rail") ?? doc.querySelector(".toc");
      const docked = rail && getComputedStyle(rail).position === "absolute";
      const railLeft = docked ? rail.getBoundingClientRect().left : Infinity;

      for (const el of doc.querySelectorAll(".prose > *, .prose figure img, .prose .table-wrap, .refs, .media")) {
        const box = el.getBoundingClientRect();
        if (box.width === 0) continue;
        const label = `${el.tagName.toLowerCase()}${el.className ? "." + String(el.className).split(" ")[0] : ""}`;
        if (box.right > railLeft - 8) problems.push(`${page}: under-rail ${label}`);
        else if (box.left < 0 || box.right > width) problems.push(`${page}: off-page ${label}`);
      }
      if (doc.documentElement.scrollWidth > doc.documentElement.clientWidth) problems.push(`${page}: h-scroll`);

      for (const el of doc.querySelectorAll(".article-title, .card-title, .prose h2, .prose h3, .pager .t")) {
        const range = doc.createRange();
        range.selectNodeContents(el);
        const lines = {};
        for (const rect of range.getClientRects()) {
          if (rect.width > 0) lines[Math.round(rect.top / 4)] = (lines[Math.round(rect.top / 4)] ?? 0) + rect.width;
        }
        const widths = Object.values(lines);
        const boxWidth = el.getBoundingClientRect().width;
        const text = el.textContent.trim().slice(0, 24);
        if (widths.length > 1 && widths.at(-1) < 0.18 * boxWidth) problems.push(`${page}: orphan "${text}"`);
        if (el.scrollWidth > el.clientWidth + 1) problems.push(`${page}: overflow "${text}"`);
      }
    }
  } finally {
    frame.remove();
  }
  const unique = [...new Set(problems)];
  // Capped so a broken run (hundreds of identical lines) does not flood the tool result.
  return { width, pages: pages.length, count: unique.length, problems: unique.slice(0, 40) };
};
"layoutCheck ready: await layoutCheck(375)";
