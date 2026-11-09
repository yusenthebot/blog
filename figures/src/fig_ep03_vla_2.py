"""EP03 figure: from one action at a time to a 50-step chunk drawn by flow matching (VLA, part 2).

Crops are frames from the episode film. The error fan is 40 seeded rollouts computed for the film;
the two-tower scene is marked schematic in the film; numbers come from the narration script and
the pi0 / ALOHA entries of the fact-check notes (B_PI与2025-2026.md, A_2022-2024_奠基.md).
"""

from pathlib import Path

from figkit import MUTED, HAIR, INK, PAL, WIRE, Fig

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets" / "ep03-vla-2"
OUT = HERE.parent / "ep03-vla-2-vla-figure.svg"

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


ca = column(0, "(a) One at a time", "red", "error.jpg", "RT-2", "1\u20133 Hz",
            [("40 rollouts", "mono"), ("$\\times3.6$ band", "sans")],
            "step 30 vs 5", fit="contain")
cb = column(1, "(b) Action chunk", "amber", "chunk.jpg", "ALOHA", "$H=100$",
            [("100 steps", "sans"), ("battery up to 96 %", "sans")],
            "100\u00d7 fewer")
cc = column(2, "(c) Two experts", "blue", "experts.jpg", "$\\pi_0$", "3B + 300M",
            [("VLM 3B", "mono"), ("action expert 300M", "mono")],
            "one-way attention", fit="contain")
cd = column(3, "(d) Flow matching", "green", "flow.jpg", "Noise to chunk", "$H=50$",
            [("$A^{\\tau}=\\tau A+(1-\\tau)\\epsilon$", "sans"), ("10 steps, 50 Hz", "sans")],
            "schematic path", key=True, fit="contain")

for a, b in ((ca, cb), (cb, cc), (cc, cd)):
    f.connect(a, b, color=WIRE, sw=1.4, ta=0.62, tb=0.62)

f.save(str(OUT))
print(OUT)
