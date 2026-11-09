---
title: SuperMimic 的可微世界模型方法，及其在 Apple Silicon 上的实现
description: 介绍 SuperMimic 通过学习到的可微世界模型、H 步想象展开与 critic 自举训练全身控制策略的方法，并说明 MacMimic 在 Apple Silicon 上的系统设计：CPU 上的 MuJoCo 线程池采样、Metal 上的 torch.compile 学习，以及仓库中的实测数据。
date: 2026-11-04
series: notes
tags: [MacMimic, SuperMimic, 全身控制, 世界模型, Apple Silicon, 人形机器人]
cover: ./cover.jpg
coverAlt: MacMimic的运行方式框图，物理在CPU，学习在Metal
platforms: [xiaohongshu]
links:
  - label: Liao et al. (2026). SuperMimic - Scaling Humanoid Whole-Body Control with One Differentiable World Model.
    url: https://arxiv.org/abs/2610.28480
    note: CoRL 2026
  - label: Xu et al. (2022). Accelerated Policy Learning with Parallel Differentiable Simulation.
    url: https://arxiv.org/abs/2204.07137
    note: arXiv，SHAC
  - label: Schulman et al. (2015). High-Dimensional Continuous Control Using Generalized Advantage Estimation.
    url: https://arxiv.org/abs/1506.02438
    note: arXiv
  - label: Schulman et al. (2017). Proximal Policy Optimization Algorithms.
    url: https://arxiv.org/abs/1707.06347
    note: arXiv
  - label: Liao et al. (2025). BeyondMimic - From Motion Tracking to Versatile Humanoid Control via Guided Diffusion.
    url: https://arxiv.org/abs/2508.08241
    note: arXiv
  - label: Luo et al. (2025). SONIC - Supersizing Motion Tracking for Natural Humanoid Whole-Body Control.
    url: https://arxiv.org/abs/2511.07820
    note: arXiv
  - label: Harvey et al. (2020). Robust Motion In-betweening.
    url: https://arxiv.org/abs/2102.04942
    note: SIGGRAPH 2020，LAFAN1 数据集的来源
  - label: MuJoCo documentation. Python bindings - mujoco.rollout.
    url: https://mujoco.readthedocs.io/en/stable/python.html
    note: 官方文档
  - label: PyTorch documentation. torch.compile.
    url: https://docs.pytorch.org/docs/stable/generated/torch.compile.html
    note: 官方文档
  - label: yusenthebot. MacMimic.
    url: https://github.com/yusenthebot/macmimic
    note: 代码与报告，MIT
---

