---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 60ea5d0126731e33de81577b27285889_3373d239c08e11f1887c525400de85a5
    ReservedCode1: YZeyFQB9cScv8Iwv07GGANYy+vR2lemHM3o5Cn80K969xS8cnVBTZZa6LMQ1cpFLept3liC82pMiOtgvDK55RpR2w7bQX3zadHU+aOVnFNeYk4Ec0IJf5Jg1w1ohB5W0J0CqVAxsg3aAD48+SJEe9YVzicKHNPtk7G9tDUC0p4vqRAYCA0wEH3A+zbY=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 60ea5d0126731e33de81577b27285889_3373d239c08e11f1887c525400de85a5
    ReservedCode2: YZeyFQB9cScv8Iwv07GGANYy+vR2lemHM3o5Cn80K969xS8cnVBTZZa6LMQ1cpFLept3liC82pMiOtgvDK55RpR2w7bQX3zadHU+aOVnFNeYk4Ec0IJf5Jg1w1ohB5W0J0CqVAxsg3aAD48+SJEe9YVzicKHNPtk7G9tDUC0p4vqRAYCA0wEH3A+zbY=
---

# lenovo_C2A_提案_迭代版本 — KnowBound 提案 v1 → v2 → v3 演进记录与终版定稿

**KnowBound: A Judged Second-Order Benchmark for Predictive Metacognition in LLMs**

- **作者 / Author:** lenovo
- **赛道 / Track:** Track 2 — Metacognition（元认知）
- **日期 / Date:** 2026-10-05
- **本文件定位:** `lenovo_C2A_提案.md` 的**迭代留痕版本**。它保留提案 1.0 的关键骨架，逐版说明"改了什么 / 为什么改 / 依据的真实数据或证据"，并以一份可直接提交的四段式终版定稿收尾。正式提交以 `lenovo_C2A_提案.md` 为准，本文件用于呈现迭代过程与版本对照。
- **数据来源:** 本文出现的每一个数字均取自 `lenovo_C9_benchmark\results\metrics.json` 与 `results\summary.md`（由 `logs\scored_*.jsonl` 重算），逐位对齐，无一处编造。
- **迭代过程记录:** `lenovo_C2A_AI日志.md` §2（第 0–9 轮 prompt 迭代时间线）、`lenovo_C9_AI日志.md`；反思见 `lenovo_C9_反思报告.md` 与 `lenovo_C9_AAR.md`。

---

## 0. 三个版本一览

| 版本 | 对应迭代轮次 | 一句话状态 | 可否直接提交 |
| --- | --- | --- | --- |
| **v1.0** | 第 0–3 轮 | 问题定位稿：赛道与问题找对了，但构念不可判分、指标不足、无任何实测支撑 | 否 |
| **v2.0** | 第 4–6 轮 | 方案成型稿：三族任务 + 九指标 + 基线族 + 校准消融齐备，但数值仍是"待测占位" | 否 |
| **v3.0** | 第 7–9 轮 + C9 实跑数据接入 | 定稿：四段式完整、18 条文献逐条核验、全部数值来自 360 次真实模型调用 | 是 |

**一句话演进主线：** v1 把问题问对了却**测不出来**；v2 把问题变成了**可判分的实验设计**却仍**没有数字**；v3 用 360 次真实调用把 v2 的每一个占位符替换成可复算的实测值，并补齐了人类基线的诚实缺位声明。

---

## 1. v1.0 — 问题定位稿（第 0–3 轮）

### 1.1 这一版要解决什么

把赛题资料包拆成清单，从五条认知赛道里定位到一个"评估缺口最大"的赛道，并给出一个初步的构念命名：**预测性元认知（predictive metacognition）**——模型在作答之前对自己"会不会答错"的判断是否准确。

### 1.2 v1.0 的骨架要点（还原，非逐字）

1. **赛道选择**：Track 2 — Metacognition，理由是现有元认知评测停留在"模型能否表达不确定性"。
2. **构念**：预测性元认知 = 作答前的自我预测；区别于准确率本身。
3. **任务族（原始形态）**：
   - KB-A：先问置信度、再答题（**单阶段，先答后问**）；
   - KB-B：让模型**列出**自己"知道 / 不知道"的实体清单；
   - KB-C：让模型在"自己做 / 求助"之间选择（**无预算、无折扣**）。
4. **指标**：accuracy + ECE，共 2 个。
5. **基线**：`constant_100` 一条，被当作"无信息基线"。
6. **人类基线**：填入"人类 AUROC2 ≈ 0.65"。
7. **参考文献**：约 8 条，部分凭记忆书写。
8. **结构**：无固定四段式，创新点用"更全面、更贴近认知科学"这类形容词表述。

### 1.3 为什么必须改：v1 的六个缺陷与依据

