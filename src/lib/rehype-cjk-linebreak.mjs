// Posts keep one sentence per source line. HTML turns each line break into a space, which
// shows up as a gap after Chinese punctuation ("失效。 PPO") or between two Chinese characters.
// Drop the break there; keep it as a normal space between Latin words.
const CJK = "\\u3400-\\u4dbf\\u4e00-\\u9fff\\uf900-\\ufaff";
const CJK_PUNCT = "\\u3000-\\u303f\\uff00-\\uffef\\u2018-\\u201d";
const AFTER_PUNCT = new RegExp(`([${CJK_PUNCT}])[ \\t]*\\n[ \\t]*`, "g");
const BETWEEN_CJK = new RegExp(`([${CJK}])[ \\t]*\\n[ \\t]*(?=[${CJK}${CJK_PUNCT}])`, "g");
const SKIP = new Set(["code", "pre", "script", "style", "math", "annotation"]);

function walk(node) {
  if (!node.children) return;
  for (const child of node.children) {
    if (child.type === "text") {
      child.value = child.value.replace(AFTER_PUNCT, "$1").replace(BETWEEN_CJK, "$1");
    } else if (child.type === "element" && !SKIP.has(child.tagName)) {
      const cls = child.properties?.className;
      if (Array.isArray(cls) && cls.some((c) => String(c).startsWith("katex"))) continue;
      walk(child);
    }
  }
}

export function rehypeCjkLinebreak() {
  return (tree) => walk(tree);
}
