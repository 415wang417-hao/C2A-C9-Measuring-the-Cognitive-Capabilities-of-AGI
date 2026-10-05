---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 60ea5d0126731e33de81577b27285889_39803937c08e11f1887c525400de85a5
    ReservedCode1: gkA+4hvOBXOYh19eYt2Mlr5pppPNVnqYk+9mjP1zPoAVf+e0KfHfZOKd5+ChuIcLyB/QYJjPED4IHC2olIv6FsbaNJhiYoXbjUU0imXxyY+jLQD7RBDkI9LUE63/JYiJ21NQsR8x9WwVmLEEdJZGNbrnIRxswkMJkMJQ5QzcJDu6WMzhejCqMRYP1jw=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 60ea5d0126731e33de81577b27285889_39803937c08e11f1887c525400de85a5
    ReservedCode2: gkA+4hvOBXOYh19eYt2Mlr5pppPNVnqYk+9mjP1zPoAVf+e0KfHfZOKd5+ChuIcLyB/QYJjPED4IHC2olIv6FsbaNJhiYoXbjUU0imXxyY+jLQD7RBDkI9LUE63/JYiJ21NQsR8x9WwVmLEEdJZGNbrnIRxswkMJkMJQ5QzcJDu6WMzhejCqMRYP1jw=
---

# lenovo_C9_测试结果 — KnowBound 全量评测真实数据

> **作者 / Author:** lenovo
> **挑战 / Challenge:** C2A / C9 — 衡量 AGI 的认知能力
> **赛道 / Track:** Track 2 — Metacognition（元认知）
> **日期 / Date:** 2026-10-05

本文档所有数值均为真实实测结果，直接读取自
`C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\lenovo_C9_benchmark\results\metrics.json` 与
`...\results\summary.md`（由 `python -m knowbound compare --tag full --n-boot 2000` 从
`...\logs\scored_*.jsonl` 重算生成），逐字对应，未做四舍五入美化，未编造。
**评测日期 2026-10-05，tag = `full`。**

---

## 1. 环境与模型元信息

| 项 | 值 |
| --- | --- |
| 操作系统 | Windows 11（Build 26200），i7-14650HX，24 GB RAM，RTX 5060 Laptop 8 GB |
| 推理服务 | Ollama **0.35.1**，endpoint `http://127.0.0.1:11434` |
| 模型 A | `gemma4:e4b`，7.5B 参数，**Q4_K_M** 量化 |
| 模型 B | `Librellama/gemma4:e2b-Uncensored`，4.6B 参数，**Q4_K_M** 量化 |
| 解码参数 | `temperature = 0`、`num_predict = 256`、`think = false`、`seed = 20261005` |
| 调用方式 | **严格串行**（参考机推理期间可用内存曾降至约 2.3 GB），每次调用后写 checkpoint |
| 数据集 seed | `20261005`（`configs/default.yaml`，`data/manifest.json` 记录） |
| 题量 | KB-A 60（×2 阶段 = 120 调用）、KB-B 40、KB-C 20 ⇒ 每模型 180 调用 |
| bootstrap | `n_boot = 2000`，`alpha = 0.05`，item 级重采样；模型间为 paired bootstrap |
| 人类基线 | **未采集**（仅有协议、空 CSV 模板、同口径评分脚本与文献参照值） |

来源：`...\logs\run_manifest_full_gemma4-e4b.json`、`...\run_manifest_full_Librellama_gemma4-e2b-Uncensored.json`、`configs/default.yaml`、`data/manifest.json`。

---

## 2. 运行耗时与调用统计

| 模型 | 调用数 | 成功 | 空回复 | JSON 解析失败 | 模型耗时 | 墙钟区间 | 含加载耗时 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `gemma4:e4b` | 180/180 | 180 | 0 | **0（全部 `strict`）** | 137.1 s | 12:18:03 → 12:20:12 | ≈2.3 min（含 9.2 s 模型加载） |
| `Librellama/gemma4:e2b-Uncensored` | 180/180 | 180 | 0 | **0（全部 `strict`）** | 76.0 s | 12:20:21 → 12:21:29 | ≈1.3 min（含 8.5 s 模型加载） |
| **合计** | **360** | **360** | **0** | **0** | 213.1 s | — | ≈3.6 min |

多模型聚合（`compare`）自身耗时 **3.8 s**。加上数据生成、manifest、报告渲染与自检，整个会话远低于 40 分钟预算。

**冒烟切片（`results/smoke_report.md`，3 题/族，12 次调用，非结论性证据，仅证明链路通）**：
9/9 题 OK、12/12 调用成功、0 解析失败；热调用延迟 **0.678 s**（首次 16.824 s 为模型加载）。

---

## 3. 每模型每族完整指标表（含 95% bootstrap CI）

### 3.1 KB-A — pre-answer confidence（n = 60）