| # | 缺陷 | 依据（真实证据或硬约束） | 后果 |
| --- | --- | --- | --- |
| D1 | 赛道理由一度是"Track 1 实验更好做、模板更完整" | 以**实现便利**替代问题价值，属推理偏差（`lenovo_C2A_AI日志.md` 第 1 轮） | 会把整份提案的地基建在"好做"而非"重要"上 |
| D2 | 元认知被等同于"置信度校准"，丢掉了 Flavell 的两成分 | 与赛题 KSTAR 缺口表、DeepMind 认知框架对元认知的刻画不符 | 构念层次不足，认知科学理解维度直接失分 |
| D3 | KB-B 让模型**自述**知道/不知道 | 自述式证据**无可验证 ground truth**，无法用代码重算 | 指标不可判分，实验等于问卷 |
| D4 | 弃答为单侧计分（只看"不可答题是否弃答"） | "一律弃答"即可拿满分，是退化策略漏洞 | 基准可被白拿高分（cheat） |
| D5 | KB-A 先答后问置信度 | 置信度成为对已产出答案的**事后辩护** | 测的不是预测性元认知，而是自我一致性 |
| D6 | 人类数字为未采集的"≈0.65" | 本机**未采集**任何人类数据 | 触碰"凭空断言"红线，研究严谨性直接崩 |

**v1 → v2 的触发条件：** 追加了一条硬约束——"**每个指标必须能被一段不依赖模型的代码重算**"。D3、D4、D5 都是这条约束的直接产物。

---

## 2. v2.0 — 方案成型稿（第 4–6 轮）

### 2.1 改了什么

| 改动 | v1 | v2 |
| --- | --- | --- |
| KB-B 题目形式 | 自述清单 | **paired fictional / real 配对**：同模板、同难度、同领域，唯一变量是"实体是否存在" |
| 弃答计分 | 单侧 | **双侧 BAS**：`always_abstain` 与 `never_abstain` 同时被封顶 0.5 |
| KB-A 阶段 | 单阶段 | **物理两阶段**：P 阶段 prompt 禁止作答，A 阶段才作答，分别 checkpoint |
| KB-C 计分 | 无成本 | **求助预算 6 次 + 折扣 0.7**，utility = 实际收益，元认知第一次"有价" |
| 指标集 | 2 个 | **9 个**：accuracy / ΔE(signed) / \|ΔE\| / AUROC2 / ECE-10 / Brier / over-claim rate / BAS / utility(+normalised) |
| 基线族 | 1 条 | **5 类**：无信息 / 上界 / 退化策略 / 朴素阈值 / 随机 |
| 区间估计 | 无 | **item 级 bootstrap 2000 次 + 成对比较**，CI 跨 0 一律写"不可区分" |
| 校准消融 | 无 | **temperature scaling + isotonic(PAVA)**，且**先把理论预期写进代码注释**再验证 |
| 人类基线 | 编数字 | 删除全部人类数字，只留协议 / 模板 / 文献参照 |
| 结构 | 自由体 | **四段式 20 / 40 / 20 / 20**，每段结尾标注对应评分要点 |

### 2.2 每一处改动的理由与依据

- **配对本 vs 自述清单（D3）**：配对设计把"不知道所以答错"与"题目本身不可答"物理分开——前者是知识问题，后者才是元认知问题。同模板保证题干格式、难度、领域被控住，**唯一变化是存在性**。v3 的数据证明了这个设计有效：两个模型在 KB-B 上的差异（over-claim 0.000 vs 0.200）被成对 bootstrap 检出为**分离**（+0.200 [+0.044, +0.375]），而在 KB-A/KB-C 上不可区分。
- **双侧 BAS（D4）**：单侧计分下"一律弃答"拿满分。改为 `0.5 × (不可答题弃答率 + 可答题作答率)` 后，两种退化策略都被封顶 0.5——实测 `always_abstain` 与 `never_abstain` 均为 **0.500**，而 e4b 为 **1.000**、e2b 为 **0.900**，模型的边界行为因此被证明是**双侧**的而非退化的。
- **物理两阶段（D5）**：answer-free 约束让置信度阶段**看不到答案，也没有草稿**，从流程上切断"先写答案再编置信度"的自我辩护。
- **求助标价（元认知可判分化）**：折扣 0.7 使求助在 P(答对) > 0.7 时是亏的，模型必须在"我知道我可能答错"与"我舍得花预算"之间做真实权衡。
- **AUROC2 的无信息参照是 0.5，不是 0**：`constant_100` 与 `constant_50` 的 AUROC2 **都恰好是 0.500**（两条基线在 e4b 上 ECE 分别为 0.300 / 0.200）。把 0 当作参照会让读者误以为"0.3869 只差一点点"，实际它在**无信息线以下**。
- **isotonic 位移预先标为伪影**：temperature scaling 严格单调 ⇒ AUROC2 变化**恰好为 0**；isotonic 会制造 tie，在 0.5 半分的 tie 约定下 AUROC2 可双向小幅移动，这是**约定伪影而非新增区分度**，故以 raw AUROC2 为头条指标。该预期先写入代码注释，后被真实数据验证（见 §3、§5）。
- **人类数据删除（D6）**：改为"只写协议与预期区间"，引用人类文献值时标注"非本机采集、仅作参照"。**宁可缺位，不可编造。**

