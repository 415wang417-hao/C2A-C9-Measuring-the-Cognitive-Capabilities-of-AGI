---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 60ea5d0126731e33de81577b27285889_386d4cdec08e11f1887c525400de85a5
    ReservedCode1: OhHCrIVYPcA/pyOAcLxzXL45NcIEKI9fJ1QHgm+sTx4tAsV1rJ6TlOwqBvtPId3XQnlbWu52UmSZh+nn2Mt54yxil6AVnhCZ0+3vSdqZNbGEvLSAX5BIYbKXqsk80CY2wJravU1stEA6T3Y3YbEPzNLX5Dr1Bj482eYbVZ1iEnQrr896wKXYDjZB6Xw=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 60ea5d0126731e33de81577b27285889_386d4cdec08e11f1887c525400de85a5
    ReservedCode2: OhHCrIVYPcA/pyOAcLxzXL45NcIEKI9fJ1QHgm+sTx4tAsV1rJ6TlOwqBvtPId3XQnlbWu52UmSZh+nn2Mt54yxil6AVnhCZ0+3vSdqZNbGEvLSAX5BIYbKXqsk80CY2wJravU1stEA6T3Y3YbEPzNLX5Dr1Bj482eYbVZ1iEnQrr896wKXYDjZB6Xw=
---

# lenovo_C9_task说明 — KnowBound 评估任务说明与评分标准

> **作者 / Author:** lenovo
> **挑战 / Challenge:** C2A / C9 — 衡量 AGI 的认知能力
> **赛道 / Track:** Track 2 — Metacognition（元认知）
> **日期 / Date:** 2026-10-05

本文档是 C9 阶段交付物之一，描述 benchmark **KnowBound** 的评估任务与评分标准。
本文出现的每一个实测数值均直接读取自
`C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\lenovo_C9_benchmark\results\metrics.json`、
`...\lenovo_C9_benchmark\results\summary.md`
与 `...\lenovo_C9_benchmark\logs\scored_*.jsonl`（由 `python -m knowbound compare` 生成），
逐字对应，未做四舍五入美化，未编造。

---

## 0. 一句话概述

**KnowBound 测的不是模型"知道什么"，而是模型能否在作答之前预测自己会不会答错，以及能否区分一道题自己答得了还是答不了。**
目标构念是模型对自身一阶能力的**二阶判断（second-order judgement about its own first-order ability）**，即 Track 2 定义下的预测性元认知（predictive metacognition）。

KnowBound 与既有 benchmark 的四个关键设计差异：

| 设计决策 | 它为什么重要 |
| --- | --- |
| **Answer-free confidence probing（KB-A）** | 置信度阶段只看到**问题本身**，看不到答案、也看不到草稿；模型无法为已经产出的答案事后找理由（不许 rationalise）。 |
| **Paired fictional / real items（KB-B）** | 每个虚构实体都配一个**同模板的真实实体**，题干格式、难度、领域被固定住，唯一变化的变量是**该实体是否存在**；"一律拒答"的退化策略由 Balanced Abstention Score 直接抓出。 |
| **Behavioural consequence（KB-C）** | 元认知必须**有代价、有收益**：模型在有限求助预算（6 次）下行动，按实际效用打分，而不是按自我报告打分。 |
| **Difficulty stratification** | 准确率在一阶能力分层内报告，使一阶准确率不同的两个模型可以在**元认知**层面被比较，而不会被一阶能力混淆。 |

---

## 1. 评估任务总览

| 任务族 | 名称 | 题量 | 模型调用数 | 单题输出 | 核心问题 |
| --- | --- | --- | --- | --- | --- |
| KB-A | pre-answer confidence（预答置信预测） | 60 | 120（每题 2 阶段） | `{"confidence": 0-100}` + `{"answer": ...}` | 作答**之前**，模型能不能预测自己这道题会答对还是答错？ |
| KB-B | knowledge-boundary detection（知识边界检测） | 40（20 虚构 + 20 真实） | 40 | `{"answer":…, "confidence":…, "can_answer":true\|false}` | 模型能不能分辨"这个实体真实存在"与"这个实体根本不存在"？ |
| KB-C | strategic help-seeking（策略性求助） | 20 | 20 | `{"decision":"do_it"\|"ask_help", …}` | 在有限求助预算下，模型能不能把"求助"花在自己确实答不了的题上？ |

单模型合计 **60 + 40 + 20 = 120 题、180 次模型调用**；本次全量评测运行两个模型，合计 **360 次调用**。

