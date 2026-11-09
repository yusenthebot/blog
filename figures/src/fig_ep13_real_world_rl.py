"""EP13 figure: imitation vs practice, the practice curve, and a judge that lies (MuJoCo peg-in-hole, simulated).

Images are frames from the episode film. Numbers come from the episode's 策划/实验/结果.md
(E1 imitation ceiling, E2 practising, E3 takeovers, E4 lying rewards); 3 seeds, simulated time.
"""

from pathlib import Path

from figkit import HAIR, INK, MUTED, PAL, Fig

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets" / "ep13-real-world-rl"
OUT = HERE.parent / "ep13-real-world-rl-figure.svg"

f = Fig(1400, 540)
LABEL, MODULE = f.fs("label"), f.fs("module")
TOP_Y, BOT_Y = 8, 532
W_A, W_B, W_C = 460, 450, 450
PA, PB, PC = f.place(8, 1392, (W_A, W_B, W_C), gap=8)


def name(x, y, s, color=INK, box=None, anchor="start"):
    f.text(x, y, s, size=MODULE, weight=500, color=color, box=box, anchor=anchor)


def note(x, y, s, box=None, anchor="start", color=MUTED):
    f.text(x, y, s, size=LABEL, color=color, box=box, anchor=anchor, family="serif", italic=True)


def bar(x, w, y, s, frac, role, h=40):
    f.chip(x, y, max(w * frac, 90), h, s, role, size=LABEL, fill=PAL[role].tint, stroke=PAL[role].accent)


def panel(px, pw, role, title):
    top = f.panel(px, TOP_Y, pw, BOT_Y - TOP_Y, role, title)
    card = f.card(px + 10, top + 4, pw - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
    return top, card, px + 22, pw - 44


# ------------------------------------------------------------ (a) imitation vs practice
top, ca, ix, iw = panel(PA, W_A, "purple", "(a) Imitate vs. practise")
f.image(ASSETS / "teacher.jpg", ix, top + 16, iw, 150)
LBL = 170
bx, bw = ix + LBL, iw - LBL
for i, (en, res, frac, role) in enumerate((
    ("20 demos", "59 %", 0.59, "purple"),
    ("80 demos", "75 %", 0.75, "purple"),
    ("Practice", "98.5-99.5 %", 1.0, "green"),
)):
    y = top + 180 + i * 48
    name(ix, y + 28, en, box=ca)
    bar(bx, bw, y, res, frac, role)
name(ix, top + 352, "Time per insertion", box=ca)
hw = (iw - 10) / 2
f.chip(ix, top + 366, hw, 40, "Teacher 4.89 s", "purple", size=LABEL, fill="#FFFFFF", stroke=PAL["purple"].accent)
f.chip(ix + hw + 10, top + 366, hw, 40, "Practised 2.2 s", "green", size=LABEL, fill="#FFFFFF",
       stroke=PAL["green"].accent)

# ------------------------------------------------------------ (b) practice curve
top, cb, jx, jw = panel(PB, W_B, "green", "(b) Practice curve")
f.image(ASSETS / "dip.jpg", jx, top + 16, jw, 170)
name(jx, top + 222, "Success over time", box=cb)
for i, (s, role) in enumerate((
    ("0 % for the first ~5 min", "red"),
    ("passes imitation at 17-20 min", "amber"),
    ("$>$98 % by ~33 min", "green"),
)):
    f.chip(jx, top + 236 + i * 44, jw, 38, s, role, size=LABEL, fill=PAL[role].tint, stroke=PAL[role].accent)
name(jx, top + 396, "Teacher takeovers", box=cb)
f.text(jx + jw, top + 396, "$110\\to0$", size=MODULE, anchor="end", box=cb)
note(jx, top + 428, "first vs. last 100 episodes", box=cb)

# ------------------------------------------------------------ (c) wrong judge
top, cc, kx, kw = panel(PC, W_C, "red", "(c) Wrong judge")
f.image(ASSETS / "tower.jpg", kx, top + 16, kw, 160)
name(kx, top + 212, "Last 100 practice runs", box=cc)
LBL = 120
bx, bw = kx + LBL, kw - LBL
for i, (en, res, frac, role) in enumerate((
    ("Judge says", "98 %", 1.0, "blue"),
    ("True", "24 %", 0.24, "red"),
)):
    y = top + 226 + i * 48
    name(kx, y + 28, en, box=cc)
    bar(bx, bw, y, res, frac, role)
name(kx, top + 352, "Judge misses wins", box=cc)
f.chip(kx, top + 366, kw, 40, "true success 29-46 %", "orange", size=LABEL, fill="#FFFFFF",
       stroke=PAL["orange"].accent)

f.save(str(OUT))
print(OUT)