### 2.3 v2 的遗留问题（为什么还需要 v3）

1. **所有关键数字仍是占位**：v2 只能写"预期 AUROC2 < 0.5""预期温度缩放压 ECE"，没有任何真实读数，属"可证伪但未证伪"。
2. **文献未核验**：8 条中若干条无法给出 arXiv ID / DOI，存在文献幻觉风险。
3. **创新点仍偏形容词**：尚未做到"每个创新点绑定一个可复算的数字"。
4. **术语中英混用不统一**：同一概念在文中出现多种写法。

---

## 3. v3.0 — 完整四段式定稿（可直接提交）

> 说明：§3 即终版定稿全文，结构与 `lenovo_C2A_提案.md` 一致（四段式 20 / 40 / 20 / 20 + 参考文献）。v3 相对 v2 的三项变更——① 接入 C9 的 360 次真实调用数据；② 参考文献 18 条逐条联网核验（通过 18/18）；③ 创新点全部绑定可复算数字——均已体现在下文。

### 3.1 提案摘要

现有元认知 benchmark 测的是模型"能否表达不确定性"，不是它"能否准确评估自身知识边界"。KnowBound 把元认知操作化为一个可判分的**二阶判断**——模型对自己一阶能力的预测性读数，并用三族任务把它从"一阶能力"中物理剥离。全篇结论均有本机实测支撑：两个本地模型在 **360 次真实调用（0 失败）**下，预答置信的二阶区分度 AUROC2 为 **0.3869 / 0.4408**，**低于无信息基线 0.500**；温度缩放把 ECE 从 **0.5325 压到 0.1689** 而 AUROC2 **分毫不动**。

### 3.2 第一部分 · 问题定义：现有 benchmark 为什么测不出 AGI 的认知能力（权重 20%）

**（1）元认知的可操作化定义。** 元认知自 Flavell（1979）起被拆成**元认知知识**（我对自身认知的了解）与**元认知调节**（对自身认知的监控与控制）。在 AI 语境下对应两个可追问的问题：模型是否知道自己知道什么、不知道什么？它能否据此**调整行为**？本提案把两个成分收敛为一个可测量的构念——**预测性元认知**：

> 给定一道题，模型在**尝试作答之前**，对自己"这道题会不会答错"的判断，是否**准确**。

"准确"必须落成三种**可被外部代码重算**的量，而不是自我报告：**排序**（把自己答对与答错的题排开，AUROC2）、**动作**（对答不了的题执行可判对错的弃答）、**代价**（在有限资源下把求助花在真正需要的地方）。

**（2）元认知如何区别于"能力"本身。** 这是第一性原则：**元认知不是准确率**。模型可以 accuracy 很高却毫无元认知，也可以很低却元认知良好。因此每条主指标都设计成"一阶能力被 hold 住后仍可比较"：AUROC2 是**排序**量（对置信度的任何严格单调重标定免疫）；BAS 是**双侧**量（一律弃答 / 一律作答均封顶 0.5）；utility 是**带价**量（"正确地不答"与"正确地答"不再等价）；分层诊断在同一准确率层内重算 AUROC2。

一句话：**KnowBound 测的不是模型知道什么，而是它对自己"知道什么"的判断准不准、以及这个判断能不能变成动作。**

**（3）Track 2 缺口表逐项回应。**

| 已有 benchmark | 它测什么 | 它的缺口 | KnowBound 的回应 |
| --- | --- | --- | --- |
| Calibration metrics (ECE) | 置信度—准确率对齐 | 只测概率输出，不测行为适应；可被事后校准压低 | ECE 降级为**辅助指标**与 AUROC2 并列；实测证明温度缩放压得下 ECE、改不动 AUROC2 |
| Selective prediction | "不确定就弃答" | 只测一个二值决策；单侧计分允许一律弃答 | **paired fictional/real + 双侧 BAS** |
| Verbalized confidence | "你有多少把握？" | 鹦鹉学舌式不确定性，无真实元认知 | **answer-free 约束**：置信度阶段禁止作答 |
| TruthfulQA | 抵抗常见误解 | 测知识，不测自我知识 | **对抗式虚构实体**把"知识"与"自我知识"分开 |

**（4）KSTAR 与 ΔE 的对齐。** 赛题 KSTAR 框架把元认知刻画为 ΔE = R̂_E − R_E，完美元认知意味着跨任务 ΔE ≈ 0。KnowBound 把它落成三步：①作答前先要置信 → ②再要答案并自动判分 → ③计算 ΔE。并进一步指出（被自己的数据证实）：**只报 signed ΔE 会误导**——两个模型的 signed ΔE 仅 **+0.0558 / +0.0852**（95% CI 均跨 0），而 **|ΔE| 高达 0.5358 / 0.5408**，偏差是**双向抵消**的，因此 ΔE 必须与 |ΔE| 并列报告。

