"""EP13 figure: predict the ball with drag and spin, the latency budget, and a small stroke network.

All numbers are simulated, from the episode's own experiment (策划/实验/结果.md; MuJoCo 4.0.0, Franka Panda on a
rail, 2026-11-10): E2 arrival error 0.2 s before the hitting plane (topspin, 5 seeds), E3 latency sweep with the
3x arm (schematic; 5 seeds x 30 balls), E4 network on 450 held-out balls (5 seeds) and its face-pitch sweep.
Images are frames from the episode film (MuJoCo motion, Blender render).
"""

from pathlib import Path

from figkit import HAIR, INK, MUTED, PAL, Fig

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets" / "ep13-table-tennis"
OUT = HERE.parent / "ep13-table-tennis-figure.svg"

f = Fig(1400, 540)
LABEL, MODULE, MIN = f.fs("label"), f.fs("module"), f.fs("min")
TOP_Y, BOT_Y = 8, 532
W_A, W_B, W_C, W_D = 360, 320, 320, 360
PA, PB, PC, PD = f.place(8, 1392, (W_A, W_B, W_C, W_D), gap=8)
IMG_H = 178


def name(x, y, s, color=INK, box=None, anchor="start"):
    f.text(x, y, s, size=MODULE, weight=500, color=color, box=box, anchor=anchor)


def note(x, y, s, box=None, anchor="start", color=MUTED):
    f.text(x, y, s, size=LABEL, color=color, box=box, anchor=anchor, family="serif", italic=True)


def white_card(px, pw, top):
    return f.card(px + 10, top + 4, pw - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)


def hbar(x, y, w, h, role, value, label, label_w, box):
    p = PAL[role]
    f.text(x, y + h / 2 + LABEL * 0.36, label, size=LABEL, color=INK, box=box)
    bx = x + label_w
    f.add(f'<rect x="{bx}" y="{y}" width="{max(w, 2):.1f}" height="{h}" fill="{p.mid}" stroke="{p.accent}" '
          f'stroke-width="1"/>')
    f.text(bx + max(w, 2) + 8, y + h / 2 + LABEL * 0.36, value, size=LABEL, weight=700, color=p.deep, box=box)


# ---------------------------------------------------------------- (a) predict
top = f.panel(PA, TOP_Y, W_A, BOT_Y - TOP_Y, "blue", "(a) Predict")
ca = white_card(PA, W_A, top)
ix, iw = PA + 22, W_A - 44
f.image(ASSETS / "predict.jpg", ix, top + 16, iw, IMG_H)
ROW1 = top + 16 + IMG_H + 36
name(ix, ROW1, "Arrival error", box=ca)
note(ix + iw, ROW1, "0.2 s ahead", box=ca, anchor="end")
errs = (("Gravity", 14.6, "gray"), ("+ drag", 9.4, "purple"), ("+ spin", 3.5, "blue"))
for i, (lab, v, role) in enumerate(errs):
    hbar(ix, ROW1 + 18 + i * 36, v / 14.6 * 140, 24, role, f"{v:g} cm", lab, 92, ca)
f.chip(ix, BOT_Y - 72, iw, 44, "$a=g-k_D|v|v+k_L\\,\\omega\\times v$", "blue", size=LABEL, fill="#FFFFFF",
       stroke=PAL["blue"].accent, color=INK)

# ---------------------------------------------------------------- (b) latency
top = f.panel(PB, TOP_Y, W_B, BOT_Y - TOP_Y, "amber", "(b) Latency")
cb = white_card(PB, W_B, top)
jx, jw = PB + 22, W_B - 44
f.image(ASSETS / "robot.jpg", jx, top + 16, jw, IMG_H)
name(jx, ROW1, "Contact, 3× arm", box=cb)
col_w = 64
c1, c2 = jx + jw - 2 * col_w - 8, jx + jw - col_w
for cx, lab in ((c1, "10 ms"), (c2, "200 ms")):
    f.text(cx + col_w / 2, ROW1 + 34, lab, size=MIN, color=MUTED, anchor="middle", box=cb, family="mono")
rows_b = (("Spin-aware", "94%", "82%", "blue"), ("Spin-blind", "87%", "38%", "red"))
for i, (lab, a, b, role) in enumerate(rows_b):
    y = ROW1 + 46 + i * 46
    f.text(jx, y + 24, lab, size=LABEL, color=INK, box=cb)
    f.chip(c1, y, col_w, 36, a, role, size=LABEL, fill="#FFFFFF", stroke=PAL[role].accent, color=INK)
    f.chip(c2, y, col_w, 36, b, role, size=LABEL, weight=700, fill="#FFFFFF", stroke=PAL[role].accent)
