"""EP08 figure: where a biped should step (capture point), our G1 push test, and the gait clock.

Images are frames from the episode film (MuJoCo + Blender renders, the charts are drawn from the real data).
Numbers come from the episode's 策划/实验/结果.md (G1 mass 33.3 kg, CoM 0.687 m, 64 pushes, r = 0.82, 7.7 cm,
plain vs clock at 1000 iterations).
"""

from pathlib import Path

from figkit import FAINT, HAIR, INK, MUTED, PAL, WIRE, Fig

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets" / "ep08-biped-rl"
OUT = HERE.parent / "ep08-biped-rl-figure.svg"

f = Fig(1400, 520)
LABEL, MODULE = f.fs("label"), f.fs("module")

TOP_Y, BOT_Y = 8, 512
W_A, W_B, W_C = 440, 396, 524
PA, PB, PC = f.place(8, 1392, (W_A, W_B, W_C), gap=8)


def name(x, y, s, color=INK, box=None, anchor="start", family="sans", italic=False):
    f.text(x, y, s, size=MODULE, weight=500 if family == "sans" else 400, color=color, box=box, anchor=anchor,
           family=family, italic=italic)


def note(x, y, s, box=None, anchor="start", color=MUTED):
    f.text(x, y, s, size=LABEL, color=color, box=box, anchor=anchor, family="serif", italic=True)


# ---------------------------------------------------------------- (a) capture point
top = f.panel(PA, TOP_Y, W_A, BOT_Y - TOP_Y, "orange", "(a) Where to step")
ca = f.card(PA + 10, top + 4, W_A - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
ix, iw = PA + 22, W_A - 44
half = (iw - 10) / 2
f.image(ASSETS / "lipm.jpg", ix, top + 16, half, 200)
f.image(ASSETS / "push.jpg", ix + half + 10, top + 16, half, 200)
name(ix, top + 250, "Capture point", color=PAL["orange"].deep, box=ca)
f.chip(ix, top + 268, iw, 44, "ξ = x + ẋ / ω", "orange", size=MODULE, fill="#FFFFFF", stroke=PAL["orange"].accent,
       color=INK, family="serif", italic=True)
name(ix, top + 350, "Inverted pendulum", box=ca)
f.text(ix + iw, top + 350, "ẍ = ω²(x − p)", size=MODULE, anchor="end", box=ca, family="serif", italic=True)
f.chip(ix, top + 368, half, 40, "$z=0.69$ m", "gray", size=LABEL, fill="#FFFFFF")
f.chip(ix + half + 10, top + 368, half, 40, "$\\omega=3.78$ /s", "gray", size=LABEL, fill="#FFFFFF")

# ---------------------------------------------------------------- (b) our push test
top = f.panel(PB, TOP_Y, W_B, BOT_Y - TOP_Y, "blue", "(b) 64 pushes, our G1")
cb = f.card(PB + 10, top + 4, W_B - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
jx, jw = PB + 22, W_B - 44
f.image(ASSETS / "scatter.jpg", jx, top + 16, jw, 200)
name(jx, top + 250, "Farthest step", box=cb)
note(jx + jw, top + 250, "within 1.5 s", box=cb, anchor="end")
half = (jw - 10) / 2
f.chip(jx, top + 268, half, 44, "$r=0.82$", "blue", size=MODULE, fill="#FFFFFF", stroke=PAL["blue"].accent, color=INK)
f.chip(jx + half + 10, top + 268, half, 44, "7.7 cm", "blue", size=MODULE, fill="#FFFFFF", stroke=PAL["blue"].accent,
       color=INK)
name(jx, top + 350, "vs. ξ at push", box=cb, family="serif", italic=True)
f.chip(jx, top + 372, jw, 40, "PPO, 12 leg joints", "blue", size=LABEL, fill="#FFFFFF", stroke=PAL["blue"].accent,
       color=INK)

# ---------------------------------------------------------------- (c) gait clock
top = f.panel(PC, TOP_Y, W_C, BOT_Y - TOP_Y, "green", "(c) Gait clock")
cc = f.card(PC + 10, top + 4, W_C - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
kx, kw = PC + 22, W_C - 44
f.image(ASSETS / "clock.jpg", kx, top + 16, kw, 200)
name(kx, top + 250, "Clock", color=PAL["green"].deep, box=cc)
f.text(kx + kw, top + 250, "$T=0.8$ s", size=MODULE, anchor="end", box=cc)
# comparison grid: row label, no clock, clock
lw = 118
cw = (kw - lw - 20) / 2
x1, x2 = kx + lw + 10, kx + lw + 20 + cw
note(kx, top + 290, "1000 iterations", box=cc)
f.text(x1 + cw / 2, top + 290, "plain", size=LABEL, color=PAL["red"].deep, anchor="middle", box=cc, weight=500)
f.text(x2 + cw / 2, top + 290, "clock", size=LABEL, color=PAL["green"].deep, anchor="middle", box=cc, weight=500)
rows = (
    ("foot lift", "2.3 cm", "10.4 cm"),
    ("slip", "45 cm/s", "1.2 cm/s"),
    ("L : R steps", "4.5 : 1", "1 : 1"),
)
for k, (lab, a, b) in enumerate(rows):
    y = top + 298 + k * 46
    f.text(kx, y + 26, lab, size=LABEL, color=MUTED, box=cc, family="serif", italic=True)
    f.chip(x1, y, cw, 38, a, "red", size=LABEL, fill="#FFFFFF", stroke=PAL["red"].mid, color=INK)
    f.chip(x2, y, cw, 38, b, "green", size=LABEL, fill="#FFFFFF", stroke=PAL["green"].accent, color=INK)

f.save(str(OUT))
print(OUT)