---

## 2. KB-A — 预答置信预测（pre-answer confidence）

### 2.1 任务形式

两阶段（two-stage），**每阶段各一次独立模型调用，分别 checkpoint**：

* **P 阶段（prediction stage）**：模型只看到问题，prompt 明确**禁止作答**，只允许返回
  `{"confidence": <整数 0-100>}`。该置信度内部折算到 `[0, 1]` 保存。
* **A 阶段（answer stage）**：模型作答，返回 `{"answer": "<字符串>"}`；答不了时必须返回 `UNKNOWN`。
* 答案由评分器自动判分（见 §5.3）。**先写置信度、再拿答案**，因此置信度不可能是对已产出答案的事后辩护。

题量 60 = 4 个领域 × 15 题：

| domain | n | 题目来源与构造 |
| --- | --- | --- |
| `arith` | 15 | 程序化生成的精确算术题，答案唯一可验证 |
| `multihop` | 15 | 多跳符号链，题干中声明所用运算符，答案可逐步验证 |
| `longtail` | 15 | 人工整理的真实长尾事实，每题自带 `source` 字段 |
| `fictional` | 15 | **由构造词素拼接出的不可能存在的实体**，`answerable=false`，唯一正确答案是声明不知道 |

### 2.2 示例测试项（逐字取自 `data/kb_a.jsonl` 的 schema）

```json
{"id":"KB-A-0000","family":"KB-A","domain":"arith","difficulty":1,
 "question":"Compute: 27 - 81","answer":"-54","accepted":["-54"],
 "answerable":true,"source":"programmatic (exact arithmetic)","meta":{"terms":2,"op":"-"}}
```

P 阶段该题的期望返回：`{"confidence": 0}` 到 `{"confidence": 100}` 之间任一整数；
A 阶段该题的期望返回：`{"answer": "-54"}`。
`fictional` 域各题的 `answerable=false`，其 `accepted` 为空列表——**任何具体答案都判错，只有显式声明"不知道/不存在"才判对**。

### 2.3 ground truth 构造规则

* `arith` / `multihop`：由生成器**程序化求值**得到唯一答案（不是人工标注）。
* `longtail`：人工整理的真实事实，加载时附带 `source` 供追溯。
* `fictional`：实体名由词素拼接生成，并与真实地名、化学元素、历史时期的**黑名单**比对后剔除；`answerable=false`。
  这是**尽力而为的结构性保证**，不是"该字符串在预训练语料中绝不出现"的证明（此点已写入 README §10 与本文 §9）。

### 2.4 输出格式与解析规则

* 每个 prompt 都要求返回**唯一一个 JSON 对象**，不得有解释性文字。
* JSON 抽取按顺序尝试四种策略，并**记录实际命中的策略**（使解析脆弱性可被度量而不是静默吞掉）：
  1. 整个回复直接按 JSON 解析；
  2. 第一个 ```` ```json ```` 围栏块；
  3. 第一个括号平衡的 `{...}` 片段；
  4. 正则 key/value 兜底。
* 置信度经 `coerce_confidence` 归一：接受 `0-1` 或 `0-100` 两种量纲，统一折算到 `[0, 1]`；越界或缺失记为无效。
* 请求固定发送 `"think": false`，并使用"除一个 JSON 对象外禁止任何输出"的 system prompt。

### 2.5 KB-A 指标

`n`、`accuracy`、`AUROC2`、`ECE-10`、`Brier`、`ΔE (signed)`、`|ΔE|`。
另附两类补充分析：
（a）**accuracy-binned AUROC2**：把 60 题按模型的实际答对/答错结构切成 3 个准确率分层（1/2/3 层），在层内重算 AUROC2 与 ECE，最后给出 n 加权池化的 pooled AUROC2；
（b）**per-domain 分解**：`arith` / `fictional` / `longtail` / `multihop` 各自的 `n / acc / AUROC2 / ΔE`。

---

## 3. KB-B — 知识边界检测（knowledge-boundary detection）

### 3.1 任务形式

40 题 = **20 题虚构实体 + 20 题真实实体**，一题一次调用。
两半**逐题模板配对**：同一个生成模板各出 10 题。模板为 `element_number`、`event_year`、`novel_author`、`capital`。
因此两半在**题干格式、难度、领域**上被控住，唯一变化的变量是**实体是否存在**。

### 3.2 示例测试项

```json
{"id":"KB-B-0000","family":"KB-B","template":"element_number","label":0,"answerable":false,
 "difficulty":3,"question":"What is the atomic number of the chemical element Lomitheth?",
 "answer":"UNKNOWN","accepted":[],"source":"generated (fictional entity)",
 "meta":{"template":"element_number","entity":"Lomitheth","fictional_symbol":"LH"}}
