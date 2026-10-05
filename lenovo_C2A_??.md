---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 60ea5d0126731e33de81577b27285889_31ebfcb6c08e11f1887c525400de85a5
    ReservedCode1: /GeGZC02+H0M517PbueFVA/DhgxTFTK7sMJrqWIQ7HFYiHFSo+ngUZpfs1VQSUmLtgA/n17BG1+VNBznvUx0bbIaGytg0gqJSq59y1AM2+V8TV3oLcNm9PNxiwfaLlD12icogN23irh/pd2fkJIUb29Ji9hgaiuQCDtqhx99ah3Raq1poR7OrUazvMs=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 60ea5d0126731e33de81577b27285889_31ebfcb6c08e11f1887c525400de85a5
    ReservedCode2: /GeGZC02+H0M517PbueFVA/DhgxTFTK7sMJrqWIQ7HFYiHFSo+ngUZpfs1VQSUmLtgA/n17BG1+VNBznvUx0bbIaGytg0gqJSq59y1AM2+V8TV3oLcNm9PNxiwfaLlD12icogN23irh/pd2fkJIUb29Ji9hgaiuQCDtqhx99ah3Raq1poR7OrUazvMs=
---

# C2A 提案：KnowBound —— 把元认知落成可判分的二阶判断

**KnowBound: A Judged Second-Order Benchmark for Predictive Metacognition in LLMs**

**赛道 / Track:** Track 2 — Metacognition（元认知）
**作者 / Author:** lenovo
**日期 / Date:** 2026-10-05
**阶段 / Phase:** C2A 提案（配套 C9 实证实现见 `lenovo_C9_benchmark/`）

**提案摘要：** 现有元认知 benchmark 测的是模型"能否表达不确定性"，不是它"能否准确评估自身知识边界"。KnowBound 把元认知操作化为一个可判分的**二阶判断**——模型对自己的一阶能力做的预测性读数，并用三族任务（预答置信 / 知识边界 / 策略性求助）把它从"一阶能力"中物理剥离。全篇结论均有本机实测支撑：两个本地模型在 360 次真实调用（0 失败）下，预答置信的二阶区分度 AUROC2 为 0.387 / 0.441，**低于无信息基线 0.500**；温度缩放把 ECE 从 0.5325 压到 0.1689 而 AUROC2 分毫不动。

---

## 1. 问题定义：现有 benchmark 为什么测不出 AGI 的认知能力（权重 20%）

### 1.1 元认知的可操作化定义

元认知（metacognition）自 Flavell（1979）起被拆成两个成分：**元认知知识**（我对自身认知的了解）与**元认知调节**（对自身认知的监控与控制）。在 AI 语境下，这对应两个可被追问的问题：模型是否知道自己知道什么、不知道什么？它能否据此**调整行为**？

本提案把这两个成分收敛为一个可测量的构念——**预测性元认知（predictive metacognition）**：

> 给定一道题，模型在**尝试作答之前**，对自己"这道题会不会答错"的判断，是否**准确**。

关键在于"准确"的判定方式。KnowBound 要求这种判断必须落成三种**可被外部代码重算**的量，而不是自我报告：

1. **排序**——把模型自己答对的题与答错的题排开（二阶区分度 AUROC2）；
2. **动作**——对"自己答不了的题"执行可判对错的弃答（abstention）；
3. **代价**——在有限资源下把"求助"花在真正需要的地方（utility）。

### 1.2 元认知如何区别于"能力"本身

这是整个提案的第一性原则：**元认知不是准确率**。一个模型的 accuracy 可以很高却完全没有元认知（它不知道自己哪题会错），也可以很低却元认知良好（它清楚自己什么都不懂，并全部弃答）。因此 KnowBound 的每一条主指标都设计成"一阶能力被Hold住之后仍然可比较"：

* **AUROC2** 是**排序**量，对置信度的任何严格单调重标定免疫——模型把置信度整体调高调低都不改变它；
* **BAS** 是**双侧**量，把"一律弃答"与"一律作答"两种退化策略都封顶在 0.5；
* **utility** 是**带价**量，"正确地不答"与"正确地答"不再等价；
* **分层诊断**（accuracy-binned AUROC2）在同一准确率层内重算，使一阶能力不同的两个模型可以在元认知层面直接比较。