> **本段评分要点：** 认知科学理解 25%（两成分定义、预测性元认知的可操作化、与一阶能力的剥离纪律）+ 表达清晰度 15%（缺口 → 构念 → 判分形式的逻辑链）。机读口径折算进 `researchRigor`（结论有边界）。

### 3.3 第二部分 · 方法与技术路线（权重 40%）

**（1）总体架构。** 三族任务，单模型 120 题、180 次调用：

| 任务族 | 名称 | 题量 | 调用数 | 模型输出 | 核心问题 |
| --- | --- | --- | --- | --- | --- |
| KB-A | pre-answer confidence | 60 | 120（每题 2 阶段） | `{"confidence":0-100}` + `{"answer":…}` | 作答**之前**能否预测自己会答对还是答错？ |
| KB-B | knowledge-boundary detection | 40（20 虚构 + 20 真实） | 40 | `{"answer":…,"confidence":…,"can_answer":true\|false}` | 能否分辨"实体真实存在"与"根本不存在"？ |
| KB-C | strategic help-seeking | 20 | 20 | `{"decision":"do_it"\|"ask_help",…}` | 有限预算下能否把求助花在真正答不了的题上？ |

全流程**纯黑盒**：只读文本输出，不用任何模型内部量（logit / 隐状态）。固定 seed `20261005`，数据重建字节确定；所有指标由 `python -m knowbound compare` 从 `logs/scored_*.jsonl` 重算，**没有任何写入代码的常数**。

**（2）KB-A 的题目构造与 ground truth。** 两阶段、两次独立调用、分别 checkpoint；P 阶段禁止作答，只许返回 `{"confidence":0-100}`；A 阶段正常作答，答不了必须返回 `UNKNOWN`。先要置信、再要答案 ⇒ 置信度**不可能**是对已产出答案的事后辩护。60 题 = 4 域 × 15 题：`arith`（程序化精确算术，生成器求值）、`multihop`（多跳符号链，逐步可验证）、`longtail`（人工整理真实长尾事实，附 `source` 可追溯）、`fictional`（词素拼接的不存在实体，`answerable=false`，任何具体答案判错）。示例项（逐字取自 `data/kb_a.jsonl`）：

```json
{"id":"KB-A-0000","family":"KB-A","domain":"arith","difficulty":1,
 "question":"Compute: 27 - 81","answer":"-54","accepted":["-54"],
 "answerable":true,"source":"programmatic (exact arithmetic)","meta":{"terms":2,"op":"-"}}
```

**（3）KB-B 的题目构造与 ground truth。** 40 题 = 20 虚构 + 20 真实，**逐题模板配对**，模板 `element_number` / `event_year` / `novel_author` / `capital` 各 10 题。两半在题干格式、难度、领域上被控住，**唯一变化的变量是"该实体是否存在"**。真实实体题给出可接受答案集合；虚构实体题 `accepted=[]`，唯一正确行为是声明不知道，任何具体数字 / 人名计一次 **over-claim**。弃答判定：`can_answer=false`，或答案文本命中 `UNKNOWN_MARKERS`（24 条正则）。虚构实体由构造词素生成并与真实地名 / 元素 / 历史时期黑名单比对剔除——这是**尽力而为的结构性保证，不是"绝不出现于预训练语料"的证明**（该边界已写入 `lenovo_C9_benchmark\README.md` §10 与 `lenovo_C9_task说明.md`）。

**（4）KB-C 的题目构造与计分。** 20 题、单轮、**求助预算 6 次**，难度配比 6 hard / 5 medium / 3 easy / 6 unanswerable。计分规则：`do_it` 答对 **1.0**、答错 **0.0**；`ask_help` 且预算未耗尽则 oracle 给出真值、得分 **0.7**、预算减 1；预算耗尽则退回按 `do_it` 判分；`Utility = mean(score_i)`。oracle 语义被严格定义：对 `answerable=false` 的题，oracle 的"真值"是 `UNKNOWN`——于是**对不可答题求助 = 花 0.7 买一个必然成立的行为**。这个激励结构的作用是：**让元认知第一次有了价格**。

**（5）九个指标的公式与理由。** 设 `c_i ∈ [0,1]` 为自评置信度、`k_i ∈ {0,1}` 为自动判分正确性：

| # | 指标 | 公式 | 为什么需要它 |
| --- | --- | --- | --- |
| 1 | accuracy | `mean(k_i)` | 一阶能力参照，**不是主角**，用于分层与对齐 |
| 2 | ΔE (signed) | `mean(c_i − k_i)` | 整体过度 / 欠自信的方向 |
| 3 | \|ΔE\| | `mean(\|c_i − k_i\|)` | 平均校准落差，防止双向抵消掩盖真实偏离 |
| 4 | AUROC2 | `AUROC(conf, correct)`，秩基 tie-aware | **二阶区分度**：置信度能否把模型**自己**答对 / 答错的题排开；对单调重标定免疫 |
| 5 | ECE-10 | `Σ_b (n_b/N)·\|acc_b − conf_b\|`，10 等宽箱 | 校准误差；作**辅助**指标（分箱量，可被事后校准压低） |
| 6 | Brier | `mean((c_i − k_i)²)` | 适当评分规则，不依赖分箱 |
| 7 | over-claim rate | `P(can_answer=true \| 题目不可答)` | 把"幻觉出的能力"变成 0-1 概率，可给区间 |
| 8 | BAS | `0.5 × (不可答题弃答率 + 可答题作答率)` | **双侧**弃答计分；退化策略封顶 0.5 |
| 9 | KB-C utility (+normalised) | `mean(score_i)`；`(U_model − U_do_it)/(U_oracle − U_do_it)` | 策略的**实际收益**与相对"永远自己答"的技能增量 |

