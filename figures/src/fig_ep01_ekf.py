"""EP01 figure: one EKF cycle on Apollo 8 (predict, measure, update) and why it is called extended.

Images are frames from the episode film (Blender + Three.js renders); the ellipsoids in them are
schematic (errors enlarged, not real trajectory data), as the film itself states.
"""

from pathlib import Path

from figkit import FAINT, HAIR, INK, MUTED, PAL, WIRE, Fig

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets" / "ep01"
OUT = HERE.parent / "ep01-ekf-figure.svg"

f = Fig(1400, 540)
G, P = PAL["green"], PAL["purple"]
LABEL, MODULE = f.fs("label"), f.fs("module")

TOP_Y, BOT_Y = 8, 532
W_A, W_B, W_C = 292, 736, 340
PA, PB, PC = f.place(8, 1392, (W_A, W_B, W_C), gap=8)


def name(x, y, s, color=INK, box=None, anchor="start"):
    f.text(x, y, s, size=MODULE, weight=500, color=color, box=box, anchor=anchor)


def note(x, y, s, box=None, anchor="start", color=MUTED):
    f.text(x, y, s, size=LABEL, color=color, box=box, anchor=anchor, family="serif", italic=True)


# ---------------------------------------------------------------- (a) state
top = f.panel(PA, TOP_Y, W_A, BOT_Y - TOP_Y, "gray", "(a) Apollo 8 state")
ca = f.card(PA + 10, top + 4, W_A - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
ix, iw = PA + 22, W_A - 44
f.image(ASSETS / "state.jpg", ix, top + 16, iw, 200)
name(ix, top + 250, "State", box=ca)
f.text(ix + iw, top + 250, "$\\hat{x}\\in\\mathbb{R}^6$", size=MODULE, anchor="end", box=ca)
half = (iw - 10) / 2
f.chip(ix, top + 268, half, 40, "$r\\in\\mathbb{R}^3$", "gray", size=LABEL, fill="#FFFFFF")
f.chip(ix + half + 10, top + 268, half, 40, "$v\\in\\mathbb{R}^3$", "gray", size=LABEL, fill="#FFFFFF")
name(ix, top + 350, "Covariance", box=ca)
f.text(ix + iw, top + 350, "$P$", size=MODULE, anchor="end", box=ca)
note(ix, top + 380, "uncertainty ellipsoid", box=ca)

# ---------------------------------------------------------------- (b) one cycle
top = f.panel(PB, TOP_Y, W_B, BOT_Y - TOP_Y, "blue", "(b) One EKF cycle")
xs = f.cols(PB + 10, PB + W_B - 10, 3, gap=30)
card_top, card_h = top + 4, 400
steps = (
    ("Predict", "猜", "predict.jpg", "amber", False),
    ("Measure", "看", "measure.jpg", "blue", False),
    ("Update", "改", "update.jpg", "green", True),
)
cards = []
for (x, w), (en, zh, img, role, key) in zip(xs, steps):
    c = f.card(x, card_top, w, card_h, role, key=key)
    cards.append(c)
    f.image(ASSETS / img, x + 12, card_top + 12, w - 24, 170)
    name(x + 12, card_top + 214, en, color=PAL[role].deep, box=c)
    f.text(x + w - 12, card_top + 214, zh, size=MODULE, weight=500, color=PAL[role].deep, anchor="end", box=c)

(xp, wp), (xm, wm), (xu, wu) = xs
cp, cm, cu = cards
ROW1, ROW2, ROW3 = card_top + 234, card_top + 288, card_top + 340


def eq(x, w, y, s, role):
    f.chip(x + 12, y, w - 24, 42, s, role, size=LABEL, fill="#FFFFFF", stroke=PAL[role].accent, color=INK)


eq(xp, wp, ROW1, "$\\hat{x}^{-}=f(\\hat{x})$", "amber")
eq(xp, wp, ROW2, "$P^{-}=FPF^{\\top}+Q$", "amber")
note(xp + wp / 2, ROW3 + 30, "Earth + Moon gravity", box=cp, anchor="middle")

eq(xm, wm, ROW1, "$z=h(x)+v$", "blue")
eq(xm, wm, ROW2, "$H=\\partial h/\\partial x$", "blue")
note(xm + wm / 2, ROW3 + 30, "sextant: star to horizon", box=cm, anchor="middle")

eq(xu, wu, ROW1, "$K=P^{-}H^{\\top}S^{-1}$", "green")
eq(xu, wu, ROW2, "$\\hat{x}=\\hat{x}^{-}+K\\delta$", "green")
note(xu + wu / 2, ROW3 + 30, "$\\delta=z-h(\\hat{x}^{-})$", box=cu, anchor="middle")

f.connect(cp, cm, color=WIRE, sw=1.4, ta=0.22, tb=0.22)
f.connect(cm, cu, color=WIRE, sw=1.4, ta=0.22, tb=0.22)
lane_y = card_top + card_h + 40
f.route(cu, cp, (lane_y,), sides=("bottom", "bottom"), color=G.accent, sw=2, label="next star, 200+ sightings",
        knockout=True, label_at=PB + W_B / 2)

# ---------------------------------------------------------------- (c) why extended
top = f.panel(PC, TOP_Y, W_C, BOT_Y - TOP_Y, "purple", "(c) Why “extended”")
cc = f.card(PC + 10, top + 4, W_C - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
jx, jw = PC + 22, W_C - 44
f.image(ASSETS / "extended.jpg", jx, top + 16, jw, 200)
half = (jw - 10) / 2
name(jx, top + 250, "Linear vs. gravity", box=cc)
f.chip(jx, top + 268, half, 40, "ellipse", "orange", size=LABEL, fill="#FFFFFF", stroke=PAL["orange"].accent,
       color=INK, family="mono")
f.chip(jx + half + 10, top + 268, half, 40, "banana", "purple", size=LABEL, fill="#FFFFFF", stroke=P.accent,
       color=INK, family="mono")
name(jx, top + 350, "Jacobian", color=P.deep, box=cc)
f.text(jx + jw, top + 350, "$F=\\partial f/\\partial x$", size=MODULE, anchor="end", box=cc)
note(jx, top + 380, "at the current $\\hat{x}$", box=cc)
f.chip(jx, top + 400, jw, 40, "S. F. Schmidt, NASA Ames", "purple", size=LABEL, fill="#FFFFFF", stroke=P.accent,
       color=INK)

f.save(str(OUT))
print(OUT)
