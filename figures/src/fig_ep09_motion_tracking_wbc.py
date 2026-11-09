"""EP09 figure: motion tracking for whole-body control, two ways to scale it, and our one-arm comparison.

Images are frames from the episode film (Blender renders and charts drawn from real data).
Numbers: SONIC on the Mac and the open-loop baseline from 策划/实验/sonic_port_notes.md and 发布文案.md;
SONIC / SuperMimic scale from the narration script (author-reported for SuperMimic);
arm experiment from 策划/实验/supermini/结果.md (all seeds).
"""

from pathlib import Path

from figkit import HAIR, INK, MUTED, PAL, Fig

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets" / "ep09-motion-tracking-wbc"
OUT = HERE.parent / "ep09-motion-tracking-wbc-figure.svg"

f = Fig(1400, 520)
LABEL, MODULE = f.fs("label"), f.fs("module")

TOP_Y, BOT_Y = 8, 512
W_A, W_B, W_C = 360, 548, 460
PA, PB, PC = f.place(8, 1392, (W_A, W_B, W_C), gap=8)


def name(x, y, s, color=INK, box=None, anchor="start"):
    f.text(x, y, s, size=MODULE, weight=500, color=color, box=box, anchor=anchor)


def note(x, y, s, box=None, anchor="start", color=MUTED):
    f.text(x, y, s, size=LABEL, color=color, box=box, anchor=anchor, family="serif", italic=True)


def chip(x, y, w, h, s, role, size=None):
    f.chip(x, y, w, h, s, role, size=size or LABEL, fill="#FFFFFF", stroke=PAL[role].accent, color=INK)


# ---------------------------------------------------------------- (a) why tracking
top = f.panel(PA, TOP_Y, W_A, BOT_Y - TOP_Y, "red", "(a) Angles are not enough")
ca = f.card(PA + 10, top + 4, W_A - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
ix, iw = PA + 22, W_A - 44
f.image(ASSETS / "fall.jpg", ix, top + 16, iw, 200)
name(ix, top + 250, "Open loop", color=PAL["red"].deep, box=ca)
chip(ix, top + 266, iw, 40, "falls at 1.1 s", "red")
name(ix, top + 340, "SONIC on a Mac", color=PAL["blue"].deep, box=ca)
half = (iw - 10) / 2
chip(ix, top + 356, half, 40, "27.5 s", "blue")
chip(ix + half + 10, top + 356, half, 40, "0.087 rad", "blue")

# ---------------------------------------------------------------- (b) two ways to scale
top = f.panel(PB, TOP_Y, W_B, BOT_Y - TOP_Y, "purple", "(b) Motion tracking, two ways")
cw = (W_B - 20 - 12) / 2
cx1, cx2 = PB + 10, PB + 10 + cw + 12
card_top, card_h = top + 4, BOT_Y - 10 - top - 4
c1 = f.card(cx1, card_top, cw, card_h, "blue", key=False)
c2 = f.card(cx2, card_top, cw, card_h, "purple", key=True)
for cx, c, img, title, tag, role in (
    (cx1, c1, "track.jpg", "SONIC", "scale", "blue"),
    (cx2, c2, "grad.jpg", "SuperMimic", "gradient", "purple"),
):
    f.image(ASSETS / img, cx + 12, card_top + 12, cw - 24, 170)
    name(cx + 12, card_top + 214, title, color=PAL[role].deep, box=c)
    f.text(cx + cw - 12, card_top + 214, tag, size=LABEL, color=MUTED, anchor="end", box=c, family="serif", italic=True)
chip_w = cw - 24
chip(cx1 + 12, card_top + 234, chip_w, 40, "611 h mocap", "blue")
chip(cx1 + 12, card_top + 286, chip_w, 40, "128 GPU × 7 d", "blue")
chip(cx1 + 12, card_top + 338, chip_w, 40, "64-d token", "blue")
chip(cx2 + 12, card_top + 234, chip_w, 40, "world model", "purple")
chip(cx2 + 12, card_top + 286, chip_w, 40, "32-step rollout", "purple")
chip(cx2 + 12, card_top + 338, chip_w, 40, "1 H100 × 3 h", "purple")
note(cx2 + cw / 2, card_top + 408, "author-reported", box=c2, anchor="middle")
note(cx1 + cw / 2, card_top + 408, "real robot 123 / 124", box=c1, anchor="middle")

# ---------------------------------------------------------------- (c) our arm experiment
top = f.panel(PC, TOP_Y, W_C, BOT_Y - TOP_Y, "green", "(c) Our one-arm test")
cc = f.card(PC + 10, top + 4, W_C - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
kx, kw = PC + 22, W_C - 44
f.image(ASSETS / "arms.jpg", kx, top + 16, kw, 200)
name(kx, top + 250, "To 0.05 rad", box=cc)
note(kx + kw, top + 250, "unseen dance", box=cc, anchor="end")
lw = 96
cwd = (kw - lw - 20) / 2
x1, x2 = kx + lw + 10, kx + lw + 20 + cwd
f.text(x1 + cwd / 2, top + 290, "PPO", size=LABEL, color=MUTED, anchor="middle", box=cc, weight=500)
f.text(x2 + cwd / 2, top + 290, "World model", size=LABEL, color=PAL["purple"].deep, anchor="middle", box=cc, weight=500)
rows = (
    ("steps", "0.45-1.28 M", "29-41 k"),
    ("wall clock", "1-2 min", "5-6.6 min"),
)
for k, (lab, a, b) in enumerate(rows):
    y = top + 302 + k * 48
    f.text(kx, y + 26, lab, size=LABEL, color=MUTED, box=cc, family="serif", italic=True)
    f.chip(x1, y, cwd, 38, a, "gray", size=LABEL, fill="#FFFFFF", stroke=PAL["gray"].mid, color=INK)
    f.chip(x2, y, cwd, 38, b, "purple", size=LABEL, fill="#FFFFFF", stroke=PAL["purple"].accent, color=INK)

f.save(str(OUT))
print(OUT)