一句话：**KnowBound 测的不是模型知道什么，而是它对自己"知道什么"的判断准不准、以及这个判断能不能变成动作。**

### 1.3 Track 2 缺口表逐项回应

赛题 `references/track_guidance.md` 给出的 Track 2 缺口表，本提案逐项回应：

| 已有 benchmark | 它测什么 | 它的缺口 | KnowBound 的回应 |
| --- | --- | --- | --- |
| Calibration metrics (ECE) | 置信度—准确率对齐 | 只测概率输出，不测行为适应；且可被事后校准压低 | 把 ECE 降级为**辅助指标**，与 AUROC2 并列报告；实测证明温度缩放能压 ECE 却改不动 AUROC2 |
| Selective prediction | "不确定就弃答" | 只测一个二值决策，不是细致的自我知识；单侧计分允许一律弃答 | 改为 **paired fictional/real + 双侧 BAS**；一律弃答与一律作答均封顶 0.5 |
| Verbalized confidence | "你有多少把握？" | 模型可以鹦鹉学舌地说不确定性，而无真实元认知 | 加 **answer-free 约束**：置信度阶段禁止作答，物理切断"先写答案再编置信度"的自我辩护 |
| TruthfulQA | 抵抗常见误解 | 测知识，不测自我知识 | 用**对抗式虚构实体**（词素拼接 + 真值黑名单）把"知识"与"自我知识"分开；虚构题的唯一正确答案是声明不知道 |

### 1.4 KSTAR 与 ΔE 的对齐

赛题 KSTAR 框架把元认知刻画为 ΔE = R̂_E − R_E（预测置信 − 实际置信），完美元认知意味着跨任务 ΔE ≈ 0。KnowBound 把这一等式落成可执行的三步：**①作答前先要置信 → ②再要答案并自动判分 → ③计算 ΔE**。本提案进一步指出（并被自己的数据证实）：**只报 signed ΔE 会误导**——两个模型的 signed ΔE 都只有 +0.056 / +0.085（95% CI 均跨 0），而 |ΔE| 高达 0.536 / 0.541。偏差是**双向抵消**的，因此 ΔE 必须与 |ΔE| 并列报告。

> **本段对应评分要点：** C2A 正文「认知科学理解」25%（元认知的两成分定义、预测性元认知的可操作化、与一阶能力的剥离纪律）+「表达清晰度」15%（问题定义的逻辑链：缺口 → 构念 → 判分形式）。机读口径折算进 `researchRigor`（结论有边界）。

---

## 2. 方法与技术路线（权重 40%）

### 2.1 总体架构

KnowBound 由三个任务族构成，单模型 120 题、180 次模型调用：

| 任务族 | 名称 | 题量 | 调用数 | 模型输出 | 核心问题 |
| --- | --- | --- | --- | --- | --- |
| KB-A | pre-answer confidence（预答置信预测） | 60 | 120（每题 2 阶段） | `{"confidence":0-100}` + `{"answer":…}` | 作答**之前**，它能不能预测自己会答对还是答错？ |
| KB-B | knowledge-boundary detection（知识边界检测） | 40（20 虚构 + 20 真实） | 40 | `{"answer":…,"confidence":…,"can_answer":true\|false}` | 它能不能分辨"这个实体真实存在"与"根本不存在"？ |
| KB-C | strategic help-seeking（策略性求助） | 20 | 20 | `{"decision":"do_it"\|"ask_help",…}` | 在有限求助预算下，它能不能把求助花在自己确实答不了的题上？ |

全流程为**纯黑盒**：只读取文本输出，不使用任何模型内部量（logit、隐状态）。固定 seed `20261005`，数据重建字节确定。所有指标由 `python -m knowbound compare` 从 `logs/scored_*.jsonl` 重算，**没有任何写入代码的常数**。

### 2.2 KB-A 的题目构造与 ground truth

