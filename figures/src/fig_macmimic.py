"""MacMimic figure: physics on the CPU, learning on Metal, one exchange per 20 ms control step.

Facts come from ~/macmimic README.md and docs/SuperMimic_MacMimic_报告.md. The robot image is a frame
from the MacMimic README (no film frames: the rollout footage derives from LAFAN1, CC BY-NC-ND).
"""

from pathlib import Path

from figkit import HAIR, INK, MUTED, PAL, WIRE, Fig

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets" / "macmimic"
OUT = HERE.parent / "macmimic-pipeline-figure.svg"

f = Fig(1400, 500)
LABEL, MODULE = f.fs("label"), f.fs("module")
B, P, G, A, O = PAL["blue"], PAL["purple"], PAL["green"], PAL["amber"], PAL["orange"]

TOP_Y, BOT_Y = 8, 492
PA, PB, PC = f.place(8, 1392, (330, 660, 314), gap=40)
WA, WB, WC = 330, 660, 314


def name(x, y, s, color=INK, box=None, anchor="start"):
    f.text(x, y, s, size=MODULE, weight=500, color=color, box=box, anchor=anchor)


def note(x, y, s, box=None, anchor="start", color=MUTED):
    f.text(x, y, s, size=LABEL, color=color, box=box, anchor=anchor, family="serif", italic=True)


# ------------------------------------------------------------ (a) physics on CPU
top = f.panel(PA, TOP_Y, WA, BOT_Y - TOP_Y, "blue", "(a) Physics", "CPU")
ROW1_Y, ROW2_Y, ROW_H = top + 10, top + 262, 150
ca = f.card(PA + 10, ROW1_Y, WA - 20, BOT_Y - 10 - ROW1_Y, "blue", key=True)
ix, iw = PA + 24, WA - 48
name(ix, ROW1_Y + 34, "MuJoCo rollout", color=B.deep, box=ca)
f.text(ix, ROW1_Y + 62, "mujoco.rollout", size=LABEL, color=MUTED, family="mono", box=ca)
for k, s in enumerate(("8 threads", "2048 worlds", "4$\\times$5 ms PD")):
    f.chip(ix, ROW1_Y + 84 + k * 58, iw, 46, s, "blue", fill="#FFFFFF", stroke=B.accent, color=INK, family="mono")
name(ix, ROW1_Y + 296, "Unified memory", box=ca)
f.chip(ix, ROW1_Y + 314, iw, 46, "64 GB, no PCIe", "gray", fill="#FFFFFF", family="mono")
note(ix, ROW1_Y + 394, "states / actions every 20 ms", box=ca)

# ------------------------------------------------------------ (b) learning on Metal
top = f.panel(PB, TOP_Y, WB, BOT_Y - TOP_Y, "purple", "(b) Learning", "Metal (MPS), torch.compile")
xs = f.cols(PB + 12, PB + WB - 12, 3, gap=40)
CARD_H = 232
buf = f.card(xs[0][0], ROW1_Y, xs[0][1], CARD_H, "gray")
wm = f.card(xs[1][0], ROW1_Y, xs[1][1], CARD_H, "purple")
im = f.card(xs[2][0], ROW1_Y, xs[2][1], CARD_H, "amber", key=True)

x, w = xs[0]
name(x + 12, ROW1_Y + 34, "Replay", box=buf)
f.text(x + w - 12, ROW1_Y + 34, "$\\mathcal{B}$", size=MODULE, anchor="end", box=buf)
f.cylinder(x + 24, ROW1_Y + 56, w - 48, 100, "gray", "$(s_t,a_t)$", size=LABEL)

x, w = xs[1]
name(x + 12, ROW1_Y + 34, "World model", color=P.deep, box=wm)
f.text(x + 12, ROW1_Y + 66, "$f_\\omega$", size=MODULE, box=wm)
f.chip(x + 12, ROW1_Y + 84, w - 24, 44, "fit $k=8$", "purple", fill="#FFFFFF", stroke=P.accent, color=INK)
f.chip(x + 12, ROW1_Y + 138, w - 24, 44, "MLP $512\\times3$", "purple", fill="#FFFFFF", stroke=P.accent, color=INK)

x, w = xs[2]
name(x + 12, ROW1_Y + 34, "Imagination", color=A.deep, box=im)
f.text(x + 12, ROW1_Y + 66, "$H=32$", size=MODULE, box=im)
f.chip(x + 12, ROW1_Y + 84, w - 24, 44, "BPTT", "amber", fill="#FFFFFF", stroke=A.accent, color=INK)
f.chip(x + 12, ROW1_Y + 138, w - 24, 44, "critic $V_\\psi$", "amber", fill="#FFFFFF", stroke=A.accent, color=INK)
note(x + 12, ROW1_Y + 212, "gradient through $f_\\omega$", box=im)

f.connect(buf, wm, color=P.accent, sw=2)
f.connect(wm, im, color=P.accent, sw=2)

pol = f.card(xs[0][0], ROW2_Y + 20, PB + WB - 12 - xs[0][0], 130, "green", key=True)
name(xs[0][0] + 14, ROW2_Y + 58, "Policy", color=G.deep, box=pol)
f.text(xs[0][0] + 96, ROW2_Y + 58, "$\\pi_\\theta$", size=MODULE, box=pol)
f.chip(xs[0][0] + 14, ROW2_Y + 80, 200, 44, "512-256-128", "green", fill="#FFFFFF", stroke=G.accent, color=INK,
       family="mono")
f.chip(xs[0][0] + 228, ROW2_Y + 80, 190, 44, "EMA", "green", fill="#FFFFFF", stroke=G.accent, color=INK,
       family="mono")
f.connect(im, pol, sides=("bottom", "top"), color=G.accent, sw=2, tb=None, label="$\\nabla\\hat{J}$", label_color=G.deep)

# wires between (a) and (b): states out, actions in
f.connect(ca, buf, color=WIRE, sw=1.6, ta=None)
f.connect(pol, ca, color=WIRE, sw=1.6, tb=None)

# ------------------------------------------------------------ (c) result
top = f.panel(PC, TOP_Y, WC, BOT_Y - TOP_Y, "gray", "(c) Result", "simulation")
cc = f.card(PC + 10, ROW1_Y, WC - 20, BOT_Y - 10 - ROW1_Y, fill="#FFFFFF", stroke=HAIR)
jx, jw = PC + 22, WC - 44
name(jx, ROW1_Y + 40, "One M5 Max", box=cc)
half = (jw - 10) / 2
f.chip(jx, ROW1_Y + 66, half, 54, "97.6 min", "gray", fill="#FFFFFF", size=LABEL)
f.chip(jx + half + 10, ROW1_Y + 66, half, 54, "40/40", "green", fill="#FFFFFF", stroke=PAL["green"].accent,
       size=LABEL, family="mono", color=INK)
name(jx, ROW1_Y + 176, "Per iteration", box=cc)
f.chip(jx, ROW1_Y + 196, jw, 54, "CPU eager 10,567 ms", "gray", fill="#FFFFFF", size=LABEL, family="mono")
f.chip(jx, ROW1_Y + 262, jw, 54, "Metal 272 ms", "orange", fill="#FFFFFF", stroke=O.accent, size=LABEL, family="mono",
       color=INK)

f.save(str(OUT))
print(OUT)
