"""EP04 figure: world model, cascaded WAM (UniPi) and joint WAM (DreamZero).

Images are frames from the episode film (MuJoCo physics + Blender render of an ALOHA stand-in for the
AgiBot G1, and the Three.js concept layer); all of them are schematic, as the film itself labels them.
Numbers are from the episode narration script and 策划/事实核查.md.
"""

from pathlib import Path

from figkit import HAIR, INK, MUTED, PAL, WIRE, Fig

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets" / "ep04"
OUT = HERE.parent / "ep04-world-action-model-figure.svg"

f = Fig(1400, 540)
LABEL, MODULE = f.fs("label"), f.fs("module")

TOP_Y, BOT_Y = 8, 532
W_A, W_B, W_C = 430, 430, 500
PA, PB, PC = f.place(8, 1392, (W_A, W_B, W_C), gap=12)


def name(x, y, s, color=INK, box=None, anchor="start"):
    f.text(x, y, s, size=MODULE, weight=500, color=color, box=box, anchor=anchor)


def note(x, y, s, box=None, anchor="start", color=MUTED):
    f.text(x, y, s, size=LABEL, color=color, box=box, anchor=anchor, family="serif", italic=True)


def column(px, pw, role, title, img, img_h=190):
    top = f.panel(px, TOP_Y, pw, BOT_Y - TOP_Y, role, title)
    card = f.card(px + 10, top + 4, pw - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
    ix, iw = px + 22, pw - 44
    f.image(ASSETS / img, ix, top + 16, iw, img_h)
    return top, card, ix, iw


# ---------------------------------------------------------------- (a) world model
top, ca, ix, iw = column(PA, W_A, "gray", "(a) World model", "futures.jpg")
name(ix, top + 232, "Transition", box=ca)
f.text(ix + iw, top + 232, "$s_{t+1}=f(s_t,a_t)$", size=MODULE, anchor="end", box=ca)
third = (iw - 20) / 3
for i, s in enumerate(("place", "+3 cm", "miss")):
    f.chip(ix + i * (third + 10), top + 248, third, 40, s, "gray", size=LABEL, fill="#FFFFFF", family="mono")
name(ix, top + 346, "Lineage", box=ca)
f.chip(ix, top + 362, iw, 34, "World Models 2018", "gray", size=LABEL, fill="#FFFFFF")
half = (iw - 10) / 2
f.chip(ix, top + 404, half, 34, "DreamerV3", "gray", size=LABEL, fill="#FFFFFF")
f.chip(ix + half + 10, top + 404, half, 34, "Genie 3 (video)", "gray", size=LABEL, fill="#FFFFFF")

# ---------------------------------------------------------------- (b) cascaded
top, cb, ix, iw = column(PB, W_B, "blue", "(b) Cascaded WAM", "unipi.jpg")
name(ix, top + 232, "UniPi", color=PAL["blue"].deep, box=cb)
f.text(ix + iw, top + 232, "2023", size=MODULE, anchor="end", box=cb)
f.chip(ix, top + 248, iw, 40, "text $\\to$ video $o_{t:t+H}$", "blue", size=LABEL, fill="#FFFFFF",
       stroke=PAL["blue"].accent, color=INK)
name(ix, top + 346, "Inverse dynamics", color=PAL["blue"].deep, box=cb)
f.chip(ix, top + 364, iw, 40, "$a_t=g(o_t,o_{t+1})$", "blue", size=LABEL, fill="#FFFFFF",
       stroke=PAL["blue"].accent, color=INK)
note(ix, top + 314, "video first, actions second", box=cb)

# ---------------------------------------------------------------- (c) joint
top, cc, ix, iw = column(PC, W_C, "green", "(c) Joint WAM: DreamZero", "joint.jpg")
G = PAL["green"]
name(ix, top + 232, "Flow matching", color=G.deep, box=cc)
f.text(ix + iw, top + 232, "$x_\\tau=\\tau x_1+(1-\\tau)x_0$", size=MODULE, anchor="end", box=cc)
half = (iw - 10) / 2
f.chip(ix, top + 248, half, 40, "Wan2.1 14B", "green", size=LABEL, fill="#FFFFFF", stroke=G.accent, color=INK)
f.chip(ix + half + 10, top + 248, half, 40, "150 ms, 7 Hz", "green", size=LABEL, fill="#FFFFFF", stroke=G.accent,
       color=INK)
note(ix, top + 310, "from 5.7 s, 38x", box=cc)
name(ix, top + 346, "Unseen tasks", color=G.deep, box=cc)
f.chip(ix, top + 362, half, 34, "DreamZero 39.5 %", "green", size=LABEL, fill="#FFFFFF", stroke=INK, color=INK, weight=500)
f.chip(ix + half + 10, top + 362, half, 34, "best VLA 16.3 %", "gray", size=LABEL, fill="#FFFFFF")
f.chip(ix, top + 404, iw, 34, "+12 min human video: 38.3 $\\to$ 54.3 %", "green", size=LABEL, fill="#FFFFFF",
       stroke=G.accent, color=INK)

f.save(str(OUT))
print(OUT)