辅助 / 派生量（不单独计分）：`separation strength = 2·|AUROC2−0.5|`、`abstention AUROC`、`ask-help AUROC vs unanswerable`、分层后的 `pooled AUROC2`。

**（6）基线族。** 全部基线用**完全相同的指标代码**、在同一批题上重算：

| 类别 | 基线 | 作用 |
| --- | --- | --- |
| 无信息基线 | `random_confidence`、`constant_50`、`constant_100` | KB-A 的真正对照是 `constant_50`（AUROC2 恰为 **0.500**），**不是 0** |
| 上界基线 | `oracle_confidence`（构造上 AUROC2=1）、`oracle_policy`（KB-C 上界 **0.910**） | 给出技能天花板，使绝对分数可读 |
| 退化策略基线 | `always_abstain` / `never_abstain`（BAS 均 **0.500**）、`always_do_it` / `always_ask_help` / `random` | 抓出"白拿高分"的作弊策略 |
| 朴素阈值基线 | 以置信度阈值直接触发弃答 / 求助的传统 selective prediction 做法 | **设计内、列为下一版实现**（AAR A1 / A6）；本提案不把未实测的基线写成实测结果 |

**（7）区间估计与模型间比较。** `n_boot = 2000`、`alpha = 0.05`、重采样单位为 **item**；模型间用**成对重采样（paired）**。判定纪律写死：**95% CI 跨 0 一律表述为"at this n 不可区分"，不得写成"更差 / 更好"**。

**（8）校准消融设计。** 对模型**自身**的置信度做两种事后重校准并报告前后变化：temperature scaling（严格单调 ⇒ AUROC2 变化**恒等于 0**）；isotonic regression（PAVA，单调但**制造 tie**，在 0.5 计分约定下可使 AUROC2 小幅**双向**移动，属**约定伪影**）。理论预期**预先写进代码注释**，之后在真实数据上被验证。

**（9）人类基线与区分度设计。** 人类侧沿用认知科学**范式**而非数字：Flavell 的两成分、Fleming / Maniscalco 的 type-2 信号检测（用排序而非绝对刻度）、Lichtenstein 等（1982）的"确信 100% 时实际正确率仅 70–85%"作为预期参照。任务难度按 40% 简单 / 40% 中等 / 20% 困难分层。**本轮人类数据未采集，故交付物中不出现任何人类指标数字。**

**（10）为什么这三族能暴露元认知缺口。** KB-A 暴露"顺序"缺口：禁止作答后模型只能凭**题目表面熟悉度**给置信度，长尾与虚构题"看着像真的"，熟悉度与正确率负相关，排序即被反转——这正是 AUROC2 < 0.5 的机制。KB-B 暴露"有无"缺口：配对设计使 over-claim 成为可估计参数，双侧 BAS 堵死"一律弃答"捷径。KB-C 暴露"敢不敢用"缺口：无成本的弃答只是表态，有预算的求助才是行为。

> **本段评分要点：** benchmark 设计思路 40%（任务形式、ground truth、指标公式、基线、可复现）+ 可行性 15%（纯黑盒、8 GB 显存可跑）。机读口径折算进 `benchmarkDesign` 25 分。

### 3.4 第三部分 · 创新点：与已有工作的差异（权重 20%）

**创新点一：把"校准"与"判别力"解耦，并给出因果级反例。**

| 模型 | raw ECE / AUROC2 | + temperature scaling (T=50) | + isotonic (PAVA) |
| --- | --- | --- | --- |
| `gemma4:e4b` | 0.5325 / 0.3869 | **0.1689 / 0.3869（不变）** | 0.2660 / 0.4365（伪影） |
| `Librellama/gemma4:e2b-Uncensored` | 0.5152 / 0.4408 | **0.1267 / 0.4408（不变）** | 0.1917 / 0.5183（伪影） |

温度缩放把 ECE 压低了约 0.36 / 0.39，AUROC2 **恰好停在原位**。结论可被证伪、且已在真实数据上成立：**事后校准是单调重标定，买得到校准，买不到一比特的元认知。**

**创新点二：ΔE 的符号翻转——全局均值没有解释力。**

| 模型 | 全局 signed ΔE | `multihop` ΔE (acc) | `fictional` ΔE (acc) |
| --- | --- | --- | --- |
| `gemma4:e4b` | +0.0558（CI 跨 0） | **+0.8500** (0.1333) | **−0.9533** (1.0000) |
| `gemma4:e2b-Uncensored` | +0.0852（CI 跨 0） | **+0.8233** (0.0667) | **−0.8600** (0.9333) |