人形机器人的全身控制（Whole-Body Control，WBC）需要策略跟踪大量人类动作，并在接触频繁切换的情况下保持平衡。主流做法是用近端策略优化（Proximal Policy Optimization，PPO）在大规模并行仿真中训练，对应的算力开销很高。[SuperMimic](https://arxiv.org/abs/2610.28480) 换用了一个学习到的可微世界模型，让策略在模型内部“想象”若干步，并把回报的梯度直接沿模型传回策略。MacMimic 是在 Apple Silicon 上对这一方法的实现，物理仿真运行在 CPU，学习运行在 Metal。

本文先用公式说明 SuperMimic 的方法，再说明 MacMimic 的系统设计，最后给出仓库中记录的测量数据。方法部分的公式取自论文，符号做了适当简化；数据部分来自 MacMimic 仓库的报告与 `docs/results/` 下的原始记录。

## 问题设定与记号

任务是目标条件的部分可观测马尔可夫决策过程。状态 $s_t$ 给出本体感受观测 $o_t$ 与终止标志 $d_t$，目标 $g_t$ 在动作跟踪中读取自参考动作。策略是确定性的，

$$
a_t=\pi_\theta(o_t,g_t),
$$

其中 $a_t$ 参数化归一化的关节设定点。采集数据时，仿真器执行带噪声的动作 $a_t+\epsilon_t$，$\epsilon_t\sim\rho_\epsilon$，回放缓冲区 $\mathcal{B}$ 记录实际执行的动作。观测分解为 $o_t=\bar{o}_t+\eta_t$，其中 $\bar{o}_t$ 是无噪声观测，$\eta_t\sim\rho_\eta$ 是已知分布的传感器噪声。回报使用软存活权重，

$$
c_0=1,\qquad c_{t+1}=c_t\,(1-d_{t+1}),\qquad J(\theta)=\mathbb{E}\Bigl[\sum_{t\ge 0}\gamma^t c_t\, r_{t+1}\Bigr],
$$

其中 $r_{t+1}$ 是奖励，$\gamma\in[0,1)$ 是折扣因子。动作跟踪的奖励采用 [BeyondMimic](https://arxiv.org/abs/2508.08241) 的跟踪奖励，去掉自碰撞惩罚。

## SuperMimic 的方法

### 每次迭代的三个步骤

SuperMimic 不分阶段训练，每次迭代依次执行三步：用当前策略在仿真器中采集转移并写入回放缓冲区；用缓冲区中的片段拟合世界模型；冻结世界模型的权重，让策略在模型中想象展开并更新。动力学与采集数据的策略无关，因此旧策略采到的数据对拟合动力学仍然有效，回放缓冲区可以持续复用。

### 世界模型与它的拟合

仿真器中的随机性来源是已知的：每个回合的仿真上下文 $\xi$（摩擦系数、标定偏置、躯干质心位置）、传感器噪声 $\eta_t$ 与动作噪声 $\epsilon_t$。因此世界模型保持确定性，以 $\xi$ 为条件，预测无噪声观测，传感器噪声在模型之外再加回去。模型由动力学网络与奖励、观测、终止三个头组成：

$$
\hat{s}_{t+1}=f_\omega(\hat{s}_t,a_t,\xi),\quad
\hat{r}_{t+1}=r_\omega(\hat{s}_t,a_t,g_t),\quad
\hat{\bar{o}}_t=h_\omega(\hat{s}_t,\xi),\quad
\hat{d}_t=d_\omega(\hat{s}_t,g_t).
$$

每个头可以是学习得到的，也可以由解析公式计算；解析头没有损失项。拟合在缓冲区的 $k$ 步窗口上进行（$k=8$）：从记录的状态 $\hat{s}_0=s_0$ 出发，按记录的动作自回归地向前展开，最小化

$$
\mathcal{L}_{\mathrm{WM}}(\omega)=\mathbb{E}_{\mathcal{B}}\Bigl[\sum_{j=1}^{k}\|\hat{s}_j-s_j\|^2+(\hat{r}_j-r_j)^2+\|\hat{\bar{o}}_j-\bar{o}_j\|^2+\operatorname{BCE}(\hat{d}_j,d_j)\Bigr],
$$

其中 $s_j,r_j,\bar{o}_j,d_j$ 为仿真器记录的量，$\operatorname{BCE}$ 是二元交叉熵。自回归地训练 $k$ 步，使模型学会纠正自身的累积误差，因此在策略更新中展开比 $k$ 更长的 $H$ 步仍然稳定。

终止概率 $\hat{d}_t\in[0,1]$ 使存活权重 $\hat{c}_{t+1}=\hat{c}_t(1-\hat{d}_{t+1})$ 在想象轨迹中保持可微，因此摔倒也能提供梯度。

### H 步想象展开与梯度

策略更新时固定 $\omega$，从缓冲区采样起点 $s_0$ 及其记录的 $\xi$，在模型中展开 $H=32$ 步。第 $t$ 步，模型输出 $\hat{\bar{o}}_t$，加回传感器噪声后由策略决定动作：$a_t=\pi_\theta(\hat{\bar{o}}_t+\eta_t,g_t)$。策略的目标为

$$
\hat{J}(\theta)=\mathbb{E}_{s_0\sim\rho_0,\ \pi_\theta}\Bigl[\sum_{t=0}^{H-1}\gamma^t\,\hat{c}_t\,\hat{r}_{t+1}+\gamma^{H}\,\hat{c}_H\,V_\psi(\hat{s}_H,g_H,\xi)\Bigr].
$$

右端第二项是在视距 $H$ 处用 critic $V_\psi$ 对其后回报的自举（bootstrap）。由于整个展开都可微，一阶梯度 $\nabla_\theta\hat{J}$ 通过时间反向传播（Backpropagation Through Time，BPTT）穿过世界模型对状态与动作的雅可比矩阵得到，更新为 $\theta\leftarrow\theta+\alpha_\theta\nabla_\theta\hat{J}$。冻结权重 $\omega$ 只表示不更新参数，模型对输入的求导仍然保留。

与 [PPO](https://arxiv.org/abs/1707.06347) 的区别在于梯度的类型。PPO 把动力学当作黑盒，用随机策略的得分函数 $\nabla_\theta\log\pi_\theta$ 乘以采样动作的优势，得到似然比估计；BPTT 则直接对每个动作求回报的导数，在短视距上方差低得多。这一思路与 [SHAC](https://arxiv.org/abs/2204.07137) 的短视距 actor-critic 一致，差别是 SHAC 对可微仿真器求导，SuperMimic 对学习得到的模型求导，所以真正的仿真器（这里是 MuJoCo）无需可微，也不要求接触光滑。

### Critic 与 H 步之外

critic 用想象轨迹上的广义优势估计（Generalized Advantage Estimation，[GAE](https://arxiv.org/abs/1506.02438)）回报拟合：

$$
\hat{R}_t=\hat{r}_{t+1}+\gamma\,(1-\hat{d}_{t+1})\bigl[(1-\lambda)V_{t+1}+\lambda\hat{R}_{t+1}\bigr],\qquad \hat{R}_H=V_H,
$$

$$
\mathcal{L}_V(\psi)=\mathbb{E}\Bigl[\sum_{t=0}^{H-1}\bigl(V_t-\hat{R}_t\bigr)^2\Bigr],\qquad V_t=V_\psi(\hat{s}_t,g_t,\xi).
$$

其中 $\lambda$ 是 GAE 的衰减参数，目标 $\hat{R}_t$ 每个展开只计算一次并在拟合 $\psi$ 时保持固定。没有 critic 的目标只优化 $H$ 步奖励之和，更加短视。论文报告去掉 critic 后 $H\le 16$ 的训练失败；在相同回报下，有 critic 的策略在仿真中被以 0.5 到 4 m/s 推动后能在 0.5 到 2.4 秒内站稳，无 critic 的策略在 4 m/s 时摔倒。

### 算法

1. 采集：用带动作噪声的 $\pi_\theta$ 在仿真中运行，把转移写入 $\mathcal{B}$，新数据替换最旧的数据。
2. 拟合世界模型：从 $\mathcal{B}$ 采样 $k=8$ 步窗口，自回归展开并最小化 $\mathcal{L}_{\mathrm{WM}}$。
3. 想象：冻结 $\omega$，从 $\mathcal{B}$ 采样起点，在模型中按策略展开 $H=32$ 步，计算 $\hat{J}(\theta)$。
4. 更新策略：沿 $\nabla_\theta\hat{J}$ 更新 $\theta$。
5. 更新 critic：用 GAE 目标拟合 $V_\psi$。
6. 回到第 1 步。

### 论文报告的结果

论文报告单张 H100 训练 3 小时，回报超过 [SONIC](https://arxiv.org/abs/2511.07820) 在 128 张 L40 上训练 7 天的公开策略；在 129,514 条动作上失败 25 条，两张 H100 训练 9.8 小时后失败 0 条。这些评测动作都是训练动作，衡量的是覆盖度，而不是对新动作的泛化。以上为论文自述的数字，本文没有复现。

## MacMimic 的系统设计

论文的物理仿真运行在 GPU 的 MuJoCo Warp 上，依赖 CUDA，Apple Silicon 上没有对应的路径。MacMimic 把系统拆成两部分，物理放在 CPU，学习放在 Metal，两者之间只保留一个窄接口。

![MacMimic 的运行方式：物理在 CPU，学习在 Metal，每个控制步交换一次](./fig-pipeline.png "MacMimic 在 Apple Silicon 上的运行方式。(a) 物理在 CPU，MuJoCo 的 C++线程池推进 2048 个环境。(b) 学习在 Metal，状态进回放缓冲，world model 拟合后冻结，策略在其中想象 32 步，梯度经 world model 传回策略。(c) 一台 M5 Max 从零训练 97.6 分钟，40 段动作全部完成；同一个 256 环境基准下，单次迭代从 CPU eager 的 10,567 ms 降到 272 ms。两端每个控制步只交换一次数据，64 GB 统一内存让这次交换只是内存内拷贝，不走 PCIe。")

### CPU：MuJoCo 的 C++ 线程池

物理由 MuJoCo 提供的 [`mujoco.rollout`](https://mujoco.readthedocs.io/en/stable/python.html) 完成。按官方文档，当传入多个 `MjData` 时，各条轨迹在内部管理的线程池上并行；`persistent_pool=True` 或 `Rollout` 对象可以复用同一个线程池，且 GIL 在调用期间被释放。MacMimic 使用持久的 `Rollout(nthread=8)`，一次调用推进全部环境。训练配置为 2048 个环境。

控制周期为 20 ms，每个控制步在 C++ 内运行 4 个 5 ms 的物理子步（仓库中常量记为 `DECIMATION`）。动作先换算为关节设定点

$$
q^{\mathrm{target}}=q^{\mathrm{default}}+\alpha\,a,
$$

其中 $q^{\mathrm{default}}$ 是默认关节角，$\alpha$ 是缩放系数。设定点在 4 个子步中保持不变；隐式 PD 控制器在每个子步更新，并保留电机力矩限幅，全部在 C++ 内完成，Python 不进入内层循环。每次调用之后，代码检查输出状态是否有限、时间戳是否与期望一致，若某个世界发散或被自动重置，就抛出异常并拒绝这次转移，而不是把坏数据写入缓冲区。

### Metal：torch.compile

学习部分在 PyTorch 的 MPS（Metal Performance Shaders）设备上运行，使用 [`torch.compile`](https://docs.pytorch.org/docs/stable/generated/torch.compile.html) 的默认后端 Inductor，把世界模型、想象步、奖励、观测和 critic 编译成融合的 Metal 内核。融合的意义在于减少内核启动次数和中间张量的读写，而想象展开恰好由大量短小的逐元素运算与小矩阵乘法构成。

### 每个控制步的数据交换

接口在每个 20 ms 控制步上只交换一次：策略在 GPU 上产生动作，换算为设定点后拷贝到 CPU；线程池推进 4 个子步，返回新的完整物理状态（双精度，同一缓冲区复用）；状态回到 GPU 计算奖励、终止并写入回放缓冲区。Apple Silicon 的 64 GB 统一内存使这次交换只是内存内拷贝，不经过 PCIe 总线。

### 按单机缩放的模型

| 项 | 论文 | MacMimic |
| --- | --- | --- |
| 物理 | MuJoCo Warp（GPU）| MuJoCo 3.16 C++ 线程池（CPU，8 线程）|
| 数据 | BONES-SEED 129,514 条，264 h | LAFAN1 40 条，2.45 h |
| 世界模型 | MLP 2048×3 | MLP 512×3，结构化 |
| 策略编码器与解码器 | 2048-1024-512-256 | 512-256-128 |
| 环境数与想象批量 | 4096 / 4096 | 512 到 2048 / 512 到 1024 |
| 优化器 | Adam | Muon（隐藏层矩阵）与 Adam |
| 新增 | 无 | 参考 PD 残差动作、左右镜像增广、策略 EMA、失败前专项重置 |
| 关闭 | 无 | 域随机化、自碰撞 |

训练数据 LAFAN1 来自 [Harvey et al. (2020)](https://arxiv.org/abs/2102.04942)。其中最重要的两项改动是结构化世界模型与参考 PD 残差。结构化世界模型让网络预测速度增量，位置由新旧速度按半隐式积分推出，网络只学一个较小的位置修正。参考 PD 残差把动作定义为“下一帧参考关节角对应的设定点加网络输出”；只靠参考 PD 跟踪在完整协议下是 0/40、补零回报 0.003，所以策略学到的部分是真实贡献。

## 测量结果

### 吞吐

下表来自 `docs/results/throughput.json`，协议为：256 个环境、世界模型与策略批量 256、4 个 Torch CPU 线程与 8 个仿真线程、每组 4 次迭代剔除第 1 次后取 3 个样本，包含采集、5 次 8 步世界模型拟合、32 步想象与 critic。

| 阶段 | CPU eager (ms) | MPS + Inductor (ms) |
| --- | --- | --- |
| 物理采集 | 35.1 | 70.7 |
| 世界模型拟合 | 9432.3 | 74.2 |
| 策略与 critic | 943.2 | 125.4 |
| 单次迭代合计 | 10567.2 | 271.8 |

整次迭代的吞吐比为 $10567.2/271.8\approx 38.9$。切到 Metal 之后，三个阶段的耗时接近均衡，C++ 线程池不再是瓶颈。这一数字是吞吐对比，不是收敛时间的加速比，也不是跨硬件的排名。

### 收敛

验收标准在训练前固定：每条动作从第 0 帧完整运行到结尾，关闭噪声与随机化，失败后的剩余时长按零回报计；要求 40/40 完成且平均补零回报不低于 0.82，并在三个相隔 250 次更新的检查点上连续保持。

| 检查点（更新次数）| 完整动作 | 补零回报 | 累计训练时间 |
| --- | --- | --- | --- |
| 10,250 | 40/40 | 0.8297 | 91.67 分钟 |
| 10,500 | 40/40 | 0.8298 | 94.61 分钟 |
| 10,750 | 40/40 | 0.8318 | 97.59 分钟 |

最终检查点的平均身体位置 RMSE 为 3.66 cm，关节 RMSE 为 0.128 rad，全局根部距离误差为 0.82 m。独立重跑完整评估，40 条动作的逐动作指标完全一致。97.59 分钟是所选分支的累计训练计时，包含进程内的预热与编译；六条主训练试验去重后合计 152.81 分钟。两者都不包含数据准备、评估、渲染和工程开发时间。

训练分阶段进行，每次续训只改变一两个变量：先以 512 个环境快速爬升，随后加大策略批量并降低接触奖励系数与学习率，再把物理环境从 512 扩到 2048，最后对三条历史失败动作失败前 10 秒的区间做 15% 的专项重置。这是经过试验选择的分阶段配方，默认的一条训练命令没有被验证能从零达到相同结果。

### 局限

这是 40 条训练动作上的 G1 仿真结果，单随机种子，不是论文 129,514 条动作的复现，不涉及对新动作的泛化，也没有实机验证。域随机化与自碰撞被关闭，每个控制周期清零 MuJoCo 求解器的 warmstart，观测中没有根部全局位置反馈，所以长动作会漂移（平均 0.82 m）。仓库的搬箱试验显示，冻结的 WBC 配合独立的双臂控制可以把 0.5 kg 的箱子搬运 2.89 m，但严格持续接触标准的通过数为 0/9，说明物体交互仍是未解决的部分。

## 小结

SuperMimic 的核心是三点：用一个确定性的可微世界模型摊销整个动作库；在模型中展开 $H$ 步并用一阶梯度更新策略；用 critic 在视距处自举。MacMimic 说明这套方法对硬件的要求主要是“一个能高效批量运行的物理仿真”和“一个能编译小网络的加速器”，在统一内存的 Apple Silicon 上，把物理放在 CPU、学习放在 Metal 可以在约 98 分钟的累计训练内完成 40 条训练动作的验收。仍然开放的问题包括：多随机种子下的稳定性、对未见动作的泛化、域随机化与自碰撞开启后的表现，以及地形与物体交互。
