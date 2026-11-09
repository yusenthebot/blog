"""EP11 figure: what a robot data point is, where it comes from, the data triangle, and our Apollo test.

Images are frames from the episode film (Blender renders of MuJoCo scenes; collection devices are
re-created illustrations, not original data). Numbers come from the narration script and
策划/实验/结果.md: RT-1 about 130k demos, ALOHA 50 Hz and 14 joint angles, UMI 1,400 demos in 12 h,
Aria 1,400 per hour, VPT 70k hours of web video, GR00T N1 8,375.7 h with 88.4 h own teleop,
dance RMS 4.3 deg, cup knocked 17.5 cm, hand-fixed lift 48 cm.
"""

from pathlib import Path

from figkit import HAIR, INK, MUTED, PAL, Fig

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets" / "ep11-robot-data"
OUT = HERE.parent / "ep11-robot-data-sources-figure.svg"

f = Fig(1400, 540)
LABEL, MODULE = f.fs("label"), f.fs("module")

TOP_Y, BOT_Y = 8, 532
W_A, W_B, W_C, W_D = 260, 520, 240, 340
PA, PB, PC, PD = f.place(8, 1392, (W_A, W_B, W_C, W_D), gap=8)


def name(x, y, s, color=INK, box=None, anchor="start"):
    f.text(x, y, s, size=MODULE, weight=500, color=color, box=box, anchor=anchor)


def note(x, y, s, box=None, anchor="start", color=MUTED):
    f.text(x, y, s, size=LABEL, color=color, box=box, anchor=anchor, family="serif", italic=True)


# ---------------------------------------------------------------- (a) one data point
top = f.panel(PA, TOP_Y, W_A, BOT_Y - TOP_Y, "gray", "(a) One datum")
ca = f.card(PA + 10, top + 4, W_A - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
ix, iw = PA + 22, W_A - 44
f.image(ASSETS / "pair.jpg", ix, top + 16, iw, 144)
name(ix, top + 210, "Image", box=ca)
f.text(ix + iw, top + 210, "$o_t$", size=MODULE, anchor="end", box=ca)
f.chip(ix, top + 226, iw, 40, "camera frame", "gray", size=LABEL, fill="#FFFFFF")
name(ix, top + 312, "Action", box=ca)
f.text(ix + iw, top + 312, "$a_t$", size=MODULE, anchor="end", box=ca)
f.chip(ix, top + 328, iw, 40, "32 joint angles", "gray", size=LABEL, fill="#FFFFFF")

# ---------------------------------------------------------------- (b) sources
top = f.panel(PB, TOP_Y, W_B, BOT_Y - TOP_Y, "blue", "(b) Data sources")
rows = f.rows(top + 4, BOT_Y - 10, 5, gap=8)
sources = (
    ("RT-1", "2 VR controllers", "rt1.jpg", "~130k demos"),
    ("ALOHA", "4 cameras, 14 joints", "aloha.jpg", "50 Hz"),
    ("UMI", "wrist GoPro + IMU", "umi.jpg", "1,400 demos"),
    ("Aria glasses", "camera + IMU", "aria.jpg", "1,400 / hour"),
    ("Web video", "images only", "web.jpg", "VPT 70k h"),
)
for (ry, rh), (nm, nt, img, num) in zip(rows, sources):
    c = f.card(PB + 10, ry, W_B - 20, rh, fill="#FFFFFF", stroke=PAL["blue"].accent)
    f.image(ASSETS / img, PB + 20, ry + 10, 118, rh - 20)
    name(PB + 150, ry + 36, nm, color=PAL["blue"].deep, box=c)
    note(PB + 150, ry + 64, nt, box=c)
    f.chip(PB + W_B - 10 - 12 - 138, ry + 22, 138, 40, num, "blue", size=LABEL, fill="#FFFFFF",
           stroke=PAL["blue"].accent, color=INK)

# ---------------------------------------------------------------- (c) triangle
top = f.panel(PC, TOP_Y, W_C, BOT_Y - TOP_Y, "amber", "(c) Data triangle")
cc = f.card(PC + 10, top + 4, W_C - 20, BOT_Y - 10 - top - 4, fill="#FFFFFF", stroke=HAIR)
jx, jw = PC + 22, W_C - 44
f.image(ASSETS / "tri.jpg", jx, top + 16, jw, 164)
for k, s in enumerate(("Like the robot", "Many", "Cheap")):
    f.chip(jx, top + 196 + k * 44, jw, 36, s, "amber", size=LABEL, fill="#FFFFFF", stroke=PAL["amber"].accent,
           color=INK)
name(jx, top + 376, "GR00T N1", color=PAL["amber"].deep, box=cc)
f.text(jx + jw, top + 376, "8,375.7 h", size=LABEL, anchor="end", box=cc)
f.chip(jx, top + 392, jw, 36, "own teleop 1%", "amber", size=LABEL, fill="#FFFFFF", stroke=PAL["amber"].accent,
       color=INK, weight=500)

# ---------------------------------------------------------------- (d) our test
top = f.panel(PD, TOP_Y, W_D, BOT_Y - TOP_Y, "red", "(d) Our test")
r1_top, r1_h = top + 4, 202
r2_top = r1_top + r1_h + 8
r2_h = BOT_Y - 10 - r2_top
kx, kw = PD + 22, W_D - 44
c1 = f.card(PD + 10, r1_top, W_D - 20, r1_h, fill="#FFFFFF", stroke=HAIR)
f.image(ASSETS / "dance.jpg", kx, r1_top + 10, kw, 128)
name(kx, r1_top + 164, "Dance", color=PAL["red"].deep, box=c1)
f.chip(kx + kw - 150, r1_top + 146, 150, 40, "4.3° RMS", "green", size=LABEL, fill="#FFFFFF",
       stroke=PAL["green"].accent, color=INK)
c2 = f.card(PD + 10, r2_top, W_D - 20, r2_h, fill="#FFFFFF", stroke=HAIR)
f.image(ASSETS / "cup.jpg", kx, r2_top + 10, kw, 120)
f.chip(kx, r2_top + 140, kw, 40, "copy: knocked 17.5 cm", "red", size=LABEL, fill="#FFFFFF", stroke=PAL["red"].accent,
       color=INK)
f.chip(kx, r2_top + 188, kw, 40, "fixed: lifts 48 cm", "green", size=LABEL, fill="#FFFFFF",
       stroke=PAL["green"].accent, color=INK)

f.save(str(OUT))
print(OUT)
