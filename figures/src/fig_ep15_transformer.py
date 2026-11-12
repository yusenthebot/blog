"""EP15 figure: attention by hand, the Transformer block, attention inside DINOv2, and our tiny models.

Numbers are from the episode's own files (策划/实验/结果.md, Apple M5 Max, torch 2.15.0):
(a) the four-token hand calculation with hand-picked integer matrices (E2): scores [4, 5, 3, 1], divided by
    sqrt(2), softmax [0.27, 0.56, 0.14, 0.03], output of cup [1.14, 2.36]; the 4 x 4 map is the full weight matrix;
(c) DINOv2 with registers ViT-B/14 on the episode-14 still at 48 x 27 patches (E1): the head-mean map of
    layer 6 and layer 9 head 6 for the teal-mug handle query (46 % on the other mug's handle);
(d) E3b reverse task (5 seeds: 100 % vs 14.4 %) and E4 attention-only induction task
    (5 seeds: 1 layer 16.7 %, 2 layers 99.4 %, 2 layers with the previous-token heads zeroed 16.4 %).
Images: the hero render with the episode's own attention overlays, and token crops from the film frame at 86.5 s.
"""

from pathlib import Path

from figkit import HAIR, INK, MUTED, PAL, Fig

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets" / "ep15-transformer"
OUT = HERE.parent / "ep15-transformer-figure.svg"

f = Fig(1400, 520)
LABEL, MODULE, MIN = f.fs("label"), f.fs("module"), f.fs("min")
TOP_Y, BOT_Y = 8, 512
W_A, W_B, W_C, W_D = 430, 300, 300, 330
PA, PB, PC, PD = f.place(8, 1392, (W_A, W_B, W_C, W_D), gap=8)
ATT, POS, DEPTH = "orange", "purple", "blue"

HAND_A = ((0.27, 0.56, 0.14, 0.03), (0.54, 0.27, 0.13, 0.06), (0.37, 0.37, 0.18, 0.09), (0.22, 0.45, 0.22, 0.11))


def name(x, y, s, box=None, anchor="start", color=INK):
    f.text(x, y, s, size=MODULE, weight=500, color=color, box=box, anchor=anchor)


def note(x, y, s, box=None, anchor="start", color=MUTED):
    f.text(x, y, s, size=LABEL, color=color, box=box, anchor=anchor, family="serif", italic=True)


def hbar(x, y, w, h, role, value, box):
    p = PAL[role]
    f.add(f'<rect x="{x}" y="{y}" width="{max(w, 2):.1f}" height="{h}" fill="{p.mid}" stroke="{p.accent}" '
          f'stroke-width="1"/>')
    f.text(x + max(w, 2) + 8, y + h / 2 + LABEL * 0.36, value, size=LABEL, weight=700, color=p.deep, box=box)


