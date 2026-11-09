"""EP05 figure: in-context linear regression, the rewired UR5e student, and the result.

Images are frames from the episode film (Three.js concept layer and MuJoCo + Blender renders).
All numbers are from 策划/实验/结果.md (our own experiments; simulation, 1000 prompts / 200 random bodies).
"""

from pathlib import Path

from figkit import HAIR, INK, MUTED, PAL, Fig

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets" / "ep05"
OUT = HERE.parent / "ep05-in-context-learning-figure.svg"

f = Fig(1400, 540)
LABEL, MODULE = f.fs("label"), f.fs("module")

TOP_Y, BOT_Y = 8, 532
W_A, W_B, W_C = 448, 448, 464
PA, PB, PC = f.place(8, 1392, (W_A, W_B, W_C), gap=12)


def name(x, y, s, color=INK, box=None, anchor="start"):
    f.text(x, y, s, size=MODULE, weight=500, color=color, box=box, anchor=anchor)


def column(px, pw, role, title, img, img_h=222):
    top = f.panel(px, TOP_Y, pw, BOT_Y - TOP_Y, role, title)
    card = f.card(px + 10, top + 4, pw - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
    ix, iw = px + 22, pw - 44
    f.image(ASSETS / img, ix, top + 16, iw, img_h)
    return top, card, ix, iw


def row(ix, iw, y, labels, role, key=None, family="sans", h=40):
    n = len(labels)
    w = (iw - 10 * (n - 1)) / n
    for i, s in enumerate(labels):
        k = key == i
        f.chip(ix + i * (w + 10), y, w, h, s, role, size=LABEL, fill="#FFFFFF",
               stroke=INK if k else PAL[role].accent, color=INK, family=family, weight=500 if k else 400)


# ---------------------------------------------------------------- (a) in-context regression
G = PAL["gray"]
top, ca, ix, iw = column(PA, W_A, "purple", "(a) In-context regression", "curve.jpg")
P = PAL["purple"]
name(ix, top + 264, "Error vs. examples", color=P.deep, box=ca)
f.text(ix + iw, top + 264, "$y=w^{\\top}x$", size=MODULE, anchor="end", box=ca)
row(ix, iw, top + 280, ("2: 0.60", "5: 0.04", "19: 0.0016"), "purple", key=2, family="mono")
name(ix, top + 378, "Controls", color=P.deep, box=ca)
row(ix, iw, top + 394, ("shuffled $y$: 1.26", "2.5x scale: 0.045"), "gray", h=40)

# ---------------------------------------------------------------- (b) rewired UR5e
B = PAL["blue"]
top, cb, ix, iw = column(PB, W_B, "blue", "(b) Rewired UR5e", "robots.jpg")
name(ix, top + 264, "Student", color=B.deep, box=cb)
f.text(ix + iw, top + 264, "last 1.2 s", size=MODULE, anchor="end", box=cb)
row(ix, iw, top + 280, ("teacher: knows wiring", "student: history"), "blue")
name(ix, top + 378, "Test", color=B.deep, box=cb)
row(ix, iw, top + 394, ("200 random bodies", "35 % rewired"), "blue")

# ---------------------------------------------------------------- (c) result
Gr = PAL["green"]
top, cc, ix, iw = column(PC, W_C, "green", "(c) Result", "bars.jpg")
name(ix, top + 264, "Within 2 cm", color=Gr.deep, box=cc)
row(ix, iw, top + 280, ("history 60.5 %", "none 0.5 %"), "green", key=0)
name(ix, top + 378, "Probe", color=Gr.deep, box=cc)
f.text(ix + iw, top + 378, "$R^2$ 0.56 to 0.68", size=MODULE, anchor="end", box=cc)
row(ix, iw, top + 394, ("flips in 0.1 s",), "green")

f.save(str(OUT))
print(OUT)