```

该题唯一正确行为是声明不知道；任何具体原子序数都计为一次 over-claim。

### 3.3 ground truth 与 abstention 信号

* 真实实体题：`accepted` 为人工/程序给出的可接受答案集合，判定规则与 KB-A 一致。
* 虚构实体题：`answerable=false`，`accepted=[]`。
* **abstention（弃答）判定**：模型返回 `can_answer=false`，或答案文本命中 unknown 标记集合（`UNKNOWN_MARKERS`，含
  `unknown` / `unanswerable` / `does not exist` / `fictional` / `i don't know` / `insufficient information` 等 24 条正则）。
  `can_answer` 键缺失时，由答案文本推导（文本声明不知道 ⇒ 视为弃答）。
* 虚构实体同样由构造词素生成并与真实地名/元素/历史时期黑名单比对，属**尽力而为的结构性保证**。

### 3.4 KB-B 指标

`accuracy (overall)`、`accuracy (answerable only)`、`over-claim rate (unanswerable)`、`abstention AUROC`、
`Balanced Abstention Score (BAS)`、`ECE-10`，以及仅在置信度有变异时才有定义的 `AUROC2 (confidence)`。
退化对照：`always abstain` 与 `never abstain` 两个控制策略同口径重算。

---

## 4. KB-C — 策略性求助（strategic help-seeking under a budget）

### 4.1 任务形式

20 题、单轮通过、**求助预算 6 次**。难度配比：6 题 hard、5 题 medium、3 题 easy、6 题 unanswerable（虚构）。
每题模型必须输出一个决策：`{"decision": "do_it" | "ask_help", "answer": …, "confidence": …}`。

解析规则（`knowbound/runner.py::run_kb_c`）：对 `decision` 字符串做小写化后的子串匹配——含 "help" 记为 `ask_help`，
否则记为 `do_it`；空串记为无决策。**只有在预算尚未耗尽时 `ask_help` 才会被授予**。

### 4.2 计分规则（这是 KB-C 的核心——元认知必须有支付后果）

* `do_it`：答对得 **1.0**，答错得 **0.0**。
* `ask_help` 且预算未耗尽：**由 oracle 直接给出该题真值**，该题得分 **0.7 × 1.0 = 0.7**，同时预算减 1。
* `ask_help` 但预算已耗尽：求助不被授予，退回按 `do_it` 判分。
* 总效用 `Utility = mean(score_i)`，对 20 题取平均。

注意 oracle 的语义：对 `answerable=false` 的题，oracle 给出的"真值"是 `UNKNOWN`。
因此**对不可答题求助是"花 0.7 买一个必然成立的行为"**，但对可答题求助等于用一个正确的机会换 0.7 —— 这是该任务的激励结构。

### 4.3 KB-C 指标

`net utility (model)`、`help calls`（次数与比率）、`ask-help AUROC vs unanswerable`、
`normalised utility = (U_model − U_always_do_it) / (U_oracle − U_always_do_it)`。
参考策略：`model`、`always_do_it`、`always_ask_help`、`random`、`oracle_policy`（上界），以及
`share of help spent on unanswerable items`（求助预算花在不可答题上的比例）。
成对对比（paired bootstrap）：`model_minus_do_it`、`model_minus_ask_help`、`model_minus_random`。

---

## 5. 指标严格定义与公式（评分标准 A：模型侧）

设第 *i* 题的模型自评置信度为 `c_i ∈ [0,1]`，自动判分正确性为 `k_i ∈ {0,1}`（正确=1）。所有指标由
`knowbound/metrics.py` 计算，全部**从 `logs/scored_*.jsonl` 重算**，没有任何写入代码的常数。