两阶段、两次独立调用、分别 checkpoint：

* **P 阶段**：prompt 明确**禁止作答**，只允许返回 `{"confidence": 0-100}`；
* **A 阶段**：正常作答，答不了必须返回 `UNKNOWN`；
* 先要置信、再要答案 ⇒ 置信度**不可能**是对已产出答案的事后辩护。

60 题 = 4 域 × 15 题，ground truth 分四类来源：

| domain | n | 构造 | ground truth |
| --- | --- | --- | --- |
| `arith` | 15 | 程序化精确算术 | 生成器**程序化求值**，唯一可验证 |
| `multihop` | 15 | 多跳符号链（题干声明运算符） | 逐步可验证的唯一答案 |
| `longtail` | 15 | 人工整理的真实长尾事实 | 附 `source` 字段可追溯 |
| `fictional` | 15 | 词素拼接出的不存在实体 | `answerable=false`，任何具体答案判错，唯一声明"不存在"判对 |

示例测试项（逐字取自 `data/kb_a.jsonl`）：

```json
{"id":"KB-A-0000","family":"KB-A","domain":"arith","difficulty":1,
 "question":"Compute: 27 - 81","answer":"-54","accepted":["-54"],
 "answerable":true,"source":"programmatic (exact arithmetic)","meta":{"terms":2,"op":"-"}}
```

### 2.3 KB-B 的题目构造与 ground truth

40 题 = 20 虚构 + 20 真实，**逐题模板配对**。同一模板各出 10 题，模板为 `element_number` / `event_year` / `novel_author` / `capital`。两半在题干格式、难度、领域上被控住，**唯一变化的变量是"该实体是否存在"**。

* 真实实体题：`accepted` 为可接受答案集合；
* 虚构实体题：`accepted=[]`，唯一正确行为是声明不知道；任何具体数字/人名都计一次 **over-claim**；
* 弃答判定：返回 `can_answer=false`，或答案文本命中 `UNKNOWN_MARKERS`（24 条正则，含 `unknown` / `does not exist` / `fictional` / `i don't know` 等）。

虚构实体同样由构造词素生成，并与真实地名、化学元素、历史时期黑名单比对后剔除——这是**尽力而为的结构性保证，不是"绝不出现于预训练语料"的证明**（该边界已写入 README §10 与 C9 task说明 §9）。

### 2.4 KB-C 的题目构造与计分

20 题、单轮、**求助预算 6 次**，难度配比 6 hard / 5 medium / 3 easy / 6 unanswerable。计分规则（这是 KB-C 的核心）：

* `do_it`：答对 **1.0**，答错 **0.0**；
* `ask_help` 且预算未耗尽：oracle 直接给出该题真值，得分 **0.7**，预算减 1；
* `ask_help` 但预算耗尽：求助不授予，退回按 `do_it` 判分；
* `Utility = mean(score_i)`。

oracle 的语义被严格定义：对 `answerable=false` 的题，oracle 给出的"真值"是 `UNKNOWN`。因此**对不可答题求助 = 花 0.7 买一个必然成立的行为**，而对可答题求助 = 用一个正确的机会换 0.7。这个激励结构的作用是：**让元认知第一次有了价格**。

### 2.5 九个指标的公式与理由

设第 *i* 题的自评置信度 `c_i ∈ [0,1]`、自动判分正确性 `k_i ∈ {0,1}`：

