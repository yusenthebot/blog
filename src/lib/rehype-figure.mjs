// Turns a paragraph that holds only an image with a title into
// <figure><img><figcaption>, so Markdown stays plain:
//   ![alt](./fig.png "Caption text")
function isWhitespace(node) {
  return node.type === "text" && !node.value.trim();
}

function walk(node) {
  if (!node.children) return;
  node.children = node.children.map((child) => {
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