f.chip(jx, BOT_Y - 72, jw, 44, "Panda: 1.8× joint limit", "amber", size=LABEL, fill="#FFFFFF",
       stroke=PAL["amber"].accent, color=INK)

# ---------------------------------------------------------------- (c) stroke network
top = f.panel(PC, TOP_Y, W_C, BOT_Y - TOP_Y, "green", "(c) Stroke MLP")
cc = white_card(PC, W_C, top)
kx, kw = PC + 22, W_C - 44
NET_X, NET_W = kx + 56, kw - 112
f.mlp(NET_X, top + 16, NET_W, IMG_H, (8, 12, 12, 3), "green", r=4)
f.text(kx, top + 16 + IMG_H / 2 + LABEL * 0.36, "$s_{in}$", size=MODULE, box=cc)
f.text(kx + kw, top + 16 + IMG_H / 2 + LABEL * 0.36, "$a,b,s$", size=LABEL, anchor="end", box=cc)
name(kx, ROW1, "8-32-32-3", box=cc)
note(kx + kw, ROW1, "1,443 params", box=cc, anchor="end")
f.text(kx, ROW1 + 34, "held-out return", size=MIN, color=MUTED, box=cc, family="mono")
for i, (lab, v, role) in enumerate((("with $\\omega$", 100.0, "green"), ("no $\\omega$", 80.5, "red"))):
    hbar(kx, ROW1 + 46 + i * 36, v / 100 * 120, 24, role, f"{v:g}%", lab, 84, cc)
f.chip(kx, BOT_Y - 72, kw, 44, "CEM teacher", "green", size=LABEL, fill="#FFFFFF",
       stroke=PAL["green"].accent, color=INK)

# ---------------------------------------------------------------- (d) learned face pitch
top = f.panel(PD, TOP_Y, W_D, BOT_Y - TOP_Y, "purple", "(d) Learned face pitch")
cd = white_card(PD, W_D, top)
gx0, gx1 = PD + 76, PD + W_D - 34
gy0, gy1 = top + 50, BOT_Y - 92
spins = (-90, -45, 0, 45, 90)
pitch = (52.3, 36.8, 19.8, 2.3, -17.7)
blind = 18.8
YMIN, YMAX = -25.0, 60.0


def X(s):
    return gx0 + (s + 90) / 180 * (gx1 - gx0)


def Y(p):
    return gy1 - (p - YMIN) / (YMAX - YMIN) * (gy1 - gy0)


f.line(f"M{gx0} {gy0}V{gy1}H{gx1}", "#B9B4A8", 1)
f.line(f"M{gx0} {Y(0):.1f}H{gx1}", HAIR, 1, dashed=True)
for v in (50, 0):
    f.text(gx0 - 10, Y(v) + MIN * 0.36, f"{v}°", size=MIN, color=MUTED, anchor="end", box=cd, family="mono")
for s in (-90, 0, 90):
    f.text(X(s), gy1 + 26, f"{s}", size=MIN, color=MUTED, anchor="middle", box=cd, family="mono")
f.text((gx0 + gx1) / 2, gy1 + 56, "spin, rev/s", size=LABEL, color=MUTED, anchor="middle", box=cd,
       family="serif", italic=True)
f.line(f"M{X(-90):.1f} {Y(blind):.1f}H{X(90):.1f}", PAL["red"].accent, 1.6, dashed=True)
pts = " ".join(f"{'M' if i == 0 else 'L'}{X(s):.1f} {Y(p):.1f}" for i, (s, p) in enumerate(zip(spins, pitch)))
f.line(pts, PAL["purple"].accent, 2.2)
for s, p in zip(spins, pitch):
    f.add(f'<circle cx="{X(s):.1f}" cy="{Y(p):.1f}" r="4" fill="#FFFFFF" stroke="{PAL["purple"].deep}" '
          f'stroke-width="1.4"/>')
note(X(-90) + 6, Y(52.3) - 16, "open", box=cd, color=PAL["purple"].deep)
note(X(40), Y(0) + 34, "close", box=cd, anchor="end", color=PAL["purple"].deep)
f.text(X(90), Y(blind) - 12, "no $\\omega$", size=MIN, color=PAL["red"].deep, anchor="end", box=cd)
f.text(PD + 22, top + 30, "backspin", size=MIN, color=MUTED, box=cd, family="mono")
f.text(PD + W_D - 22, top + 30, "topspin", size=MIN, color=MUTED, anchor="end", box=cd, family="mono")

f.save(str(OUT))
print(OUT)
