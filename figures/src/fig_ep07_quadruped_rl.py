"""EP07 figure: PPO on Go2, domain randomization, and a reward that was written wrong.

Numbers are from the episode's own experiment (策划/实验/结果.md; Apple M5 Max CPU, MuJoCo, 3 seeds at epoch 200
for the randomization test). "Sim-real" robots are simulated robots with parameters unseen in training.
Images are frames from the episode film (MuJoCo physics, Blender render).
"""

from pathlib import Path

from figkit import HAIR, INK, MUTED, PAL, Fig

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets" / "ep07-quadruped-rl"
OUT = HERE.parent / "ep07-quadruped-rl-figure.svg"

f = Fig(1400, 540)
LABEL, MODULE, MIN = f.fs("label"), f.fs("module"), f.fs("min")
TOP_Y, BOT_Y = 8, 532
W_A, W_B, W_C = 440, 500, 428
PA, PB, PC = f.place(8, 1392, (W_A, W_B, W_C), gap=8)


def name(x, y, s, color=INK, box=None, anchor="start"):
    f.text(x, y, s, size=MODULE, weight=500, color=color, box=box, anchor=anchor)


def note(x, y, s, box=None, anchor="start", color=MUTED):
    f.text(x, y, s, size=LABEL, color=color, box=box, anchor=anchor, family="serif", italic=True)


def vbar(cx, base, h, w, role, value, box):
    p = PAL[role]
    f.add(f'<rect x="{cx - w / 2:.1f}" y="{base - max(h, 1.5):.1f}" width="{w}" height="{max(h, 1.5):.1f}" fill="{p.mid}" '
          f'stroke="{p.accent}" stroke-width="1"/>')
    f.text(cx, base - max(h, 1.5) - 7, value, size=MIN, weight=700, color=p.deep, anchor="middle", box=box)


def hbar(x, y, w, h, role, value, label, label_w, box):
    p = PAL[role]
    f.text(x, y + h / 2 + LABEL * 0.36, label, size=LABEL, color=INK, box=box)
    bx = x + label_w
    f.add(f'<rect x="{bx}" y="{y}" width="{max(w, 2):.1f}" height="{h}" fill="{p.mid}" stroke="{p.accent}" stroke-width="1"/>')
    f.text(bx + max(w, 2) + 8, y + h / 2 + LABEL * 0.36, value, size=LABEL, weight=700, color=p.deep, box=box)


# ---------------------------------------------------------------- (a) PPO
top = f.panel(PA, TOP_Y, W_A, BOT_Y - TOP_Y, "blue", "(a) PPO on Go2")
ca = f.card(PA + 10, top + 4, W_A - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
ix, iw = PA + 22, W_A - 44
f.image(ASSETS / "reward.jpg", ix, top + 16, iw, 170)
rows = (
    ("Reward", "$r_t$", "8 terms"),
    ("Advantage", "$A_t=\\hat{R}_t-V(s_t)$", "vs. critic"),
    ("PPO clip", "$\\epsilon=0.2$", "per update"),
)
for i, (nm, sym, sub) in enumerate(rows):
    y = top + 224 + i * 62
    name(ix, y, nm, box=ca)
    f.text(ix + iw, y, sym, size=MODULE, anchor="end", box=ca)
    note(ix, y + 28, sub, box=ca)
f.chip(ix, top + 410, iw, 40, "4096 × 24 = 98,304", "blue", size=LABEL, fill="#FFFFFF", stroke=PAL["blue"].accent, color=INK)

# ---------------------------------------------------------------- (b) randomization
top = f.panel(PB, TOP_Y, W_B, BOT_Y - TOP_Y, "green", "(b) Domain randomization")
cb = f.card(PB + 10, top + 4, W_B - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
jx, jw = PB + 22, W_B - 44
f.image(ASSETS / "fleet.jpg", jx, top + 16, jw, 150)
name(jx, top + 207, "Push test", box=cb)
cw = 98
f.chip(jx + jw - 2 * cw - 10, top + 178, cw, 36, "1 world", "red", size=LABEL, fill="#FFFFFF", stroke=PAL["red"].accent, color=INK)
f.chip(jx + jw - cw, top + 178, cw, 36, "DR", "green", size=LABEL, fill="#FFFFFF", stroke=PAL["green"].accent, color=INK)
base = top + 410
slot = jw / 2
groups = (("own world", 82.4, 0.0), ("256 robots", 38.8, 0.7))
for g, (lab, a, b) in enumerate(groups):
    cx = jx + slot * (g + 0.5)
    vbar(cx - 36, base, a * 2.0, 56, "red", f"{a:g}", cb)
    vbar(cx + 36, base, b * 2.0, 56, "green", f"{b:g}", cb)
    f.text(cx, base + 24, lab, size=MIN, color=MUTED, anchor="middle", box=cb)
f.line(f"M{jx} {base}H{jx + jw}", "#B9B4A8", 1)
note(jx, top + 250, "fell, %", box=cb)

# ---------------------------------------------------------------- (c) reward hacking
top = f.panel(PC, TOP_Y, W_C, BOT_Y - TOP_Y, "red", "(c) Wrong reward")
cc = f.card(PC + 10, top + 4, W_C - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
kx, kw = PC + 22, W_C - 44
f.image(ASSETS / "hack.jpg", kx, top + 16, kw, 150)
name(kx, top + 202, "Speed", box=cc)
note(kx + kw, top + 202, "m/s", box=cc, anchor="end")
hb = (("Command", 0.6, "gray", "0.6"), ("8 terms", 0.6, "green", "0.6"), ("Speed only", 4.2, "red", "4.2"))
for i, (lab, v, role, txt) in enumerate(hb):
    hbar(kx, top + 222 + i * 38, v / 4.2 * 130, 26, role, txt, lab, 120, cc)
f.line(f"M{kx} {top + 346}H{kx + kw}", HAIR, 1)
name(kx, top + 378, "Asymmetric critic", box=cc)
half = (kw - 10) / 2
f.chip(kx, top + 392, half, 40, "actor 44", "purple", size=LABEL, fill="#FFFFFF", stroke=PAL["purple"].accent, color=INK)
f.chip(kx + half + 10, top + 392, half, 40, "critic 44 + 7", "amber", size=LABEL, fill="#FFFFFF", stroke=PAL["amber"].accent, color=INK)

f.save(str(OUT))
print(OUT)
