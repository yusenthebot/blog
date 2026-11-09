"""EP02 figure: how RT-2 turns a camera frame and a sentence into action tokens (VLA, part 1).

Crops are frames from the episode film (Blender, MuJoCo and Three.js layers). Attention arcs are
marked schematic in the film itself; the 256-bin landscape is a real softmax over seeded logits;
the 32 % and 62 % come from the RT-2 paper (fact check A_2022-2024_奠基.md and the film narration).
"""

from pathlib import Path

from figkit import MUTED, HAIR, INK, PAL, WIRE, Fig

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets" / "ep02-vla-1"
OUT = HERE.parent / "ep02-vla-1-vla-figure.svg"

f = Fig(1400, 440)
LABEL, MODULE = f.fs("label"), f.fs("module")
TOP_Y, BOT_Y = 8, 432
GAP = 30
W = 4
widths = (321,) * W
PX = f.place(8, 1392, widths, gap=GAP)


def name(x, y, s, color=INK, box=None, anchor="start"):
    f.text(x, y, s, size=MODULE, weight=500, color=color, box=box, anchor=anchor)


def note(x, y, s, box=None, anchor="start", color=MUTED):
    f.text(x, y, s, size=LABEL, color=color, box=box, anchor=anchor, family="serif", italic=True)


def column(i, title, role, img, label, sym, chips, foot, key=False, fit="cover"):
    x = PX[i]
    top = f.panel(x, TOP_Y, widths[i], BOT_Y - TOP_Y, role, title)
    cx, cw = x + 10, widths[i] - 20
    card = f.card(cx, top + 4, cw, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=PAL[role].accent if key else HAIR)
    ix, iw = cx + 12, cw - 24
    f.image(ASSETS / img, ix, top + 16, iw, 150, fit=fit)
    name(ix, top + 198, label, color=PAL[role].deep, box=card)
    if sym:
        f.text(ix + iw, top + 198, sym, size=MODULE, anchor="end", box=card)
    for k, (s, fam) in enumerate(chips):
        f.chip(ix, top + 214 + 48 * k, iw, 40, s, role, size=LABEL, fill="#FFFFFF", stroke=PAL[role].accent,
               color=INK, family=fam)
    note(ix, top + 214 + 48 * len(chips) + 28, foot, box=card)
    return card


ca = column(0, "(a) Tokens", "gray", "tokens.jpg", "Image + text", "$256+5$",
            [("16×16 patches", "sans"), ("pick up the extinct animal", "serif")],
            "one token per patch")
cb = column(1, "(b) Transformer", "blue", "attention.jpg", "Attention", "$\\times L$",
            [("$\\mathrm{softmax}(QK^{\\top})V$", "sans"), ("extinct ↔ dinosaur", "mono")],
            "schematic arcs")
cc = column(2, "(c) Action tokens", "orange", "action.jpg", "Action", "$8\\times256$",
            [("$\\hat{n}=\\arg\\max_b\\,p(b)$", "sans"), ("1  128  91  241 …", "mono")],
            "one number at a time", fit="contain")
cd = column(3, "(d) Result", "green", "result.jpg", "Unseen tasks", "",
            [("RT-1  32 %", "mono"), ("RT-2  62 %", "mono")],
            "new words, not new motions", key=True)

for a, b in ((ca, cb), (cb, cc), (cc, cd)):
    f.connect(a, b, color=WIRE, sw=1.4, ta=0.62, tb=0.62)

f.save(str(OUT))
print(OUT)