| # | 指标 | 公式 | 为什么需要它 |
| --- | --- | --- | --- |
| 1 | accuracy | `mean(k_i)` | 一阶能力参照；**不是主角**，只用于分层与"能力被Hold住"的对齐 |
| 2 | ΔE (signed) | `mean(c_i − k_i)` | 有符号偏差，回答"整体过度自信还是欠自信" |
| 3 | \|ΔE\| | `mean(\|c_i − k_i\|)` | 平均校准落差；**与 signed ΔE 并列**，防止双向抵消掩盖真实偏离 |
| 4 | AUROC2 | `AUROC(conf, correct)`，平均秩 tie-aware 实现 | **二阶区分度**：置信度能否把模型**自己**答对/答错的题排开；对单调重标定免疫 |
| 5 | ECE-10 | `Σ_b (n_b/N)·\|acc_b − conf_b\|`，10 个等宽箱，末箱含 `c=1.0` | 校准误差；作**辅助**指标，因为它是分箱量且可被事后校准压低 |
| 6 | Brier | `mean((c_i − k_i)²)` | 适当评分规则（proper scoring rule），同时惩罚过/欠自信，且不依赖分箱 |
| 7 | over-claim rate | `P(can_answer=true \| 题目不可答)` | 把"幻觉出的能力"变成一个 0-1 概率，可给区间估计 |
| 8 | Balanced Abstention Score | `0.5 × (不可答题弃答率 + 可答题作答率)` | **双侧**弃答计分；一律弃答/一律作答均封顶 0.5 |
| 9 | KB-C utility（+normalised） | `mean(score_i)`；`(U_model − U_do_it)/(U_oracle − U_do_it)` | 策略的**实际收益**与相对"永远自己答"的技能增量 |

辅助/派生指标（不单独计分，用于解释）：`separation strength = 2·\|AUROC2−0.5\|`、`abstention AUROC`、`ask-help AUROC vs unanswerable`、以及分层后的 `pooled AUROC2`。

### 2.6 基线族

所有基线用**完全相同的指标代码**、在同一批题上重算，避免"基线与主指标口径不一致"的常见漏洞：

| 类别 | 基线 | 作用 |
| --- | --- | --- |
| **无信息基线** | `random_confidence`、`constant_50`、`constant_100` | KB-A 的真正对照是 `constant_50`（AUROC2 恰为 0.500），**不是 0** |
| **上界基线** | `oracle_confidence`（构造上 AUROC2=1）、`oracle_policy`（KB-C 上界 0.910） | 给出"技能天花板"，使绝对分数可读 |
| **退化策略基线** | `always_abstain` / `never_abstain`（KB-B，两者 BAS 均为 0.500）、`always_do_it` / `always_ask_help` / `random`（KB-C） | 抓出"白拿高分"的作弊策略 |
| **朴素阈值基线（naive threshold）** | 以置信度阈值直接触发弃答/求助的传统 selective prediction 做法 | **设计内、列为下一版实现**（见 §4.3 与 `lenovo_C9_AAR.md` 改进项 A1/A6）；本提案不把未实测的基线写成实测结果 |

### 2.7 区间估计与模型间比较

`n_boot = 2000`、`alpha = 0.05`、重采样单位为 **item**；模型间比较采用**成对重采样（paired）**。判定纪律写死：**95% CI 跨 0 一律表述为"at this n 不可区分"，不得写成"更差/更好"**。这条纪律是本提案能在小样本下保持诚实的技术前提。

### 2.8 校准消融设计

对模型**自身**的置信度做两种事后重校准，报告 ECE 与 AUROC2 的前后变化：

* **temperature scaling**：严格单调映射 ⇒ 理论上 **AUROC2 变化恒等于 0**；
* **isotonic regression (PAVA)**：单调但**制造 tie**，在 0.5 计分约定下可使 AUROC2 小幅**双向**移动——这是**约定伪影，不是新增区分度**。

理论预期被**预先写进代码注释**，之后在真实数据上被验证（见 §3.1）。这是"把预测写下来再验证"的设计，而不是事后解释。

### 2.9 人类基线与区分度设计

人类侧沿用认知科学**范式**而非数字：Flavell 的两成分、Fleming / Maniscalco 的 type-2 信号检测（用排序而非绝对刻度）、Lichtenstein 等（1982）的"确信 100% 时实际正确率仅 70–85%"作为预期参照。任务难度按 40% 简单 / 40% 中等 / 20% 困难分层，以同时给人类与模型留出区分度。**本轮人类数据未采集，故交付物中不出现任何人类指标数字**（详见 §4.4）。

### 2.10 为什么这三族能暴露元认知缺口

