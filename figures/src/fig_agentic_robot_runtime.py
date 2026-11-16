"""Rich conceptual runtime diagram; network sizes and signals are schematic."""

from itertools import pairwise
from pathlib import Path

from figkit import HAIR, MUTED, PAL, WIRE, Fig

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "agentic_robot_runtime-figure.svg"
FRAME = HERE / "assets" / "ep10-fast-slow-brain" / "s1.jpg"


def draw() -> None:
    """Render model, signal, runtime and control responsibilities without measured claims."""
    f = Fig(1400, 700)
    label, module, title, hero = (
        f.fs(role) for role in ("label", "module", "title", "hero")
    )
    blue, amber, purple, green = (
        PAL[role] for role in ("blue", "amber", "purple", "green")
    )
    widths = (196, 480, 320, 316)
    xs = f.place(8, 1392, widths, gap=24)
    panels = []
    for index, name in enumerate(
        ("(a) 观测", "(b) 模型", "(c) Runtime", "(d) Robotics")
    ):
        panel = f.card(
            xs[index],
            8,
            widths[index],
            600,
            fill="#F7F7F5",
            stroke=HAIR,
            sw=1 if index == 0 else 0.7,
            dashed=index == 0,
            kind="panel",
            r=6,
        )
        panels.append(panel)
        f.text(xs[index] + 12, 42, name, size=title, weight=700, box=panel)

    # Inputs are concrete data types. The frame is from our previous simulation video;
    # the bars and repeated frames illustrate formats, not a new captured rollout.
    x, w = xs[0] + 10, widths[0] - 20
    vision = f.card(x, 64, w, 160, fill="#FFFFFF")
    f.text(x + 12, 91, "视觉", size=module, weight=500, box=vision)
    f.text(x + w - 12, 91, "$o_t$", size=module, anchor="end", box=vision)
    f.image(FRAME, x + 12, 105, w - 24, 102)
    state = f.card(x, 234, w, 110, fill="#FFFFFF")
    f.text(x + 12, 262, "本体状态", size=label, box=state)
    f.text(x + w - 12, 262, "$q_t$", size=module, anchor="end", box=state)
    f.bars(
        x + 12, 280, w - 24, 34, [0.6, 0.4, 0.8, 0.3, 0.7, 0.5, 0.9, 0.35], blue.accent
    )
    f.text(
        x + 12,
        335,
        "schematic",
        size=f.fs("min"),
        color=MUTED,
        box=state,
        family="serif",
        italic=True,
    )
    instruction = f.card(x, 354, w, 94, fill="#FFFFFF")
    f.text(x + 12, 382, "任务 $\\ell$", size=module, box=instruction)
    f.bubble(
        x + 16,
        395,
        w - 28,
        36,
        "去房间取物",
        size=label,
        family="sans",
        italic=False,
        tail="none",
    )
    history = f.card(x, 458, w, 138, fill="#FFFFFF")
    f.text(x + 12, 486, "历史 $h_t$", size=module, box=history)
    for i, (tx, tw) in enumerate(f.cols(x + 12, x + w - 12, 2, gap=8)):
        f.chip(
            tx, 499, tw, 36, f"$a_{{t-{2 - i}}}$", "gray", size=label, fill="#FFFFFF"
        )
        f.image(FRAME, tx, 545, tw, 39)

    f.text(
        xs[1] + widths[1] - 14,
        42,
        "示意",
        size=f.fs("min"),
        color=MUTED,
        anchor="end",
        box=panels[1],
    )

    # System 2: symbolic parameter tensor, transformer layers and planned subgoals.
    x, w = xs[1] + 12, widths[1] - 24
    s2 = f.card(x, 64, w, 236, "amber")
    f.text(x + 14, 95, "System 2", size=title, weight=500, color=amber.deep, box=s2)
    f.text(x + 208, 95, "$g_t=f_\\theta(c_t,\\ell)$", size=module, box=s2)
    f.tokens(x + 14, 116, 6, "amber", w=22, h=12, gap=5)
    f.layer_stack(x + 14, 145, 172, 104, 4, "amber", "Transformer", size=label)
    f.vector(x + 14, 270, 12, "amber", cell=11, gap=3, vertical=False)
    f.token_grid(x + 208, 123, 4, 6, "amber", cell=15, gap=2)
    f.text(x + 330, 159, "$\\theta$", size=hero, box=s2)
    goals = []
    for index, (gx, gw) in enumerate(f.cols(x + 208, x + w - 14, 3, gap=12)):
        goals.append(
            f.chip(
                gx,
                216,
                gw,
                46,
                f"$g_{index + 1}$",
                "amber",
                size=module,
                fill="#FFFFFF",
            )
        )
    for a, b in pairwise(goals):
        f.connect(a, b, head=6)
    f.text(x + 208, 284, "规划 · 恢复", size=label, color=MUTED, box=s2)

    # System 1: compact policy graph, parameter vector, action chunk and trajectories.
    s1 = f.card(x, 370, w, 226, "blue")
    f.text(x + 14, 402, "System 1", size=title, weight=500, color=blue.deep, box=s1)
    f.text(x + 208, 402, "$A_t=\\pi_\\phi(o_t,q_t,g_t)$", size=module, box=s1)
    f.mlp(x + 14, 432, 172, 86, (3, 5, 5, 3), "blue", r=5, fill=None)
    f.token_grid(x + 14, 544, 2, 7, "blue", cell=11, gap=2)
    f.text(x + 116, 565, "$\\phi$", size=hero, color=blue.deep, box=s1)
    f.tokens(x + 208, 432, 6, "blue", w=31, h=13, gap=6)
    f.card(x + 208, 462, w - 222, 76, fill="#FFFFFF", stroke=blue.mid, kind="thumb")
    f.curves(
        x + 220,
        471,
        w - 246,
        56,
        [blue.accent, purple.accent, "#A3A09A"],
        seed=1.7,
        grid=False,
    )
    f.text(x + 208, 575, "$A_t\\in\\mathbb{R}^{H\\times d_a}$", size=module, box=s1)
    f.connect(
        s2,
        s1,
        sides=("bottom", "top"),
        ta=0.28,
        tb=0.28,
    )
    f.pill(xs[1] + 12 + (widths[1] - 24) * 0.28, 335, "$g_t$", size=label, h=40)
    f.connect(
        s1,
        s2,
        sides=("top", "bottom"),
        ta=0.82,
        tb=0.82,
        dashed=True,
        label="异常",
        label_family="sans",
        label_size=label,
        knockout=True,
    )

    # Runtime: state packet, task state machine and two independently routed APIs.
    x, w = xs[2] + 12, widths[2] - 24
    context = f.card(x, 64, w, 144, fill="#FFFFFF")
    f.text(x + 14, 95, "上下文 $c_t$", size=module, weight=500, box=context)
    f.bracket(x + 14, 112, w - 28, 42)
    f.text(
        x + w / 2,
        141,
        "$o_t,\\;q_t,\\;h_t,\\;m_t$",
        size=title,
        anchor="middle",
        box=context,
    )
    f.text(x + 14, 183, "观测 · 进度", size=label, color=MUTED, box=context)
    manager = f.card(x, 226, w, 164, fill="#FFFFFF", key=True)
    f.text(x + 14, 257, "执行管理", size=module, weight=500, box=manager)
    phases = []
    for (px, pw), name in zip(
        f.cols(x + 14, x + w - 14, 3, gap=12), ("ready", "run", "check"), strict=True
    ):
        phases.append(f.chip(px, 280, pw, 40, name, "gray", size=label, family="mono"))
    for a, b in pairwise(phases):
        f.connect(a, b, head=6)
    f.chip(
        x + 14,
        342,
        w - 28,
        34,
        "timeout → recover",
        "gray",
        size=label,
        family="mono",
        fill="#FFFFFF",
    )
    interface = f.card(x, 408, w, 188, fill="#FFFFFF")
    f.text(x + 14, 439, "接口与反馈", size=module, weight=500, box=interface)
    for (px, pw), name, symbol in zip(
        f.cols(x + 14, x + w - 14, 2, gap=14),
        ("Nav", "Control"),
        ("$x_g$", "$a_t$"),
        strict=True,
    ):
        port = f.card(px, 458, pw, 72, "purple")
        f.text(px + pw / 2, 485, name, size=label, anchor="middle", box=port)
        f.text(px + pw / 2, 516, symbol, size=module, anchor="middle", box=port)
    f.text(x + 14, 574, "时间同步", size=label, color=MUTED, box=interface)
    f.connect(context, manager, sides=("bottom", "top"), head=6)
    f.connect(manager, interface, sides=("bottom", "top"), head=6)

    # Robotics: a schematic occupancy map, a kinematic relation and a real simulation still.
    x, w = xs[3] + 12, widths[3] - 36
    navigation = f.card(x, 64, w, 176, fill="#FFFFFF")
    f.text(x + 14, 95, "SLAM · Navigation", size=module, weight=500, box=navigation)
    f.card(x + 14, 111, 142, 94, fill="#FAFAF8", stroke=HAIR, kind="thumb")
    for col in range(1, 7):
        f.line(f"M{x + 14 + col * 20} 112V204", "#E8E7E3", 0.7)
    for row in range(1, 5):
        f.line(f"M{x + 15} {111 + row * 18}H{x + 155}", "#E8E7E3", 0.7)
    for dx, dy, ow, oh in ((48, 20, 20, 38), (88, 56, 30, 18)):
        f.add(
            f'<rect x="{x + 14 + dx}" y="{111 + dy}" width="{ow}" height="{oh}" fill="#B6B5B0"/>'
        )
    f.line(
        f"M{x + 28} 190L{x + 46} 170L{x + 46} 124L{x + 94} 124L{x + 144} 147",
        blue.accent,
        2,
    )
    f.dot(x + 28, 190, blue.deep, 4)
    f.add(
        f'<circle cx="{x + 144}" cy="147" r="5" fill="white" stroke="{blue.deep}" stroke-width="1.5"/>'
    )
    f.text(x + 170, 137, "全局规划", size=label, box=navigation)
    f.text(x + 170, 173, "局部避障", size=label, box=navigation)
    f.text(
        x + 14,
        228,
        "$x_t,m_t,x_g\\rightarrow p_t$",
        size=label,
        color=MUTED,
        box=navigation,
    )
    control = f.card(x, 258, w, 160, "purple")
    f.text(
        x + 14, 289, "运动控制", size=module, weight=500, color=purple.deep, box=control
    )
    for (cx, cw), name, law, color in zip(
        f.cols(x + 14, x + w - 14, 2, gap=12),
        ("底盘", "机械臂"),
        ("$K(p_t,q_t)$", "$q^*=\\mathrm{IK}(T^*)$"),
        (blue.accent, purple.accent),
        strict=True,
    ):
        servo = f.card(cx, 303, cw, 101, fill="#FFFFFF", stroke=purple.mid)
        f.text(cx + cw / 2, 327, name, size=label, anchor="middle", box=servo)
        f.text(cx + cw / 2, 356, law, size=label, anchor="middle", box=servo)
        f.curves(cx + 10, 374, cw - 20, 19, [color], seed=0.3, grid=False)
    robot = f.card(x, 436, w, 160, fill="#FFFFFF")
    f.text(x + 14, 467, "Robot · sensors", size=module, weight=500, box=robot)
    f.image(FRAME, x + 14, 479, 128, 92)
    f.vector(x + 162, 489, 7, "blue", cell=12, gap=2, vertical=False)
    f.text(x + 162, 542, "$q_{t+1}$", size=title, box=robot)
    f.text(x + 14, 589, "仿真示例", size=f.fs("min"), color=MUTED, box=robot)
    f.text(x + 162, 577, "反馈", size=label, color=MUTED, box=robot)
    f.connect(navigation, control, sides=("bottom", "top"), ta=0.25, tb=0.25, head=6)
    f.connect(control, robot, sides=("bottom", "top"), head=6)
    f.bus(
        robot,
        [navigation, control],
        side="right",
        face="right",
        at=xs[3] + widths[3] - 12,
        color=green.deep,
        sw=1.6,
        head=6,
    )

    # Collect the observation modalities, then make the decision and feedback paths explicit.
    f.brace(xs[0] + widths[0] + 2, 64, 596, color=MUTED, depth=10)
    bundle = f.zone(xs[0] + widths[0] + 11, 329, 2, 2)
    f.bus(bundle, [s2, s1], side="right", at=xs[1] - 5, color=WIRE, head=6)
    f.connect(s2, manager, sides=("right", "left"), ta=0.87, tb=0.25)
    f.connect(s1, manager, sides=("right", "left"), ta=0.20, tb=0.75)
    f.connect(
        context, s2, sides=("left", "right"), tb=None, color=green.deep, dashed=True
    )
    f.bus(
        interface, [navigation, control], side="right", at=xs[3] - 12, ta=0.65, head=6
    )
    f.route(
        robot,
        interface,
        (638,),
        sides=("bottom", "bottom"),
        ta=0.75,
        tb=0.8,
        color=green.deep,
        sw=1.8,
        label="观测与执行结果",
        label_family="sans",
        label_size=label,
        knockout=True,
    )
    f.route(
        interface,
        s1,
        (674,),
        sides=("bottom", "bottom"),
        ta=0.2,
        tb=0.5,
        color=green.deep,
        sw=1.8,
        label="状态与异常反馈",
        label_family="sans",
        label_size=label,
        knockout=True,
    )
    f.save(str(OUT))
    print(OUT)


if __name__ == "__main__":
    draw()
