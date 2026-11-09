// Line breaks for Chinese headlines.
// Headlines use `word-break: keep-all`, so Chinese text only breaks where a <wbr> allows it.
// We put <wbr> between Chinese words found by Intl.Segmenter, after merging single characters
// into their neighbours (the segmenter splits 卡尔|曼 and 步|态), so a line never ends inside a
// word and a lone character never lands on the last line.

const segmenter = new Intl.Segmenter("zh", { granularity: "word" });
const CJK = /[㐀-䶿一-鿿豈-﫿]/;
const PUNCT = /^[　-〿＀-￯‘-”、，。：；！？（）《》“”]+$/;

/** Split text into unbreakable pieces; a break is allowed between two consecutive pieces. */
export function cjkPieces(text) {
  const raw = [...segmenter.segment(text)].map((s) => s.segment);
  const pieces = [];
  for (const seg of raw) {
    const prev = pieces[pieces.length - 1];
    const single = seg.length === 1 && CJK.test(seg);
    if (prev !== undefined && PUNCT.test(seg)) {
      pieces[pieces.length - 1] = prev + seg; // never start a line with punctuation
    } else if (prev !== undefined && single && CJK.test(prev.slice(-1))) {
      pieces[pieces.length - 1] = prev + seg; // 卡尔+曼, 步+态
    } else {
      pieces.push(seg);
    }
  }
  return pieces;
}

const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" };
const escape = (s) => s.replace(/[&<>"]/g, (c) => ESC[c]);

/** HTML for a headline with <wbr> between Chinese words. */
export function wbrHtml(text) {
  const pieces = cjkPieces(text);
  return pieces
    .map((p, i) => {
      const next = pieces[i + 1];
      const breakHere = next !== undefined && CJK.test(p.slice(-1)) && CJK.test(next[0]);
      return escape(p) + (breakHere ? "<wbr>" : "");
    })
    .join("");
}

/** Rehype plugin: the same treatment for h2 and h3 in posts. */
export function rehypeCjkHeadings() {
  const visit = (node) => {
    if (!node.children) return;
    if (node.type === "element" && (node.tagName === "h2" || node.tagName === "h3")) {
      node.children = node.children.flatMap((child) => {
        if (child.type !== "text") return [child];
        const pieces = cjkPieces(child.value);
        const out = [];
        pieces.forEach((p, i) => {
          out.push({ type: "text", value: p });
          const next = pieces[i + 1];
          if (next !== undefined && CJK.test(p.slice(-1)) && CJK.test(next[0])) {
            out.push({ type: "element", tagName: "wbr", properties: {}, children: [] });
          }
        });
        return out;
      });
      return;
    }
    node.children.forEach(visit);
  };
  return (tree) => visit(tree);
}
