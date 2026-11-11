"""EP14 figure: ViT patches, DINO self-distillation, frozen patch features, and one-demo grasping.

Numbers are from the episode's own experiment (策划/实验/结果.md; Apple M5 Max, MuJoCo 4.0.0, all simulated):
E2 handle-to-handle on another mug, each model at 224 px, 40 image pairs (DINOv2-B 0.71, SigLIP-B 0.39);
E3 / E3b one demonstration, 50 trials per cell, yaw within 45 degrees (whole mug 29 vs 26, handle only 40 vs 4).
Images are the episode's Blender Cycles still (HERO_CAM), its last grasp frame, and the PCA maps computed on it.
"""

from pathlib import Path

from figkit import HAIR, INK, MUTED, PAL, Fig

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets" / "ep14-vision-encoder"
OUT = HERE.parent / "ep14-vision-encoder-figure.svg"

f = Fig(1400, 520)
LABEL, MODULE, MIN = f.fs("label"), f.fs("module"), f.fs("min")
TOP_Y, BOT_Y = 8, 512
W_A, W_B, W_C, W_D = 284, 420, 336, 320
PA, PB, PC, PD = f.place(8, 1392, (W_A, W_B, W_C, W_D), gap=8)
DINO, SIG = "orange", "purple"


def name(x, y, s, box=None, anchor="start", color=INK):
    f.text(x, y, s, size=MODULE, weight=500, color=color, box=box, anchor=anchor)


def note(x, y, s, box=None, anchor="start", color=MUTED):
    f.text(x, y, s, size=LABEL, color=color, box=box, anchor=anchor, family="serif", italic=True)


def hbar(x, y, w, h, role, value, box):
    p = PAL[role]
    f.add(f'<rect x="{x}" y="{y}" width="{max(w, 2):.1f}" height="{h}" fill="{p.mid}" stroke="{p.accent}" '
          f'stroke-width="1"/>')
    f.text(x + max(w, 2) + 8, y + h / 2 + LABEL * 0.36, value, size=LABEL, weight=700, color=p.deep, box=box)