| metric | `gemma4:e4b` | `gemma4:e2b-Uncensored` |
| --- | --- | --- |
| accuracy | 0.700 [0.583, 0.817] | 0.650 [0.517, 0.767] |
| **AUROC2** | **0.387 [0.281, 0.501]** | **0.441 [0.311, 0.583]** |
| ECE-10 | 0.533 [0.408, 0.657] | 0.515 [0.398, 0.644] |
| Brier | 0.522 | 0.507 |
| ΔE (signed) | +0.056 [−0.130, +0.230] | +0.085 [−0.094, +0.251] |
| \|ΔE\| | 0.536 | 0.541 |
| pooled accuracy-binned AUROC2 | 0.436 | 0.486 |

### 3.2 KB-B — knowledge-boundary detection（n = 40）

| metric | `gemma4:e4b` | `gemma4:e2b-Uncensored` |
| --- | --- | --- |
| accuracy (overall) | 1.000 [1.000, 1.000] | 0.900 [0.800, 0.975] |
| accuracy (answerable only) | 1.000 | 1.000 |
| **over-claim rate (unanswerable)** | **0.000 [0.000, 0.000]** | **0.200 [0.048, 0.391]** |
| abstention AUROC | 0.750 [0.639, 0.857] | 0.800 [0.684, 0.905] |
| Balanced Abstention Score (BAS) | 1.000 [1.000, 1.000] | 0.900 [0.804, 0.976] |
| AUROC2 (confidence) | n/a（无置信度变异） | 0.656 [0.415, 0.853] |

### 3.3 KB-C — strategic help-seeking（n = 20，预算 6，折扣 0.7）

| metric | `gemma4:e4b` | `gemma4:e2b-Uncensored` |
| --- | --- | --- |
| net utility | 0.520 [0.305, 0.725] | 0.485 [0.270, 0.685] |
| help calls used（budget 6） | 2 | 1 |
| 求助预算花在不可答题上的比例 | 100% | 100% |
| ask-help AUROC vs unanswerable | 0.667 [0.500, 0.875] | 0.583 [0.500, 0.750] |
| normalised utility | −0.857 | −1.024 |

---

## 4. 分域与分层结果（解释"全局均值掩盖了什么"）

### 4.1 KB-A 分域（ΔE 符号翻转）

| domain | `gemma4:e4b` acc / ΔE | `gemma4:e2b-Uncensored` acc / ΔE | 读法 |
| --- | --- | --- | --- |
| `multihop` | 0.133 / **+0.850** | 0.067 / **+0.823** | 最大的**过度自信**区 |
| `fictional` | 1.000 / **−0.953** | 0.933 / **−0.860** | 最大的**欠自信**区（答对了却不敢信） |

结论：**校准误差是领域驱动的，而且会翻转符号**——"模型总是过度自信"这一笼统说法在本数据上是**错的**。全局 ECE（0.533 / 0.515）把这个结构完全抹平了。

### 4.2 KB-A accuracy-binned 分层

在两个模型**一阶准确率可比的层内**重算：pooled AUROC2 为 0.436（e4b）与 0.486（e2b），与未分层的 0.387 / 0.441 同为**低于或接近 0.5**。也就是说，KB-A 的 null result **不能**用"两个模型一阶能力不同"来解释。

---

## 5. 与基线族对比

### 5.1 KB-A 基线（同批题、同一套指标代码）

| policy | e4b AUROC2 / ECE-10 / Brier | e2b AUROC2 / ECE-10 / Brier |
| --- | --- | --- |
| `random_confidence` | 0.426 / 0.386 / 0.396 | 0.466 / 0.370 / 0.380 |
| `constant_100` | 0.500 / 0.300 / 0.300 | 0.500 / 0.350 / 0.350 |
| `constant_50` | 0.500 / 0.200 / 0.250 | 0.500 / 0.150 / 0.250 |
| `oracle_confidence`（上界） | 1.000 / 0.000 / 0.000 | 1.000 / 0.000 / 0.000 |

关键对照：**`constant_50` 恒定给 0.5 就能拿到 AUROC2 = 0.500**，而两个模型分别是 0.387 与 0.441 ——
在这批题上，模型口头声明的置信度**不只是无信息，而是轻度反诊断（anti-diagnostic）**。

### 5.2 KB-B 退化控制

| policy | BAS |
| --- | --- |
| `always_abstain` | 0.500 |
| `never_abstain` | 0.500 |
| `gemma4:e4b` | **1.000** |
| `Librellama/gemma4:e2b-Uncensored` | **0.900** |

两个模型的边界行为是**双侧的**（既敢答可答题、又敢拒不可答题），不是"一律作答"或"一律拒答"的退化策略。

### 5.3 KB-C 参考策略与成对对比

| policy | utility |
| --- | --- |
| `always_do_it` | 0.700 |
| `always_ask_help` | 0.660 |
| `random` | 0.680 |
| `oracle_policy`（上界） | 0.910 |

| 成对对比 | `gemma4:e4b` | `gemma4:e2b-Uncensored` |
| --- | --- | --- |
| model − `always_do_it` | −0.180 [−0.515, +0.205] | −0.215 [−0.565, +0.185] |
| model − `always_ask_help` | **+0.310 [+0.095, +0.515]** | **+0.275 [+0.075, +0.490]** |

两个模型的绝对效用都**低于**`always_do_it`，但与它的 CI **跨 0**；同时二者都显著**高于**`always_ask_help`。

