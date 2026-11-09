// Turns a paragraph that holds only an image with a title into
// <figure><img><figcaption>, so Markdown stays plain:
//   ![alt](./fig.png "Caption text")
function isWhitespace(node) {
  return node.type === "text" && !node.value.trim();
}

const textOf = (node) => (node.type === "text" ? node.value : (node.children ?? []).map(textOf).join(""));

// Short cells (numbers like "94.5 / 71.1 / 81.6%", "约 1.7 只") must not wrap mid-value;
// longer prose cells still wrap, and the scroll box takes any extra width on phones.
const SHORT_CELL = 24;
function markShortCells(node) {
  if (node.type === "element" && (node.tagName === "td" || node.tagName === "th")) {
    if (textOf(node).trim().length <= SHORT_CELL) {
      node.properties = { ...node.properties, className: [...(node.properties?.className ?? []), "nw"] };
    }
    return;
  }
  (node.children ?? []).forEach(markShortCells);
}

function walk(node) {
  if (!node.children) return;
  node.children = node.children.map((child) => {
    // Tables sit in a scroll box, so the table itself can span the column and still scroll on phones.
    if (child.type === "element" && child.tagName === "table") {
      markShortCells(child);
      return { type: "element", tagName: "div", properties: { className: ["table-wrap"] }, children: [child] };
    }
    if (child.type === "element" && child.tagName === "p") {
      const kids = child.children.filter((k) => !isWhitespace(k));
      const img = kids[0];
      if (kids.length === 1 && img.type === "element" && img.tagName === "img" && img.properties?.title) {
        const caption = String(img.properties.title);
        delete img.properties.title;
        return {
          type: "element",
          tagName: "figure",
          // block diagrams (fig-*.png) get the wide measure; film stills stay at text width
          properties: { className: String(img.properties.src ?? "").includes("fig-") ? ["fig", "wide"] : ["fig"] },
          children: [
            img,
            { type: "element", tagName: "figcaption", properties: {}, children: [{ type: "text", value: caption }] },
          ],
        };
      }
    }
    walk(child);
    return child;
  });
}

export function rehypeFigure() {
  return (tree) => walk(tree);
}