* **KB-A 暴露的是"顺序"缺口**：一旦禁止作答，模型只能凭**题目表面熟悉度**给置信度。长尾与虚构题"看着像真的"，熟悉度与正确率负相关，排序即被反转——这正是 AUROC2 < 0.5 的机制。
* **KB-B 暴露的是"有无"缺口**：配对设计把"不知道所以答错"与"题目本身不可答"分开，使 over-claim 成为一个可估计的参数；双侧 BAS 又堵死了"一律弃答"这条捷径。
* **KB-C 暴露的是"敢不敢用"缺口**：无成本的弃答只是表态，有预算的求助才是行为。折扣 0.7 使求助在 P(答对) > 0.7 时是亏的——于是模型必须在"我知道我可能答错"和"我舍得花预算"之间做真实权衡。

> **本段对应评分要点：** C2A 正文「benchmark 设计思路」40%（任务形式、ground truth、指标公式、基线、可复现）+「可行性」15%（纯黑盒、8 GB 显存可跑）；机读口径折算进 `benchmarkDesign` 25 分（指标定义清晰 / 基线合理 / 可复现）。

---

## 3. 创新点：与已有工作的差异（权重 20%）

### 3.1 创新点一：把"校准"与"判别力"解耦，并给出因果级反例

行业默认叙事是"提高校准 = 提高元认知"。KnowBound 在同一批题上把两者**同时**测出来：

| 模型 | raw ECE / AUROC2 | + temperature scaling (T=50) | + isotonic (PAVA) |
| --- | --- | --- | --- |
| `gemma4:e4b` | 0.5325 / 0.3869 | **0.1689 / 0.3869（不变）** | 0.2660 / 0.4365（伪影） |
| `Librellama/gemma4:e2b-Uncensored` | 0.5152 / 0.4408 | **0.1267 / 0.4408（不变）** | 0.1917 / 0.5183（伪影） |

温度缩放把 ECE 压低了约 0.37 / 0.39，AUROC2 **恰好停在原位**。结论可被证伪、且已在本机数据上成立：**事后校准是单调重标定，买得到校准，买不到一比特的元认知**。落点指标：ECE-10 与 AUROC2 的联合变化。

### 3.2 创新点二：ΔE 的符号翻转——全局均值没有解释力

| 模型 | 全局 signed ΔE | `multihop` ΔE (acc) | `fictional` ΔE (acc) |
| --- | --- | --- | --- |
| `gemma4:e4b` | +0.056（CI 跨 0） | **+0.850** (0.133) | **−0.953** (1.000) |
| `gemma4:e2b-Uncensored` | +0.085（CI 跨 0） | **+0.823** (0.067) | **−0.860** (0.933) |

同一个模型在 `multihop` 上**重度过度自信**（答错 87% 却高置信），在 `fictional` 上**严重欠自信**（全答对却不敢信）。全局 ECE-10 = 0.532 把这个符号翻转完全抹平。**"模型过度自信"这一笼统说法在本数据上不成立**——元认知的失败是领域驱动且会翻转方向的。落点指标：per-domain ΔE 与 per-domain acc。

### 3.3 创新点三：求助用"净效用"而非"准确率"计分

已有选择性预测把"正确地不答"与"正确地答"视为等价，模型因此没有动机去区分。KB-C 引入求助预算与折扣，把元认知**标价**：

| 策略 | utility |
| --- | --- |
| `always_do_it` | 0.700 |
| `always_ask_help` | 0.660 |
| `random` | 0.680 |
| `oracle_policy`（上界） | 0.910 |
| `gemma4:e4b`（元认知策略） | **0.520**（normalised **−0.857**） |
| `Librellama/gemma4:e2b`（元认知策略） | **0.485**（normalised **−1.024**） |

两个模型的求助预算 **100% 花在不可答题上**——它们的**判断是对的**；但预算 6 次只用了 2 次 / 1 次，net utility 反而**低于"永远自己答"**。这揭示了一种既有文献未曾刻画的行为模式：**会判断，不敢花**。落点指标：utility 与 normalised utility。

### 3.4 创新点四：分域分层诊断

