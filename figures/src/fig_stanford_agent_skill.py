"""Stanford AI Agent Skill figure: one entry skill, seven internal modules, the course material around it.

Facts come from the repo README.md and POST.zh-CN.md (stanford-ai-agent-skill): module list and order,
nine lectures, digest / lecture guide / glossary / evidence and limits / timestamped references.
"""

from pathlib import Path

from figkit import HAIR, INK, MUTED, PAL, WIRE, Fig

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "stanford-agent-skill-modules-figure.svg"

f = Fig(1400, 480)
LABEL, MODULE = f.fs("label"), f.fs("module")
B, G = PAL["blue"], PAL["green"]

TOP_Y, BOT_Y = 8, 472
WA, WB, WC = 300, 720, 320
PA, PB, PC = f.place(8, 1392, (WA, WB, WC), gap=22)


def name(x, y, s, color=INK, box=None, anchor="start"):
    f.text(x, y, s, size=MODULE, weight=500, color=color, box=box, anchor=anchor)


def note(x, y, s, box=None, anchor="start", color=MUTED):
    f.text(x, y, s, size=LABEL, color=color, box=box, anchor=anchor, family="serif", italic=True)


# ---------------------------------------------------------------- (a) ask
top = f.panel(PA, TOP_Y, WA, BOT_Y - TOP_Y, "gray", "(a) Entry")
Y0 = top + 10
q = f.card(PA + 10, Y0, WA - 20, 190, fill="#FFFFFF", stroke=HAIR)
name(PA + 24, Y0 + 34, "Your agent", box=q)
f.chip(PA + 24, Y0 + 56, WA - 48, 46, "from scratch", "gray", fill="#FFFFFF", family="mono")
f.chip(PA + 24, Y0 + 112, WA - 48, 46, "half-built", "gray", fill="#FFFFFF", family="mono")
sk = f.card(PA + 10, Y0 + 240, WA - 20, BOT_Y - 10 - (Y0 + 240), "green", key=True)
name(PA + 24, Y0 + 276, "One skill", color=G.deep, box=sk)
f.chip(PA + 24, Y0 + 298, WA - 48, 46, "SKILL.md", "green", fill="#FFFFFF", stroke=G.accent, color=INK, family="mono")
f.connect(q, sk, color=G.accent, sw=2)

# ---------------------------------------------------------------- (b) modules
top = f.panel(PB, TOP_Y, WB, BOT_Y - TOP_Y, "blue", "(b) Seven modules")
mods = (
    ("01", "LOOP", "最小闭环"),
    ("02", "SCALE", "测试时预算"),
    ("03", "VERIFY", "验证与 Judge"),
    ("04", "CONTROL", "长程控制"),
    ("05", "TRAIN", "训练回写"),
    ("06", "RESEARCH", "检索与主张"),
    ("07", "EVALUATE", "生产评测"),
)
xs = f.cols(PB + 12, PB + WB - 12, 4, gap=14)
CH = 186
rows = (Y0, Y0 + CH + 14)
for i, (num, en, zh) in enumerate(mods):
    x, w = xs[i % 4]
    y = rows[i // 4]
    c = f.card(x, y, w, CH, "blue")
    f.text(x + 12, y + 36, num, size=LABEL, color=B.deep, family="mono", box=c)
    name(x + 12, y + 84, en, color=B.deep, box=c)
    f.text(x + 12, y + 120, zh, size=LABEL, color=INK, box=c)
x, w = xs[3]
c = f.card(x, rows[1], w, CH, "gray")
f.text(x + 12, rows[1] + 36, "CS329A", size=LABEL, color=MUTED, family="mono", box=c)
name(x + 12, rows[1] + 84, "9 lectures", box=c)

# ---------------------------------------------------------------- (c) repo
top = f.panel(PC, TOP_Y, WC, BOT_Y - TOP_Y, "purple", "(c) In the repo")
items = (
    ("课程精华", "DIGEST"),
    ("九讲导读", "LECTURE_GUIDE"),
    ("术语表", "GLOSSARY"),
    ("证据边界", "EVIDENCE_AND_LIMITS"),
    ("时间戳参考", "references/"),
)
GAP = 12
h = (BOT_Y - 10 - Y0 - GAP * 4) / 5
for k, (zh, fn) in enumerate(items):
    y = Y0 + k * (h + GAP)
    c = f.card(PC + 10, y, WC - 20, h, "purple" if k < 4 else "gray")
    f.text(PC + 24, y + h / 2 - 4, zh, size=MODULE, weight=500, color=PAL["purple"].deep if k < 4 else INK, box=c)
    f.text(PC + 24, y + h / 2 + 24, fn, size=f.fs("min"), color=MUTED, family="mono", box=c)

f.save(str(OUT))
print(OUT)