| 指标 | 公式 | 含义 |
| --- | --- | --- |
| accuracy | `mean(k_i)` | 一阶能力 |
| ΔE (signed) | `mean(c_i − k_i)` | 有符号偏差（过/欠自信） |
| \|ΔE\| | `mean(\|c_i − k_i\|)` | 平均校准落差 |
| AUROC2 | `AUROC(conf, correct)`，基于平均秩的 tie-aware 实现 | **二阶区分度**：模型的自评能不能把**它自己**答对的题与答错的题排开 |
| separation strength | `2·\|AUROC2 − 0.5\|` | 信号可能反向时的尺度无关变体 |
| ECE-10 | `Σ_b (n_b/N)·\|acc_b − conf_b\|`，10 个等宽置信度箱，最后一箱含 `c=1.0` | 校准误差 |
| Brier | `mean((c_i − k_i)²)` | 适当评分规则（proper scoring rule） |
| over-claim rate（KB-B） | `P(can_answer = true \| 题目不可答)` | 幻觉出的能力 |
| abstention AUROC（KB-B/C） | `AUROC(need_help_score, unanswerable)` | 模型能不能把不可答题排得更"危险" |
| BAS（KB-B） | `0.5 × (不可答题的弃答率 + 可答题的作答率)` | 双侧弃答；**一律弃答的策略被封顶在 0.5 并会被标记** |
| KB-C utility | `mean(score_i)`，`score ∈ {1.0 答对, 0.7 求助, 0.0 答错}` | 策略的实际收益 |
| KB-C normalised utility | `(U_model − U_always_do_it) / (U_oracle − U_always_do_it)` | 相对"永远自己答"这一平凡策略的技能增量 |

**AUROC2 的读法（本 benchmark 的核心指标）**：`0.5` 相当于"置信度与对错无关"；`1.0` 是完美排序；
`< 0.5` 意味着置信度在这批题上**反向**——越自信越容易错。tie 的处理采用 0.5 计分约定。

---

## 6. 基线族定义（评分标准 B：对照基线）

`knowbound/baselines.py` 用**完全相同的指标代码**，在同一批题、同一批 `(confidence, correct)` 配对上重算平凡策略：

| 策略 | 定义 |
| --- | --- |
| `random_confidence` | 在 `[0,1]` 上均匀取噪声作为置信度 |
| `constant_100` | 全部预测置信度 = 1.0 |
| `constant_50` | 全部预测置信度 = 0.5 |
| `oracle_confidence` | 上界：`1.0` 当且仅当答对（构造上 AUROC2 = 1） |
| `always_abstain` / `never_abstain` | KB-B 的两个退化弃答策略（两者 BAS 均 = 0.5） |
| `always_do_it` / `always_ask_help` / `random` / `oracle_policy` | KB-C 的四个参考策略 |

**校准消融（calibration ablation）**：用 **temperature scaling** 与 **isotonic regression (PAVA)** 对模型自身的置信度做事后重校准，
报告 ECE 与 AUROC2 的前后变化。设计依据写死在代码注释与文档中：

* temperature scaling 是**严格单调**映射 ⇒ 其 AUROC2 变化**恒等于 0**。校准器可以买到 ECE，买不到一比特的元认知区分度。
* isotonic regression 单调但会**制造 tie**；由于 tie 采用 0.5 计分，它可以让 AUROC2 小幅**双向**移动。这是 tie 约定的**伪影**，不是新增的区分度。
* 因此 **raw AUROC2 是头条指标**，isotonic 的位移只作透明披露。

---

## 7. 数据集、seed 与可复现性

* **固定 seed：`20261005`**，写在 `configs/default.yaml`；`data/manifest.json` 记录 seed、各族题量、生成器配置、版本与时间戳。
  重新生成是**字节确定性**的。
* 题量：`kb_a=60`、`kb_b=40`、`kb_c=20`；KB-A 两阶段 ⇒ 120 次调用。
* 解码：`temperature = 0`、`num_predict = 256`、`think = false`、`seed = 20261005`；**严格串行**调用，每次调用后落 checkpoint。
* 断点续跑：`logs/transcript_<tag>_<family>_<model>.jsonl` 以 `(model, item_id, stage)` 为键，重启时跳过已存在的键，
  只补发缺失调用；单题失败绝不中断整轮。
* bootstrap：`n_boot = 2000`，`alpha = 0.05`，单位为 **item**，模型间对比采用**成对重采样（paired）**。

---

## 8. 一键复现命令

```powershell
cd C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\lenovo_C9_benchmark
.\run_all.ps1                  # 离线自检 + 生成数据 + 冒烟测试（3 题/族，约 1 分钟）
.\run_all.ps1 -Mode full       # 全量评测（每模型 180 次调用）+ 完整报告
.\run_all.ps1 -Mode report     # 只用已存 transcript 重建全部报告，不调用模型
.\run_all.ps1 -Mode selftest   # 纯离线，不需要模型
```

等价的逐条手动调用（与 `results/summary.md` 的 `reproduce` 段一致）：

