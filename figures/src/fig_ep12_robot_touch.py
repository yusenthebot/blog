"""EP12 figure: force control, tactile sensing, and our 60-egg experiment (MuJoCo, simulated).

Images are frames from the episode film (Blender renders); numbers from the episode's
策划/实验/结果.md (E1 60 eggs, E2 reflex delay, E3 wiping with the table 4 mm higher).
"""

from pathlib import Path

from figkit import HAIR, INK, MUTED, PAL, WIRE, Fig

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets" / "ep12-robot-touch"
OUT = HERE.parent / "ep12-robot-touch-figure.svg"

f = Fig(1400, 540)
LABEL, MODULE = f.fs("label"), f.fs("module")
TOP_Y, BOT_Y = 8, 532
W_A, W_B, W_C = 440, 440, 480
PA, PB, PC = f.place(8, 1392, (W_A, W_B, W_C), gap=8)


def name(x, y, s, color=INK, box=None, anchor="start"):
    f.text(x, y, s, size=MODULE, weight=500, color=color, box=box, anchor=anchor)


def note(x, y, s, box=None, anchor="start", color=MUTED):
    f.text(x, y, s, size=LABEL, color=color, box=box, anchor=anchor, family="serif", italic=True)


# ------------------------------------------------------------ (a) force
top = f.panel(PA, TOP_Y, W_A, BOT_Y - TOP_Y, "purple", "(a) Force")
ca = f.card(PA + 10, top + 4, W_A - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
ix, iw = PA + 22, W_A - 44
half = (iw - 10) / 2
f.image(ASSETS / "wipe.jpg", ix, top + 16, iw, 164)
name(ix, top + 214, "Position", color=PAL["red"].deep, box=ca)
name(ix + half + 10, top + 214, "Impedance", color=PAL["green"].deep, box=ca)
f.chip(ix, top + 228, half, 40, "227 N", "red", size=MODULE, fill="#FFFFFF", stroke=PAL["red"].accent)
f.chip(ix + half + 10, top + 228, half, 40, "12 N", "green", size=MODULE, fill="#FFFFFF", stroke=PAL["green"].accent)
note(ix, top + 298, "mean wiping force, table +4 mm", box=ca)
name(ix, top + 342, "Spring arm", box=ca)
f.chip(ix, top + 356, iw, 44, "$F=K(x_d-x)+D(v_d-v)$", "purple", size=LABEL, fill="#FFFFFF",
       stroke=PAL["purple"].accent, color=INK)
note(ix, top + 428, "$K$ stiffness, $D$ damping", box=ca)

# ------------------------------------------------------------ (b) touch
top = f.panel(PB, TOP_Y, W_B, BOT_Y - TOP_Y, "blue", "(b) Touch")
cb = f.card(PB + 10, top + 4, W_B - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
jx, jw = PB + 22, W_B - 44
f.image(ASSETS / "gel.jpg", jx, top + 16, jw, 224)
name(jx, top + 270, "Gel + camera", color=PAL["blue"].deep, box=cb)
f.text(jx + jw, top + 270, "DIGIT", size=LABEL, anchor="end", box=cb, family="mono")
f.image(ASSETS / "taxel.jpg", jx, top + 284, jw, 84, fit="cover")
name(jx, top + 404, "Taxel map", box=cb)
f.text(jx + jw, top + 404, "$16\\times16$", size=MODULE, anchor="end", box=cb)
f.chip(jx, top + 416, jw, 40, "slip $>10$ mm/s: add force", "blue", size=LABEL, fill="#FFFFFF",
       stroke=PAL["blue"].accent)

# ------------------------------------------------------------ (c) 60 eggs
top = f.panel(PC, TOP_Y, W_C, BOT_Y - TOP_Y, "green", "(c) 60 eggs, simulated")
cc = f.card(PC + 10, top + 4, W_C - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
kx, kw = PC + 22, W_C - 44
f.image(ASSETS / "egg.jpg", kx, top + 16, kw, 150)
rows = (
    ("Position only", "51 broke", 51, "red"),
    ("Fixed 2 N", "37 dropped", 37, "orange"),
    ("Tactile reflex", "60 held", 60, "green"),
)
BAR_X = kx + 150
BAR_W = kw - 150
for i, (en, res, n, role) in enumerate(rows):
    y = top + 180 + i * 48
    name(kx, y + 28, en, box=cc)
    f.chip(BAR_X, y, BAR_W * n / 60, 40, res, role, size=LABEL, fill=PAL[role].tint, stroke=PAL[role].accent)
name(kx, top + 356, "Reflex delay", box=cc)
note(kx + kw, top + 356, "of 60 eggs, dropped", box=cc, anchor="end")
hw = (kw - 10) / 2
f.chip(kx, top + 370, hw, 40, "$\\le$35 ms: 0", "green", size=LABEL, fill="#FFFFFF", stroke=PAL["green"].accent)
f.chip(kx + hw + 10, top + 370, hw, 40, "70 ms: 20", "orange", size=LABEL, fill="#FFFFFF", stroke=PAL["orange"].accent)
note(kx, top + 440, "broken = over 10 N (our setting)", box=cc)

f.save(str(OUT))
print(OUT)