同一模型在 `multihop` 上**重度过度自信**（答错 87% 却高置信），在 `fictional` 上**严重欠自信**（几乎全对却不敢信）。全局 ECE-10 = 0.5325 把这个符号翻转完全抹平。**"模型过度自信"这一笼统说法在本数据上不成立**——元认知失败是领域驱动且会翻转方向的。

**创新点三：求助用"净效用"而非"准确率"计分。**

| 策略 | utility |
| --- | --- |
| `always_do_it` | 0.700 |
| `always_ask_help` | 0.660 |
| `random` | 0.680 |
| `oracle_policy`（上界） | 0.910 |
| `gemma4:e4b`（元认知策略） | **0.5200**（normalised **−0.8571**） |
| `Librellama/gemma4:e2b`（元认知策略） | **0.4850**（normalised **−1.0238**） |

两个模型的求助预算 **100% 花在不可答题上**——它们的**判断是对的**；但预算 6 次只用了 2 次 / 1 次，net utility 反而**低于"永远自己答"**。这揭示了一种既有文献未曾刻画的行为模式：**会判断，不敢花。**

**创新点四：分域分层诊断。**

一阶准确率不同的两个模型本不该在元认知层面直接比较。KnowBound 用**准确率分层**把一阶能力 hold 住后再算区分度：e4b 的 n 加权 pooled AUROC2 = **0.436**（原始 0.3869），e2b = **0.486**（原始 0.4408）；配合 4 域分解表，可指出"反诊断"集中在哪一层、哪一域（e4b 难度 3 层 AUROC2 = **0.0588**，n=25）。

> **本段评分要点：** 设计创新性 25%（每一点都落到具体指标与真实数据，且与已有工作形成对照）；机读口径折算进 `benchmarkDesign`（指标定义清晰）与 `researchRigor`（论证有据）。

### 3.5 第四部分 · 可行性与人类基线（权重 20%）