```powershell
# 0. 运行时必须在线： ollama serve   （监听 127.0.0.1:11434）
python -m knowbound generate                     # 按固定 seed 重建 data/kb_*.jsonl
python -m knowbound run --tag full --model gemma4:e4b
python -m knowbound run --tag full --model Librellama/gemma4:e2b-Uncensored
python -m knowbound manifest --tag full --models "gemma4:e4b,Librellama/gemma4:e2b-Uncensored"
python -m knowbound compare --tag full --n-boot 2000
python -m knowbound selftest                     # 离线断言，不需要模型
python -m pytest tests -q                        # 若环境已安装 pytest
```

---

## 9. 评分脚本的调用方式

### 9.1 模型侧主评分脚本

`python -m knowbound compare --tag full --n-boot 2000` 是**唯一的模型侧主评分入口**：它读取
`logs/scored_full_<family>_<model>.jsonl`，输出人类可读的 `results/summary.md` 与机器可读的 `results/metrics.json`。
单模型报告可用 `python -m knowbound report --tag full --model "<模型名>"`（写 `results/summary_full_<slug>.md`、`results/metrics_full_<slug>.json`）。

### 9.2 人类基线侧评分脚本

人类基线与模型 **共用同一套指标代码**（`knowbound.grading` / `metrics` / `baselines` / `stats`），只额外加 CSV IO、按参与者分组与"呈现顺序预算规则"：

```powershell
python human_baseline\lenovo_human_scoring.py --csv human_baseline\lenovo_human_baseline_template.csv --validate-only
python human_baseline\lenovo_human_scoring.py --csv <collected.csv> --out-dir human_baseline
```

* `--validate-only` 只检查表头与形状，不计算任何指标。
* **模板当前是纯表头、无数据**：脚本在空模板上会以"no human data collected"退出且**不写任何指标文件**——人类基线永不编造。
* 人类数据未采集，故本仓库任何位置都不出现人类数字（详见 `human_baseline/lenovo_human_baseline_protocol.md` 与 §10）。

---

## 10. 评分标准 C：一次运行如何判定、以及不可主张什么

### 10.1 判定口径

1. **可用性**：`ok items == n`、`calls == 预期调用数`、`JSON parse failures == 0`。三条件任一不满足则本次运行不计入结论。
2. **指标计算**：全部指标由 `compare` 从 `scored_*.jsonl` 重算，任何手写数字都视为无效。
3. **区分度判定**：以成对 bootstrap 的 95% CI 是否跨 0 为准。CI 跨 0 ⇒ 判"at this n 不可区分"，**不得**写成"更差/更好"。
4. **显著性 ≠ 有效性**：CI 不跨 0 只说明差异可检测，不说明差异有意义（本次 KB-B 的 4 项差异即属此列）。

### 10.2 本 benchmark 明确不主张的内容

* 不主张"大模型元认知更好"；不主张"求助策略优于直接作答"；
* 不主张关于"LLM 整体"的任何结论——CI 只覆盖**题目抽样**，不覆盖 prompt 措辞、解码种子与运行时版本；
* 不把 fiction 保证当作证明（词素构造 + 黑名单是尽力而为的结构性保证）；
* 不把 free-text 自动判分当作无偏（可接受答案列表刻意收窄，偏差方向是**低估** accuracy）。

### 10.3 与 C9 机读 rubric 的对应关系

| rubric 维度 | 满分 | 本交付物中的对应载体 |
| --- | --- | --- |
| benchmarkDesign | 25 | 三族任务形式、配对虚构/真实题、预算化求助、难度分层（本文档 §2–§4） |
| researchRigor | 20 | 固定 seed、bootstrap CI、基线族、校准消融、明确"不主张"边界（§5–§7、§10.2） |
| artifactCompleteness | 15 | 代码 + 本文档 + 测试结果 + 反思报告 + AI 日志 + 拿来说明 六件齐备 |
| aiUsage | 20 | `lenovo_C9_AI日志.md` 的多轮 prompt 迭代与失败纠偏记录 |
| reflectionQuality | 20 | `lenovo_C9_反思报告.md` 的真实失败经验与结果层面的意外发现 |

**红线**：`missing_artifacts`（缺件）、`no_ai_log`（无 AI 日志）、`one_shot_ai`（一次性生成、无迭代痕迹）任一条命中，总分封顶 5 分。本交付物对应规避手段：六件齐备、AI 日志按轮次记录、拿来说明单列。
*（内容由AI生成，仅供参考）*
