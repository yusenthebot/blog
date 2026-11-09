"""EP06 figure: behavior cloning drifts off the lane, three fixes, and two answers around an obstacle.

Numbers are from the episode's own experiment (策划/实验/结果.md, 3 seeds unless noted).
Images are frames from the episode film (MuJoCo physics, Blender render, Three.js concept layer).
"""

from pathlib import Path

from figkit import HAIR, INK, MUTED, PAL, Fig

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets" / "ep06-imitation-learning"
OUT = HERE.parent / "ep06-imitation-learning-figure.svg"

f = Fig(1400, 540)
LABEL, MODULE, MIN = f.fs("label"), f.fs("module"), f.fs("min")
TOP_Y, BOT_Y = 8, 532
W_A, W_B, W_C = 420, 520, 428
PA, PB, PC = f.place(8, 1392, (W_A, W_B, W_C), gap=8)


def name(x, y, s, color=INK, box=None, anchor="start"):
    f.text(x, y, s, size=MODULE, weight=500, color=color, box=box, anchor=anchor)


def note(x, y, s, box=None, anchor="start", color=MUTED):
    f.text(x, y, s, size=LABEL, color=color, box=box, anchor=anchor, family="serif", italic=True)


def vbar(cx, base, h, w, role, value, label, box):
    p = PAL[role]
    f.add(f'<rect x="{cx - w / 2:.1f}" y="{base - h:.1f}" width="{w}" height="{h:.1f}" fill="{p.mid}" '
          f'stroke="{p.accent}" stroke-width="1"/>')
    f.text(cx, base - h - 7, value, size=MIN, weight=700, color=p.deep, anchor="middle", box=box)
    f.text(cx, base + 22, label, size=MIN, color=MUTED, anchor="middle", box=box)


def hbar(x, y, w, h, role, value, label, label_w, box):
    p = PAL[role]
    f.text(x, y + h / 2 + LABEL * 0.36, label, size=LABEL, color=INK, box=box)
    bx = x + label_w
    f.add(f'<rect x="{bx}" y="{y}" width="{max(w, 2):.1f}" height="{h}" fill="{p.mid}" stroke="{p.accent}" stroke-width="1"/>')
    f.text(bx + max(w, 2) + 8, y + h / 2 + LABEL * 0.36, value, size=LABEL, weight=700, color=p.deep, box=box)


# ---------------------------------------------------------------- (a) lane
top = f.panel(PA, TOP_Y, W_A, BOT_Y - TOP_Y, "gray", "(a) Same lane, same pushes")
ca = f.card(PA + 10, top + 4, W_A - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
ix, iw = PA + 22, W_A - 44
half = (iw - 10) / 2
iy = top + 16
f.image(ASSETS / "bc.jpg", ix, iy, half, 160)
f.image(ASSETS / "dagger.jpg", ix + half + 10, iy, half, 160)
name(ix, iy + 192, "BC", color=PAL["orange"].deep, box=ca)
name(ix + half + 10, iy + 192, "DAgger", color=PAL["green"].deep, box=ca)
f.chip(ix, iy + 206, half, 40, "35.8 %", "orange", size=LABEL, fill="#FFFFFF", stroke=PAL["orange"].accent, color=INK)
f.chip(ix + half + 10, iy + 206, half, 40, "100 %", "green", size=LABEL, fill="#FFFFFF", stroke=PAL["green"].accent, color=INK)
f.line(f"M{ix} {iy + 270}H{ix + iw}", HAIR, 1)
name(ix, iy + 302, "Offset by step", box=ca)
base = iy + 410
vb = [(0.075, "orange", "0.075", "BC, step 25"), (0.169, "orange", "0.169", "BC, step 50"), (0.007, "gray", "0.007", "expert")]
slot = iw / 3
for i, (v, role, txt, lab) in enumerate(vb):
    vbar(ix + slot * (i + 0.5), base, v / 0.17 * 80, 40, role, txt, lab.split(", ")[-1].replace("step ", ""), ca)
f.line(f"M{ix} {base}H{ix + iw}", "#B9B4A8", 1)

# ---------------------------------------------------------------- (b) three fixes
top = f.panel(PB, TOP_Y, W_B, BOT_Y - TOP_Y, "blue", "(b) Three fixes", sub="success, in lane")
xs = f.cols(PB + 10, PB + W_B - 10, 3, gap=10)
y0, ch = top + 4, BOT_Y - 10 - top - 4
base = y0 + 330
fixes = (
    ("DAgger", "+1 round", "green", [("35.8", 35.8, "0"), ("100", 100, "1")], "100 %", "2011"),
    ("DART", "noise", "amber", [("35.8", 35.8, "0"), ("80.5", 80.5, ".002"), ("99.7", 99.7, ".005")], "99.7 %", "2017"),
    ("Chunking", "$k$ steps", "purple", [("78.3", 78.3, "4"), ("98.0", 98.0, "16"), ("78.5", 78.5, "64")], "98.0 %", "2023"),
)
for (x, w), (nm, sub, role, bars, best, cite) in zip(xs, fixes):
    c = f.card(x, y0, w, ch, role)
    name(x + 12, y0 + 36, nm, color=PAL[role].deep, box=c)
    note(x + 12, y0 + 66, sub, box=c)
    n = len(bars)
    slot = (w - 24) / n
    for i, (txt, v, lab) in enumerate(bars):
        vbar(x + 12 + slot * (i + 0.5), base, v / 100 * 190, min(36, slot - 8), role, txt, lab, c)
    f.line(f"M{x + 12} {base}H{x + w - 12}", "#B9B4A8", 1)
    f.chip(x + 12, y0 + 366, w - 24, 40, best, role, size=LABEL, fill="#FFFFFF", stroke=PAL[role].accent, color=INK)
    f.text(x + w / 2, y0 + 436, cite, size=LABEL, color=MUTED, anchor="middle", box=c, family="mono")

# ---------------------------------------------------------------- (c) two answers
top = f.panel(PC, TOP_Y, W_C, BOT_Y - TOP_Y, "purple", "(c) Two valid answers")
cc = f.card(PC + 10, top + 4, W_C - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
jx, jw = PC + 22, W_C - 44
half = (jw - 10) / 2
iy = top + 16
f.image(ASSETS / "obstacle.jpg", jx, iy, half, 160)
f.image(ASSETS / "diffusion.jpg", jx + half + 10, iy, half, 160)
name(jx, iy + 192, "BC (MSE)", color=PAL["red"].deep, box=cc)
name(jx + half + 10, iy + 192, "Diffusion", color=PAL["purple"].deep, box=cc)
f.chip(jx, iy + 206, half, 40, "200/200 hit", "red", size=LABEL, fill="#FFFFFF", stroke=PAL["red"].accent, color=INK)
f.chip(jx + half + 10, iy + 206, half, 40, "98 % pass", "purple", size=LABEL, fill="#FFFFFF", stroke=PAL["purple"].accent, color=INK)
f.line(f"M{jx} {iy + 270}H{jx + jw}", HAIR, 1)
name(jx, iy + 302, "Real Push-T", box=cc)
note(jx + jw, iy + 302, "Chi 2023", box=cc, anchor="end")
rows = (("Diffusion", 95, "purple", "95 %"), ("LSTM-GMM", 20, "gray", "20 %"), ("IBC", 0, "gray", "0 %"))
for i, (lab, v, role, txt) in enumerate(rows):
    hbar(jx, iy + 326 + i * 38, v / 100 * 150, 26, role, txt, lab, 110, cc)

f.save(str(OUT))
print(OUT)