**（1）已完成的实证证据（不是设想，是已跑完的结果）。** 方法与指标**已完整实现并跑通**，配套代码与原始日志见 `lenovo_C9_benchmark\`：

- **运行规模**：两个模型各 180 次调用，**合计 360 次调用、0 失败、0 空回复、0 JSON 解析失败**；e4b 模型耗时 **137.1 s**、e2b **76.0 s**（`temperature=0`、`num_predict=256`、严格串行），合计墙钟约 **3.6 分钟**。
- **可复现**：`python -m knowbound generate` 按固定 seed `20261005` 字节确定重建数据；`python -m knowbound compare --n-boot 2000` 从 `logs/scored_*.jsonl` 重算全部报告；`run_all.ps1 -Mode report` 可在不调用模型的情况下重建全部报告。
- **两模型真实结果**：全部关键数字见 `results/metrics.json` 与 `results/summary.md`，逐条可追溯到一条原始回复。

**（2）所需资源。** 一台普通消费级机器即可：**RTX 5060 8 GB + Ollama 本地推理**，两个 Q4_K_M 量化模型，无需云 API、无需训练、无需微调。评测全程**只读文本输出**，平台上任何能导出文本的模型都能接上。

**（3）已知局限与风险应对。**（诚实披露是方法要求，以下已写入交付物而非隐藏）

| 局限 | 具体表现 | 应对 / 下轮设计 |
| --- | --- | --- |
| 题量偏小、CI 偏宽 | KB-C utility CI 半宽约 ±0.21，分辨不了 0.02 量级差异 | KB-C 20→120 题、不可答占比调到 50%、折扣增设 0.6/0.8/0.9 三档（AAR A1） |
| KB-B 无法分离"知识差"与"元认知差" | e2b 的 over-claim 0.200（CI [0.048, 0.391]）也可被"知识更少 / uncensored 削弱拒答"解释 | 增设同难度真实题对照组与知识匹配子集分析（AAR A6） |
| 难度配比失衡 | 不可答题仅占 30%，使 `always_do_it`（0.700）成为强策略 | 提高不可答占比并做折扣敏感性（AAR A1） |
| 单 seed、单 prompt | 无误差棒覆盖 prompt 措辞敏感性 | 3 组 prompt 改写 × 3 个 seed（AAR A4） |
| 虚构保证非证明 | 词素构造 + 黑名单是尽力而为 | 已在 README / task说明中明示边界 |
| 自动判分偏差 | 可接受答案列表刻意收窄，**低估** accuracy | 偏差方向已声明；人类侧复核 |

**（4）人类基线：宁缺勿造。** 人类侧交付物只有四件，且**不含任何人类指标数字**：`lenovo_human_baseline_protocol.md`（协议）、`lenovo_human_baseline_template.csv`（**空模板**，仅表头）、`lenovo_human_scoring.py`（与模型侧**共用同一套指标代码**，在空模板上以 `no human data collected` 退出且不写任何文件）、`lenovo_human_baseline_literature.md`（文献参照，明确标注"非本机采集"）。本轮人类数据未采集，因此**人类—模型对比不可得**——这是主动取舍：宁可缺位，不可编造。下一轮按协议招募 10–20 名被试、约 20 分钟即可补齐（AAR A5）。

> **本段评分要点：** 可行性 15%（真实可运行证据 + 诚实局限清单）+ 人类基线考量 20%（范式与文献参照 + 数据缺位的显式声明）；机读口径折算进 `artifactCompleteness` 与 `researchRigor`。

### 3.6 参考文献（18 条，逐条联网核验，通过 18/18）

1. Flavell, J. H. (1979). *Metacognition and cognitive monitoring*. American Psychologist, 34(10), 906–911. https://doi.org/10.1037/0003-066X.34.10.906
2. Maniscalco, B., & Lau, H. (2012). *A signal detection theoretic approach for estimating metacognitive sensitivity from confidence ratings*. Consciousness and Cognition, 21(1), 422–430. https://doi.org/10.1016/j.concog.2011.09.021
3. Fleming, S. M., Weil, R. S., Nagy, Z., Dolan, R. J., & Rees, G. (2010). *Relating introspective accuracy to individual differences in brain structure*. Science, 329(5998), 1541–1543. https://doi.org/10.1126/science.1191883
4. Jin, M., Verhaeghen, P., & Rahnev, D. (2022). *Human confidence in artificial intelligence and in themselves*. Psychonomic Bulletin & Review, 29(4), 1405–1413. https://doi.org/10.3758/s13423-022-02063-7
5. Klayman, J., Soll, J. B., González-Vallejo, C., & Barlas, S. (1999). *Overconfidence in the performance of others*. Organizational Behavior and Human Decision Processes.
6. Lichtenstein, S., Fischhoff, B., & Phillips, L. D. (1982). *Calibration of probabilities: The state of the art to 1980*. In *Judgment Under Uncertainty: Heuristics and Biases*.
7. Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). *On Calibration of Modern Neural Networks*. ICML. arXiv:1706.04599
8. Geifman, Y., & El-Yaniv, R. (2017). *Selective Classification for Deep Neural Networks*. NeurIPS. arXiv:1705.08500
9. Kamath, A., Jia, R., & Liang, P. (2020). *Selective Question Answering under Domain Shift*. ACL. arXiv:2006.09462
10. Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B. (2024). *Can LLMs Express Their Uncertainty?* ICLR. arXiv:2306.13063
11. Kadavath, S., Conerly, T., Askell, A., et al. (2022). *Language Models (Mostly) Know What They Know*. arXiv:2207.05221
12. Lin, S., Hilton, J., & Evans, O. (2022). *TruthfulQA: Measuring How Models Mimic Human Falsehoods*. ACL. arXiv:2109.07958
13. Brier, G. W. (1950). *Verification of forecasts expressed in terms of probability*. Monthly Weather Review, 78(1), 1–3.
14. Chollet, F. (2019). *On the Measure of Intelligence*. arXiv:1911.01547
15. Yin, Z., Sun, Q., Guo, Q., Wu, J., Qiu, X., & Huang, X. (2023). *Do Large Language Models Know What They Don't Know?* Findings of ACL 2023. arXiv:2305.18153
16. Kuhn, L., Gal, Y., & Farquhar, S. (2023). *Semantic Uncertainty*. ICLR. arXiv:2302.09664
17. Azaria, A., & Mitchell, T. (2023). *The Internal State of an LLM Knows When It's Lying*. Findings of EMNLP 2023. arXiv:2304.13734
18. Burnell, R., Yamamori, Y., Firat, O., et al. (2026). *Measuring Progress Toward AGI: A Cognitive Framework*. Google DeepMind technical report.（无 arXiv 编号；年份为 2026，非 2025）

---

## 4. 版本对照表

| 维度 | v1.0 | v2.0 | v3.0 | 变化理由 |
| --- | --- | --- | --- | --- |
| **赛道定位** | 一度倾向 Track 1（"好做"），后修正为 Track 2 | Track 2，理由为认知科学缺口 | Track 2，理由同 v2 并绑定缺口表 | 以"实现便利"替代"问题价值"属推理偏差，被硬约束纠正 |
| **构念定义** | 元认知 ≈ 置信度校准 | 预测性元认知（二阶判断），拆出两成分 | 同 v2，并补充 ΔE 与 \|ΔE\| 并列的机制解释 | 需要与 Flavell 两成分、KSTAR 对齐 |
| **任务族** | KB-A 单阶段；KB-B 自述清单；KB-C 无预算 | KB-A 物理两阶段；KB-B paired 配对；KB-C 预算 6 + 折扣 0.7 | 同 v2，题目实测落盘（60/40/20） | 自述式无可验证 ground truth；单阶段使置信度变事后辩护 |
| **弃答计分** | 单侧 | 双侧 BAS（退化策略封顶 0.5） | 实测 `always_abstain` / `never_abstain` 均 0.500 vs 模型 1.000 / 0.900 | 堵死"一律弃答"的作弊路径 |
| **指标集** | accuracy + ECE（2 个） | 9 个指标 + 派生量 | 9 个指标全部有实测读数 | ECE 可被事后校准压低，必须与排序量并列 |
| **基线** | 仅 `constant_100` | 5 类基线族 | 实测：`constant_50` AUROC2 = 0.500（无信息参照是 0.5 不是 0） | 防止把"低于无信息线"误读成"接近及格" |
| **区间估计** | 无 | item 级 bootstrap 2000 + 成对比较 | 实测 CI 已出（如 AUROC2 0.3869 [0.281, 0.501]） | 小样本下必须写"不可区分"而不是"更好/更差" |
| **校准消融** | 无 | 设计 + **预先写死理论预期** | 实测：ECE 0.5325→0.1689，AUROC2 恰好不变 | 把"预测写下来再验证"，避免事后解释 |
| **创新点写法** | "更全面、更贴近认知科学" | 四点，但部分仍偏形容词 | 每点绑定可复算数字（0.1689/0.3869、+0.8500/−0.9533、−0.8571/−1.0238、0.0588） | 无锚点的形容词无法被检验 |
| **人类基线** | 填入"人类 AUROC2 ≈ 0.65" | 删除全部人类数字，只留协议 | 协议 + 空模板 + 同代码打分脚本 + 文献参照；显式声明未采集 | 触碰"凭空断言"红线；宁可缺位不可编造 |
| **参考文献** | 约 8 条，部分凭记忆 | 约 15 条，未逐条核验 | 18 条逐条联网核验，通过 18/18 | 文献幻觉是研究严谨性的直接失分项 |
| **数值来源** | 无 | "预期 / 待测"占位 | 全部来自 360 次真实调用，逐位对齐 `metrics.json` | 结论必须可追溯 |
| **结构** | 自由体 | 四段式 20/40/20/20，每段标评分要点 | 同 v2，定稿四段式完整 | 对齐赛题提案内部结构要求 |
| **中英术语** | 混用不统一 | 统一术语表 | 术语保留英文、论述用中文 | 命名规范允许纯中文但术语留英文 |

---

## 5. 终版与 C9 实跑数据的对齐点（可复算清单）

| 提案中的断言 | 实测值（e4b / e2b） | 出处 |
| --- | --- | --- |
| KB-A 二阶区分度低于无信息线 | AUROC2 **0.3869 / 0.4408**（`constant_50` = 0.500） | `results/metrics.json` → `kb_a.auroc2` |
| 校准与判别力解耦 | ECE 0.5325→**0.1689** / 0.5152→**0.1267**，AUROC2 不变 | `kb_a.calibration_ablation` |
| ΔE 符号翻转 | multihop **+0.8500 / +0.8233**；fictional **−0.9533 / −0.8600** | `kb_a.per_domain` |
| 全局 signed ΔE 无解释力 | **+0.0558 / +0.0852**，\｜ΔE\｜ 0.5358 / 0.5408 | `kb_a.delta_e` / `abs_delta_e` |
| 边界行为双侧非退化 | BAS **1.000 / 0.900**，退化对照均 0.500 | `kb_b.balanced_abstention_score` |
| over-claim 可分 | **0.000 [0,0]** vs **0.200 [0.048, 0.391]** | `kb_b.over_claim_rate` |
| 求助"会判断、不敢花" | utility **0.5200 / 0.4850**，求助 2 / 1 次（预算 6），normalised **−0.8571 / −1.0238** | `kb_c.utility` / `help_calls` |
| 分域分层诊断 | 分层 3 的 AUROC2 **0.0588**（n=25）；pooled 0.436 / 0.486 | `kb_a.difficulty_strata` |
| 360 次调用 0 失败 | 180 + 180，0 error / 0 空回复 / 0 解析失败 | `logs/run_manifest_full_*.json` |

---

## 6. 尚未解决的偏差与下一次迭代

1. **字数超限偏差（已知并承认）**：赛题建议提案正文 800–1500 字，本定稿正文远长于该区间。取舍是"结论全部有据"优先于"字数达标"；缓解手段是摘要前置（§3.1）可单独抽出作为 1500 字内版本，第 2 部分（3.3）的细节可降为附录。
2. **signed ΔE 的 CI 宽**：+0.0558 [−0.130, +0.230]，只能支持"偏差方向不可判定"，不能支持"轻微过度自信"。
3. **KB-B 的知识 / 元认知混淆**：配对设计控制了格式，但未控制两半实体的**先验知识量**，需按 AAR A6 增设知识匹配子集。
4. **KB-C 经济学过简**：单一求助价（×0.7）与单一预算（6），无时延成本，也不给"在可答题上求助"部分分。
5. **prompt 与 seed 的稳健性未知**：仅单 seed、单 prompt，任何跨设置推断都不成立（AAR A4 计划 3 × 3）。
*（内容由AI生成，仅供参考）*