# ---------------------------------------------------------------- (a) ViT patches
top = f.panel(PA, TOP_Y, W_A, BOT_Y - TOP_Y, "gray", "(a) ViT patches")
ca = f.card(PA + 10, top + 4, W_A - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
ix, iw = PA + 22, W_A - 44
grid_n = 14
f.image(ASSETS / "hero.jpg", ix, top + 16, iw, iw)
step = iw / grid_n
lines = "".join(f"M{ix + c * step:.1f} {top + 16}V{top + 16 + iw}" for c in range(1, grid_n))
lines += "".join(f"M{ix} {top + 16 + r * step:.1f}H{ix + iw}" for r in range(1, grid_n))
f.add(f'<path data-qa="ignore" d="{lines}" fill="none" stroke="#FFFFFF" stroke-opacity="0.45" stroke-width="0.8"/>')
ya = top + 16 + iw + 34
name(ix, ya, "224 px, $p=16$", box=ca)
f.tokens(ix, ya + 18, 14, "gray", w=12, h=10, gap=4)
note(ix, ya + 58, "$14\\times 14=196$ tokens", box=ca)
f.chip(ix, ya + 76, iw, 40, "$z_0=x_pE+E_{pos}$", "gray", size=LABEL, fill="#FFFFFF",
       stroke=PAL["gray"].accent, color=INK)

# ---------------------------------------------------------------- (b) DINO self-distillation
top = f.panel(PB, TOP_Y, W_B, BOT_Y - TOP_Y, "blue", "(b) DINO self-distillation")
tx, tw = PB + 16, 88
gx, gw = PB + 120, 80
cx_, cw_ = PB + 216, 84
px, pw = PB + 316, 88
row_t, row_s, rh = top + 14, top + 166, 64
thumb_t = f.image(ASSETS / "hero.jpg", tx, row_t, tw, rh)
thumb_s = f.image(ASSETS / "mug_a.png", tx, row_s, tw, rh)
note(tx, row_t + rh + 24, "global", box=None)
note(tx, row_s + rh + 24, "local", box=None)
teacher = f.trapezoid(gx, row_t, gw, rh, "blue", "$g_{\\theta_t}$", direction="right", dashed=True, fill="#FFFFFF")
student = f.trapezoid(gx, row_s, gw, rh, "blue", "$g_{\\theta_s}$", direction="right")
ctr = f.chip(cx_, row_t + 12, cw_, 40, "$-c,\\ \\tau_t$", "red", size=LABEL)
tau_s = f.chip(cx_, row_s + 12, cw_, 40, "$\\tau_s$", "blue", size=LABEL)
p_t = f.chip(px, row_t + 12, pw, 40, "$P_t$", "gray", size=LABEL, fill="#FFFFFF")
p_s = f.chip(px, row_s + 12, pw, 40, "$P_s$", "gray", size=LABEL, fill="#FFFFFF")
loss = f.card(px, row_t + 88, pw, 42, "red", key=True)
f.text(px + pw / 2, row_t + 88 + 21 + LABEL * 0.36, "$H(P_t,P_s)$", size=LABEL, anchor="middle", box=loss)
f.connect(thumb_t, teacher)
f.connect(thumb_s, student)
f.connect(teacher, ctr)
f.connect(student, tau_s)
f.connect(ctr, p_t)
f.connect(tau_s, p_s)
f.connect(p_t, loss, sides=("bottom", "top"))
f.connect(p_s, loss, sides=("top", "bottom"))
f.arc(student, teacher, sides=("top", "bottom"), bulge=-34, label="EMA", label_size=LABEL, knockout=True)
# DINOv2 adds a masked-patch term
yb = row_s + rh + 48
cb2 = f.card(PB + 10, yb, W_B - 20, BOT_Y - 10 - yb, fill="#FFFFFF", stroke=HAIR)
name(PB + 22, yb + 32, "DINOv2", box=cb2)
masked = {(0, 1), (0, 4), (1, 2), (1, 6), (2, 0), (2, 5), (3, 3), (3, 6)}
f.token_grid(PB + 22, yb + 50, 4, 8, "blue", cell=14, gap=3, masked=masked)
f.token_grid(PB + 196, yb + 50, 4, 8, "blue", cell=14, gap=3, highlight=masked, highlight_role="red")
note(PB + 22 + 67, yb + 142, "student", box=cb2, anchor="middle")
note(PB + 196 + 67, yb + 142, "teacher", box=cb2, anchor="middle")
f.text(PB + W_B - 22, yb + 32, "$\\mathcal{L}_{iBOT}$", size=LABEL, anchor="end", box=cb2)

# ---------------------------------------------------------------- (c) patch features
top = f.panel(PC, TOP_Y, W_C, BOT_Y - TOP_Y, DINO, "(c) Patch features")
cc = f.card(PC + 10, top + 4, W_C - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
lx = PC + 22
im_w = 96
c1, c2 = f.place(PC + 112, PC + W_C - 20, (im_w, im_w), gap=8)
rows = (("RGB", "mug_a.png", "mug_b.png", INK),
        ("DINOv2", "pca_dino_b_a.png", "pca_dino_b_b.png", PAL[DINO].deep),
        ("SigLIP", "pca_siglip_b_a.png", "pca_siglip_b_b.png", PAL[SIG].deep))
for i, (lab, a, b, col) in enumerate(rows):
    y = top + 16 + i * (im_w + 8)
    f.image(ASSETS / a, c1, y, im_w, im_w)
    f.image(ASSETS / b, c2, y, im_w, im_w)
    name(lx, y + im_w / 2 + MODULE * 0.36, lab, box=cc, color=col)
yh = top + 16 + 3 * (im_w + 8) + 22
name(lx, yh, "Handle → handle", box=cc)
hbar(lx, yh + 16, 0.71 * 200, 24, DINO, "0.71", cc)
hbar(lx, yh + 48, 0.39 * 200, 24, SIG, "0.39", cc)

# ---------------------------------------------------------------- (d) one demonstration
top = f.panel(PD, TOP_Y, W_D, BOT_Y - TOP_Y, "green", "(d) One-demo grasp")
cd = f.card(PD + 10, top + 4, W_D - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
kx, kw = PD + 22, W_D - 44
f.image(ASSETS / "grasp.jpg", kx, top + 16, kw, 180)
yd = top + 16 + 180 + 34
name(kx, yd, "Success / 50", box=cd)
f.badge(kx + kw - 150, yd + 18, "DINOv2", DINO, size=MIN, w=72)
f.badge(kx + kw - 72, yd + 18, "SigLIP", SIG, size=MIN, w=72)
groups = (("whole mug", 29, 26), ("handle only", 40, 4))
for g, (lab, a, b) in enumerate(groups):
    y = yd + 20 + g * 96
    note(kx, y + 14, lab, box=cd)
    hbar(kx, y + 26, a * 4.4, 22, DINO, str(a), cd)
    hbar(kx, y + 54, max(b * 4.4, 2), 22, SIG, str(b), cd)

f.save(str(OUT))
print(OUT)
