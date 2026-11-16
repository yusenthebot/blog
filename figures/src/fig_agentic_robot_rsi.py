"""Robot deployment, experience, model-driven improvement and validation.

All samples, network glyphs and task representations are schematic.
"""

from pathlib import Path

from figkit import HAIR, MUTED, PAL, WIRE, Fig

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "agentic_robot_rsi-figure.svg"


def draw() -> None:
    """Build the four stages and their two feedback paths."""
    f = Fig(1400, 586)
    small, label, module, title = (
        f.fs(role) for role in ("min", "label", "module", "title")
    )
    amber, blue, gray, green = (
        PAL[role] for role in ("amber", "blue", "gray", "green")
    )
    stages = zip(
        f.place(8, 1392, (248, 250, 566, 284), gap=12),
        (248, 250, 566, 284),
        ("(a) 稳定部署", "(b) 部署经验", "(c) RSI harness", "(d) 验证与更新"),
        ("gray", "gray", "amber", "green"),
        strict=True,
    )
    for x, w, heading, role in stages:
        f.panel(x, 8, w, 525, role, heading, title_size=title)

    # (a) The robot closes the deployed runtime loop with reported state.
    runtime = f.card(20, 69, 224, 144, "blue")
    f.text(34, 97, "机器人运行", size=module, weight=500, box=runtime)
    f.chip(34, 115, 194, 38, "模型 · runtime", "blue", fill="#FFFFFF")
    f.chip(34, 163, 194, 37, r"部署技能 $\mathcal{S}_k$", "blue")

    robot = f.card(20, 269, 224, 250, fill="#FFFFFF", stroke=HAIR)
    f.text(34, 297, "真实任务", size=module, weight=500, box=robot)
    f.asset(
        HERE / "assets" / "agentic-robot" / "robot.svg",
        87,
        324,
        90,
        color=gray.deep,
        sw=2.2,
    )
    f.chip(35, 433, 194, 38, r"动作 $a_t$", "blue", fill="#FFFFFF")
    f.text(132, 500, r"反馈 $(s_{t+1},r_t)$", size=label, anchor="middle", box=robot)
    f.connect(runtime, robot, sides=("bottom", "top"), ta=0.32, tb=0.32)
    f.connect(
        robot,
        runtime,
        sides=("top", "bottom"),
        ta=0.68,
        tb=0.68,
        color=blue.deep,
        dashed=True,
    )

    # (b) A synchronised state/action/result trace is converted into experience.
    trace = f.card(280, 69, 226, 241, fill="#FFFFFF", stroke=HAIR)
    f.text(294, 97, "运行记录", size=module, weight=500, box=trace)
    f.text(492, 97, "示意", size=small, color=MUTED, anchor="end", box=trace)
    f.text(296, 136, r"$s_t$", size=label, box=trace)
    f.text(296, 189, r"$a_t$", size=label, box=trace)
    f.text(296, 243, r"$r_t$", size=label, box=trace)
    f.curves(333, 111, 155, 33, (gray.deep, gray.accent), seed=0.8, grid=True)
    f.curves(333, 164, 155, 33, (blue.accent, blue.deep), seed=1.6, grid=True)
    f.token_grid(
        333,
        224,
        1,
        7,
        "gray",
        cell=17,
        gap=6,
        values=[0.15, 0.3, 0.25, 0.85, 0.7, 0.45, 0.2],
    )
    f.text(393, 287, "状态 · 动作 · 结果", size=label, anchor="middle", box=trace)

    experience = f.cylinder(280, 340, 226, 179, "gray")
    f.text(
        393,
        380,
        r"经验集 $\mathcal{D}_k$",
        size=module,
        weight=500,
        anchor="middle",
        box=experience,
    )
    for x, role, name in (
        (294, "amber", "失败"),
        (361, "blue", "纠正"),
        (428, "green", "新任务"),
    ):
        f.chip(x, 403, 64, 37, name, role, size=small, fill="#FFFFFF")
        grid_width = 3 * 11 + 2 * 4
        f.token_grid(x + (64 - grid_width) / 2, 455, 3, 3, role, cell=11, gap=4)
    f.route(robot, trace, (262,), sides=("right", "left"), ta=0.19, tb=0.63)
    f.connect(trace, experience, sides=("bottom", "top"))

    # (c) Motor-policy distillation and model-driven code changes are parallel
    # candidate-generation options. Network symbols carry no architecture sizes.
    harness = f.card(542, 69, 542, 329, "amber", key=True)
    f.text(556, 97, "模型改进", size=module, weight=500, box=harness)
    f.text(1070, 97, "示意", size=small, color=MUTED, anchor="end", box=harness)

    distill = f.card(556, 112, 514, 152, "blue", fill="#F7FCFD")
    f.text(
        570,
        140,
        r"教师运动策略 $\pi_{\Theta}$",
        size=label,
        color=blue.deep,
        box=distill,
    )
    f.text(
        1056,
        140,
        r"轻量策略 $\pi_{\phi}$",
        size=label,
        color=blue.deep,
        anchor="end",
        box=distill,
    )
    teacher = f.layer_stack(580, 147, 157, 105, 4, "blue", depth=8)
    f.token_grid(597, 183, 3, 5, "blue", cell=13, gap=4)
    student = f.mlp(927, 179, 112, 62, (3, 4, 2), "blue", r=5)
    f.connect(teacher, student, ta=0.48, tb=None, color=blue.deep)
    f.text(
        827,
        197,
        "策略蒸馏",
        size=label,
        anchor="middle",
        color=blue.deep,
        box=distill,
    )

    code = f.example(556, 280, 514, 105, "amber", fill="#FFFCF4")
    f.text(570, 309, "智能体 · 技能代码迭代", size=label, color=amber.deep, box=code)
    f.text(574, 351, "− grasp()", size=label, family="mono", color=MUTED, box=code)
    f.text(
        806,
        351,
        "+ align(); grasp()",
        size=label,
        family="mono",
        color=amber.deep,
        box=code,
    )

    candidate = f.card(542, 429, 542, 90, "blue")
    f.text(556, 457, "候选技能", size=module, weight=500, box=candidate)
    f.text(
        1070,
        456,
        r"$\tilde{\mathcal{S}}_{k+1}$",
        size=label,
        color=blue.deep,
        anchor="end",
        box=candidate,
    )
    f.line("M813 466V507", blue.mid, 1)
    f.vector(560, 482, 6, "blue", vertical=False, cell=10, gap=3)
    f.text(
        654,
        493,
        r"$\phi_k \ \to \ \tilde{\phi}_{k+1}$",
        size=label,
        color=blue.deep,
        box=candidate,
    )
    f.token_grid(879, 482, 1, 5, "amber", cell=10, gap=3)
    f.text(
        964,
        493,
        r"$\Delta c$",
        size=label,
        color=amber.deep,
        box=candidate,
    )
    f.connect(experience, harness, ta=0.20, tb=None, color=WIRE)
    f.connect(harness, candidate, sides=("bottom", "top"))

    # (d) A release gate checks both task sets, then stores the accepted version.
    validate = f.card(1120, 69, 260, 249, "green")
    f.text(1134, 97, "回归验证", size=module, weight=500, box=validate)
    for y, name, symbol in (
        (114, "已有任务", r"$\mathcal{T}_{\mathrm{old}}$"),
        (183, "新任务", r"$\mathcal{T}_{\mathrm{new}}$"),
    ):
        row = f.card(1134, y, 232, 56, fill="#FFFFFF", stroke=green.mid, kind="chip")
        f.text(1146, y + 22, name, size=label, box=row)
        f.text(1354, y + 22, symbol, size=label, anchor="end", box=row)
        f.token_grid(1146, y + 34, 1, 7, "green", cell=10, gap=4)
    f.chip(1134, 252, 232, 42, "门槛", "green", size=label)

    library = f.card(1120, 374, 260, 145, "green")
    f.text(1134, 402, "版本化技能库", size=module, weight=500, box=library)
    previous = f.chip(1134, 420, 102, 40, r"$\mathcal{S}_k$", "green", fill="#FFFFFF")
    accepted = f.chip(1264, 420, 102, 40, r"$\mathcal{S}_{k+1}$", "green")
    f.connect(previous, accepted, color=green.deep)
    f.text(1250, 496, "可追溯 · 可回退", size=label, anchor="middle", box=library)

    f.route(candidate, validate, (1102,), sides=("right", "left"), tb=0.64)
    f.connect(
        validate,
        library,
        sides=("bottom", "top"),
        color=green.deep,
        label="通过",
        label_family="sans",
        label_size=small,
        knockout=True,
    )
    f.route(
        validate,
        harness,
        (53,),
        sides=("top", "top"),
        ta=0.40,
        tb=0.82,
        color=amber.deep,
        dashed=True,
        label="未通过",
        label_family="sans",
        label_size=small,
        label_at=1048,
        knockout=True,
    )
    f.route(
        library,
        runtime,
        (560, 13),
        sides=("bottom", "left"),
        color=green.deep,
        sw=2,
        label="部署",
        label_family="sans",
        label_size=label,
        label_at=775,
        knockout=True,
    )

    f.save(str(OUT))
    print(OUT)


if __name__ == "__main__":
    draw()
