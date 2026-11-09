"""EP10 figure: the three-layer stack (S2 / S1 / S0) we ran on one Mac, and the two experiments on it.

Images are frames from the episode film (MuJoCo physics, Blender render). Numbers come from
策划/实验/结果.md and the narration script: S2 1.5 to 2 s per answer, S1 about 20 ms and checks 10 times
a second, S0 50 Hz with PD at 200 Hz, 700 N push 1 of 27 fell and 900 N 10 of 27.
"""

from pathlib import Path

from figkit import HAIR, INK, MUTED, PAL, WIRE, Fig

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets" / "ep10-fast-slow-brain"
OUT = HERE.parent / "ep10-fast-slow-brain-stack-figure.svg"

f = Fig(1400, 540)
LABEL, MODULE = f.fs("label"), f.fs("module")

TOP_Y, BOT_Y = 8, 532
W_A, W_B = 836, 540
PA, PB = f.place(8, 1392, (W_A, W_B), gap=8)


def note(x, y, s, box=None, anchor="start", color=MUTED):
    f.text(x, y, s, size=LABEL, color=color, box=box, anchor=anchor, family="serif", italic=True)


# ---------------------------------------------------------------- (a) three layers
top = f.panel(PA, TOP_Y, W_A, BOT_Y - TOP_Y, "blue", "(a) Three layers")
xs = f.cols(PA + 10, PA + W_A - 10, 3, gap=28)
card_top, card_h = top + 4, BOT_Y - 10 - top - 4
layers = (
    ("System 2", "Qwen3.8 27B", "s2.jpg", "amber", False,
     ("image + text", "JSON steps", "1.5 to 2 s")),
    ("System 1", "SONIC planner", "s1.jpg", "blue", False,
     ("10 Hz", "~20 ms", "pose, 1 to 2 s")),
    ("System 0", "SONIC tracker", "s0.jpg", "orange", True,
     ("64 numbers", "29 joints, 50 Hz", "PD 200 Hz")),
)
cards = []
for (x, w), (name, model, img, role, key, chips) in zip(xs, layers):
    c = f.card(x, card_top, w, card_h, role, key=key)
    cards.append(c)
    f.image(ASSETS / img, x + 12, card_top + 12, w - 24, 190)
    f.text(x + 12, card_top + 242, name, size=MODULE, weight=500, color=PAL[role].deep, box=c)
    f.text(x + w - 12, card_top + 242, model, size=LABEL, color=MUTED, anchor="end", box=c, family="serif", italic=True)
    for k, s in enumerate(chips):
        f.chip(x + 12, card_top + 262 + k * 58, w - 24, 46, s, role, size=LABEL, fill="#FFFFFF",
               stroke=PAL[role].accent, color=INK)

f.connect(cards[0], cards[1], color=WIRE, sw=1.4, ta=0.22, tb=0.22)
f.connect(cards[1], cards[2], color=WIRE, sw=1.4, ta=0.22, tb=0.22)

# ---------------------------------------------------------------- (b) experiments
top = f.panel(PB, TOP_Y, W_B, BOT_Y - TOP_Y, "red", "(b) Push and refresh")
row1_top = top + 4
row1_h = 214
row2_top = row1_top + row1_h + 8
row2_h = BOT_Y - 10 - row2_top
c1 = f.card(PB + 10, row1_top, W_B - 20, row1_h, fill="#FFFFFF", stroke=HAIR)
f.image(ASSETS / "push.jpg", PB + 22, row1_top + 12, 250, row1_h - 24)
rx, rw = PB + 284, PB + W_B - 22 - (PB + 284)
f.text(rx, row1_top + 30, "Push", size=MODULE, weight=500, color=PAL["red"].deep, box=c1)
for k, s in enumerate(("700 N, 0.1 s", "torque +5 ms", "700 N: 1/27 fell", "900 N: 10/27 fell")):
    role = "red" if k == 3 else "gray"
    f.chip(rx, row1_top + 44 + k * 42, rw, 36, s, role, size=LABEL, fill="#FFFFFF",
           stroke=PAL[role].accent, color=INK)

c2 = f.card(PB + 10, row2_top, W_B - 20, row2_h, fill="#FFFFFF", stroke=HAIR)
f.image(ASSETS / "hz.jpg", PB + 22, row2_top + 10, W_B - 44, 140)
f.text(PB + 22, row2_top + 172, "Refresh", size=MODULE, weight=500, color=PAL["red"].deep, box=c2)
cx = f.cols(PB + 22, PB + W_B - 22, 3, gap=8)
for (x, w), s, role in zip(cx, ("2 s: falls 1.7 s", "10 Hz: falls", "17 Hz+: walks"),
                           ("red", "red", "green")):
    f.chip(x, row2_top + 182, w, 36, s, role, size=LABEL, fill="#FFFFFF", stroke=PAL[role].accent, color=INK)

f.save(str(OUT))
print(OUT)