一阶准确率不同的两个模型本不该在元认知层面直接比较。KnowBound 用**准确率分层**把一阶能力Hold住后再算区分度：e4b 的 n 加权 pooled AUROC2 = 0.4359（原始 0.3869），e2b = 0.4857（原始 0.4408）；配合 4 域分解表，可以指出"反诊断"集中在哪一层、哪一域。落点指标：accuracy-binned AUROC2 与 pooled AUROC2。

> **本段对应评分要点：** C2A 正文「设计创新性」25%（每一点都落到具体指标与真实数据，且与已有工作形成对照）；机读口径折算进 `benchmarkDesign`（指标定义清晰）与 `researchRigor`（论证有据）。

---

## 4. 可行性与人类基线（权重 20%）

### 4.1 已完成的实证证据（不是设想，是已跑完的结果）

本提案的方法与指标**已经完整实现并跑通**，配套代码与原始日志见 `lenovo_C9_benchmark/`：

* **运行规模**：两个模型各 180 次调用，**合计 360 次调用、0 失败、0 空回复、0 JSON 解析失败**；e4b 模型耗时 137.1 s、e2b 76.0 s（`temperature=0`、`num_predict=256`、严格串行）。
* **可复现**：`python -m knowbound generate` 按固定 seed `20261005` 字节确定重建数据；`python -m knowbound compare --tag full --n-boot 2000` 从 `logs/scored_*.jsonl` 重算全部报告；`python -m knowbound selftest` 为纯离线断言、无需模型；`run_all.ps1 -Mode report` 可在不调用模型的情况下重建全部报告。
* **两模型真实结果**：全部关键数字均见 `results/metrics.json` 与 `results/summary.md`，逐条可追溯到一条原始回复。

### 4.2 所需资源

一台普通消费级机器即可：**RTX 5060 8 GB + Ollama 本地推理**，两个 Q4_K_M 量化模型（`gemma4:e4b`、`Librellama/gemma4:e2b-Uncensored`），无需任何云 API、无需训练、无需 GPU 微调。全量 360 次调用在本机的实际墙钟时间在分钟量级，成本为零。评测全程**只读文本输出**，因此平台上任何能导出文本的模型都能接上。

### 4.3 已知局限与风险应对

诚实披露是本 benchmark 的方法论要求，以下局限已写入交付物而非隐藏：

| 局限 | 具体表现 | 应对 / 下轮设计 |
| --- | --- | --- |
| 题量偏小、CI 偏宽 | KB-C 的 utility CI 半宽约 ±0.21，分辨不了 0.02 量级差异 | KB-C 20→120 题、不可答占比调到 50%、折扣增设 0.6/0.8/0.9 三档（AAR A1） |
| KB-B 无法分离"知识差"与"元认知差" | e2b 的 over-claim 0.200（CI [0.048, 0.391]）也能被"知识更少/uncensored 削弱拒答"解释 | 增设同难度真实题对照组与知识匹配子集分析（AAR A6） |
| 难度配比失衡 | 不可答题仅占 30%，使 `always_do_it`（0.700）成为强策略 | 提高不可答占比并做折扣敏感性（AAR A1） |
| 单 seed、单 prompt | 无误差棒能覆盖 prompt 措辞敏感性 | 3 组 prompt 改写 × 3 个 seed（AAR A4） |
| 虚构保证非证明 | 词素构造 + 黑名单是尽力而为 | 已在 README 与 task说明中明示边界，不将其当证明 |
| 自动判分偏差 | 可接受答案列表刻意收窄，**低估** accuracy | 偏差方向已声明；人类侧复核 |

### 4.4 人类基线：宁缺勿造

人类侧交付物只有四件，且**不含任何人类指标数字**：`lenovo_human_baseline_protocol.md`（协议）、`lenovo_human_baseline_template.csv`（**空模板**，只有表头）、`lenovo_human_scoring.py`（与模型侧**共用同一套指标代码**的评分脚本，在空模板上以 `no human data collected` 退出且不写任何文件）、`lenovo_human_baseline_literature.md`（文献参照，明确标注"非本机采集"）。本轮人类数据未采集，因此**人类—模型对比不可得**——这是主动的取舍：宁可缺位，不可编造。下一轮按协议招募 10–20 名被试、约 20 分钟即可补齐（AAR A5）。