---

## 6. 两模型区分度结论（paired bootstrap，95% CI）

| family | 可区分（CI 不跨 0） | **不可区分（CI 跨 0）** |
| --- | --- | --- |
| KB-A | **none** | accuracy、AUROC2、ECE-10、Brier、ΔE、\|ΔE\| |
| KB-B | ① overall accuracy（−0.100 [−0.200, −0.025]）② BAS（−0.100 [−0.195, −0.025]）③ ΔE（+0.199 [+0.056, +0.376]）④ over-claim（+0.200 [+0.044, +0.375]） | abstention AUROC、accuracy on answerable items、AUROC2、ECE-10 |
| KB-C | **none** | utility、help-call rate、ask-help AUROC、以及全部三个策略对比 |

**结论**：小模型"uncensored"版本的劣势**只出现在 KB-B（知识边界）**，在 KB-A（预答置信）与 KB-C（策略性求助）上**统计不可区分**。
且 KB-B 的差距"与一个纯知识/一阶能力的解释是相容的"——因此**不能**据此主张"大模型元认知更好"。

---

## 7. 校准消融对照表（calibration ≠ metacognition）

| model | stage | ECE-10 | AUROC2 | Brier |
| --- | --- | --- | --- | --- |
| e4b | raw | 0.5325 | 0.3869 | 0.5218 |
| e4b | + temperature scaling (T = 50) | **0.1689** | **0.3869**（完全不变） | 0.2550 |
| e4b | + isotonic (PAVA) | 0.2660 | 0.4365 | 0.2877 |
| e2b | raw | 0.5152 | 0.4408 | 0.5071 |
| e2b | + temperature scaling (T = 50) | **0.1267** | **0.4408**（完全不变） | 0.2563 |
| e2b | + isotonic (PAVA) | 0.1917 | 0.5183 | 0.2840 |

读法：
* temperature scaling 把 ECE 压低 **0.36–0.39**，同时把 AUROC2 移动**恰好 0**（严格单调映射的数学必然）。
  即：**校准器可以买到"看起来校准了"，买不到一比特的元认知区分度。**
* isotonic 的 AUROC2 位移（+0.0496 / +0.0775）来自**它制造的 tie 在 0.5 计分约定下得到的额外半分**，属**约定伪影**，不是新增区分度。
* 诚实披露：两个校准器都是**在同一批题上拟合并评估**的，因此上表的事后 ECE 是**乐观的**；该消融的目的是**不变性对照**，不是头条 ECE。

---

## 8. 明确标注：不可区分的指标与样本量不足的部分

**不可区分（不得写成"更好/更差"）**
1. KB-A 全部指标（含 AUROC2、ECE-10、Brier、ΔE）——两模型 CI 全部跨 0。
2. KB-C 全部指标（utility、help-call rate、ask-help AUROC、三个策略对比）——CI 全部跨 0。
3. KB-B 的 abstention AUROC、answerable-only accuracy、AUROC2、ECE-10。
4. KB-B 的 4 项差异虽然 CI 不跨 0（可检测），但**不足以支撑"元认知更强"的主张**（与纯知识解释相容）。

**样本量不足 / 定义受限**
1. **KB-C 只有 n = 20**（预算 6），utility 的 CI 宽度约 ±0.21（e4b 0.520 [0.305, 0.725]），对 0.02 量级的策略差异没有分辨力。
2. **KB-A `multihop` 仅 15 题**，且准确率低至 0.133 / 0.067，ΔE 的大幅正值主要来自这一域；`fictional` 域 15 题准确率触顶。
3. **KB-A `fictional` 域 accuracy = 1.000 ⇒ 该域 AUROC2 无定义**（正负样本只有一类）；**KB-B e4b 的 AUROC2 = n/a**（置信度无变异）。这两处不是"表现好"，是**指标不可计算**。
4. **单轮、单 prompt、单次生成**：未做 prompt 改写、seed 方差或量化档位研究，因此**不对稳定性作任何主张**；冒烟切片只是链路证据。
5. CB 只覆盖**题目抽样**（item-level），不覆盖 prompt/解码/运行时的不确定性；`n = 60/40/20` 是每族的题量上限。
6. **人类基线未采集**：仓库中不含任何人类数字，人类—模型对比**在本轮不可得**。

---

## 9. 数据出处对照

| 数据 | 来源文件 |
| --- | --- |
| 头条指标、CI、基线、消融、两模型对比 | `...\lenovo_C9_benchmark\results\metrics.json`、`...\results\summary.md` |
| 逐题原始模型 I/O（含 latency、parse strategy） | `...\logs\transcript_full_{kb_a,kb_b,kb_c}_{model}.jsonl` |
| 逐题判分记录（confidence / correct / decision / points） | `...\logs\scored_full_{kb_a,kb_b,kb_c}_{model}.jsonl` |
| 运行时与量化信息 | `...\logs\run_manifest_full_*.json` |
| 冒烟链路证据 | `...\results\smoke_report.md` |
| 题量与 seed | `...\data\manifest.json`、`...\configs\default.yaml` |
*（内容由AI生成，仅供参考）*