# ---------------------------------------------------------------- (a) attention by hand
top = f.panel(PA, TOP_Y, W_A, BOT_Y - TOP_Y, ATT, "(a) Attention by hand", sub="$d_k=2$")
ca = f.card(PA + 10, top + 4, W_A - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
lx = PA + 22
cw = 64
xs = f.place(PA + 128, PA + W_A - 22, (cw,) * 4, gap=8)
y_img = top + 16
for x, tok in zip(xs, ("cup", "table", "apple", "hand")):
    f.image(ASSETS / f"tok_{tok}.jpg", x, y_img, cw, cw)
    f.text(x + cw / 2, y_img + cw + 24, tok, size=MIN, anchor="middle", family="mono", box=ca,
           color=PAL[ATT].deep if tok == "cup" else INK)
rows = (
    ("$q_{cup}\\cdot k_j$", ("4", "5", "3", "1")),
    ("$/\\sqrt{d_k}$", ("2.83", "3.54", "2.12", "0.71")),
    ("softmax $a_j$", ("0.27", "0.56", "0.14", "0.03")),
)
ch, pitch = 38, 54
y0 = y_img + cw + 46
for i, (lab, vals) in enumerate(rows):
    y = y0 + i * pitch
    f.text(lx, y + ch / 2 + LABEL * 0.36, lab, size=LABEL, box=ca)
    for j, (x, v) in enumerate(zip(xs, vals)):
        hot = i == 2 and j == 1
        f.chip(x, y, cw, ch, v, ATT if hot else None, size=LABEL, weight=700 if hot else 400,
               fill=None if hot else "#FFFFFF", stroke=PAL[ATT].accent if hot else HAIR)
y_out = y0 + 3 * pitch
f.text(lx, y_out + ch / 2 + LABEL * 0.36, "$z_{cup}=\\Sigma\\,a_jv_j$", size=LABEL, box=ca)
f.chip(xs[0], y_out, xs[3] + cw - xs[0], ch, "[1.14, 2.36]", ATT, size=LABEL, family="mono")
y_f = y_out + pitch + 10
f.chip(lx, y_f, xs[3] + cw - lx, 40, "$\\mathrm{softmax}(QK^{\\top}/\\sqrt{d_k})\\,V$", "gray", size=LABEL,
       fill="#FFFFFF", stroke=PAL["gray"].accent, color=INK)
note(lx, y_f + 40 + 28, "hand-picked $W$", box=ca)

# ---------------------------------------------------------------- (b) Transformer block
top = f.panel(PB, TOP_Y, W_B, BOT_Y - TOP_Y, DEPTH, "(b) Block", sub="$\\times L$")
sx, sw_ = PB + 22, 44
s_top, s_bot = top + 56, BOT_Y - 70
out = f.chip(sx, top + 6, 150, 36, "residual $h^{(l)}$", DEPTH, size=LABEL)
stream = f.card(sx, s_top, sw_, s_bot - s_top, DEPTH, fill=PAL[DEPTH].mid)
inp = f.chip(sx, BOT_Y - 52, 150, 36, "$x_i+p_i$", POS, size=LABEL)
f.connect(inp, stream, sides=("top", "bottom"), ta=None)
f.connect(stream, out, sides=("top", "bottom"), tb=None)
kx, kw = PB + 110, W_B - 132
gap_c = 16
kh = (s_bot - s_top - gap_c) / 2
mlp_c = f.card(kx, s_top, kw, kh, DEPTH)
att_c = f.card(kx, s_top + kh + gap_c, kw, kh, ATT, key=True)
for cid, (y, title) in ((mlp_c, (s_top, "LN, MLP")), (att_c, (s_top + kh + gap_c, "LN, attention"))):
    name(kx + 12, y + 30, title, box=cid)
f.mlp(kx + 24, s_top + 48, kw - 48, kh - 64, (3, 5, 3), DEPTH)
cell = 24
hx = kx + (kw - 4 * cell) / 2
f.heatmap(hx, s_top + kh + gap_c + 48, 4, 4, ATT, cell=cell, values=HAND_A)
for cid in (att_c, mlp_c):
    f.connect(stream, cid, sides=("right", "left"), ta=None, tb=0.72)
    f.connect(cid, stream, sides=("left", "right"), ta=0.28, tb=None)

# ---------------------------------------------------------------- (c) inside DINOv2
top = f.panel(PC, TOP_Y, W_C, BOT_Y - TOP_Y, ATT, "(c) Inside DINOv2")
cc = f.card(PC + 10, top + 4, W_C - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
iw = W_C - 44
ih = round(iw * 2 / 3)
ix = PC + 22
qx, qy = 700 / 900, 220 / 600  # the handle query patch in the 900 x 600 crop
for k, (img, lab, tag) in enumerate((("attn_teal_mug_handle_L06_mean.jpg", "L6, mean", None),
                                     ("attn_L09h06_teal_handle.jpg", "L9, head 6", "46%"))):
    y = top + 44 + k * (ih + 52)
    name(ix, y - 12, lab, box=cc)
    f.image(ASSETS / img, ix, y, iw, ih)
    f.add(f'<circle data-qa="ignore" cx="{ix + qx * iw:.1f}" cy="{y + qy * ih:.1f}" r="9" fill="none" '
          f'stroke="#FFFFFF" stroke-width="2"/>')
    if tag:
        f.badge(ix + iw - 62, y - 30, tag, ATT, size=LABEL, w=62)

# ---------------------------------------------------------------- (d) our tiny models
top = f.panel(PD, TOP_Y, W_D, BOT_Y - TOP_Y, "green", "(d) Tiny models", sub="5 seeds")
cd = f.card(PD + 10, top + 4, W_D - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
bx = PD + 22
blx = bx + 104
scale = 1.25
bh = 26
name(bx, top + 34, "Reverse", box=cd)
for i, (lab, v, role) in enumerate((("pos", 100.0, POS), ("no pos", 14.4, "gray"))):
    y = top + 54 + i * 44
    f.text(bx, y + bh / 2 + MIN * 0.36, lab, size=MIN, family="mono", box=cd)
    hbar(blx, y, v * scale, bh, role, f"{v:g}%", cd)
y2 = top + 196
name(bx, y2, "Induction", box=cd)
ex = f.example(bx, y2 + 16, W_D - 44, 40, fill="#FAF9F6")
f.text(bx + (W_D - 44) / 2, y2 + 16 + 20 + MIN * 0.36, "… 23 5 … 9 23 → 5", size=MIN, family="mono",
       anchor="middle", box=ex)
for i, (lab, v, role) in enumerate((("1 layer", 16.7, "gray"), ("2 layers", 99.4, DEPTH),
                                    ("2, ablated", 16.4, "red"))):
    y = y2 + 80 + i * 48
    f.text(bx, y + bh / 2 + MIN * 0.36, lab, size=MIN, family="mono", box=cd)
    hbar(blx, y, v * scale, bh, role, f"{v:g}%", cd)

f.save(str(OUT))
print(OUT)