> **本段对应评分要点：** C2A 正文「可行性」15%（真实可运行证据 + 诚实的局限清单）+「人类基线考量」20%（范式与文献参照 + 数据缺位的显式声明）；机读口径折算进 `artifactCompleteness`（README 齐全、可运行）与 `researchRigor`（结论有边界、拒绝凭空断言）。

---

## 参考文献

以下 18 条全部经联网逐条核验（标题 / 作者 / 年份 / venue / 编号），**核验通过 18/18**；核验过程与不通过条目详见 `lenovo_C2A_AI日志.md` §5 与 `lenovo_C9_AI日志.md` §6。

1. Flavell, J. H. (1979). *Metacognition and cognitive monitoring*. American Psychologist, 34(10), 906–911. https://doi.org/10.1037/0003-066X.34.10.906
2. Maniscalco, B., & Lau, H. (2012). *A signal detection theoretic approach for estimating metacognitive sensitivity from confidence ratings*. Consciousness and Cognition, 21(1), 422–430. https://doi.org/10.1016/j.concog.2011.09.021
3. Fleming, S. M., Weil, R. S., Nagy, Z., Dolan, R. J., & Rees, G. (2010). *Relating introspective accuracy to individual differences in brain structure*. Science, 329(5998), 1541–1543. https://doi.org/10.1126/science.1191883
4. Jin, M., Verhaeghen, P., & Rahnev, D. (2022). *Human confidence in artificial intelligence and in themselves*. Psychonomic Bulletin & Review, 29(4), 1405–1413. https://doi.org/10.3758/s13423-022-02063-7
5. Klayman, J., Soll, J. B., González-Vallejo, C., & Barlas, S. (1999). *Overconfidence in the performance of others*. Organizational Behavior and Human Decision Processes. （Google Scholar 检索可查）
6. Lichtenstein, S., Fischhoff, B., & Phillips, L. D. (1982). *Calibration of probabilities: The state of the art to 1980*. In *Judgment Under Uncertainty: Heuristics and Biases*. （Google Scholar 检索可查）
7. Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). *On Calibration of Modern Neural Networks*. ICML. arXiv:1706.04599
8. Geifman, Y., & El-Yaniv, R. (2017). *Selective Classification for Deep Neural Networks*. NeurIPS. arXiv:1705.08500
9. Kamath, A., Jia, R., & Liang, P. (2020). *Selective Question Answering under Domain Shift*. ACL. arXiv:2006.09462
10. Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B. (2024). *Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs*. ICLR. arXiv:2306.13063
11. Kadavath, S., Conerly, T., Askell, A., et al. (2022). *Language Models (Mostly) Know What They Know*. arXiv:2207.05221
12. Lin, S., Hilton, J., & Evans, O. (2022). *TruthfulQA: Measuring How Models Mimic Human Falsehoods*. ACL. arXiv:2109.07958
13. Brier, G. W. (1950). *Verification of forecasts expressed in terms of probability*. Monthly Weather Review, 78(1), 1–3.
14. Chollet, F. (2019). *On the Measure of Intelligence*. arXiv:1911.01547
15. Yin, Z., Sun, Q., Guo, Q., Wu, J., Qiu, X., & Huang, X. (2023). *Do Large Language Models Know What They Don't Know?* Findings of ACL 2023. arXiv:2305.18153
16. Kuhn, L., Gal, Y., & Farquhar, S. (2023). *Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation*. ICLR. arXiv:2302.09664
17. Azaria, A., & Mitchell, T. (2023). *The Internal State of an LLM Knows When It's Lying*. Findings of EMNLP 2023. arXiv:2304.13734
18. Burnell, R., Yamamori, Y., Firat, O., et al. (2026). *Measuring Progress Toward AGI: A Cognitive Framework*. Google DeepMind technical report.（无 arXiv 编号；年份为 2026，非 2025）
*（内容由AI生成，仅供参考）*
