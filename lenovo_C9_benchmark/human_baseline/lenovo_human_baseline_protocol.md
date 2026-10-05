# KnowBound 人类基线采集协议 / Human-baseline collection protocol

> 版本：2026-10-05（与 `data/kb_a.jsonl`、`kb_b.jsonl`、`kb_c.jsonl` 的固定种子版本一一对应，
> 三份题目文件的 sha256 记录在 `logs/run_manifest_full_*.json` 中，采集前必须核对一致，
> 否则人类数据与模型数据不可比）。

**目录内容**

| 文件 | 作用 |
| --- | --- |
| `lenovo_human_baseline_protocol.md` | 本文件：采集协议 + 录入规范 + 分析口径 |
| `lenovo_human_baseline_template.csv` | 空 CSV 模板（仅表头），按本协议录入 |
| `lenovo_human_scoring.py` | 评分脚本，直接 `import knowbound.metrics / grading / baselines`，与模型评测共用同一份度量实现 |
| `lenovo_human_baseline_literature.md` | 已发表文献的参照值（**不是**本机采集的数据） |

**重要声明**：截至本文件生成，**本机未实际采集任何人类被试数据**。本目录提供的是采集与评分的
完整基础设施；`lenovo_human_baseline_literature.md` 中只有可查的文献数值，不得当作本 benchmark
的人类实测结果引用。在 CSV 为空时，评分脚本会明确拒绝输出任何人类指标。

---

## 1. 目的

KnowBound 用三族任务测量"知道边界"的元认知能力（KB-A 作答前预测、KB-B 知识边界识别、
KB-C 预算下的求助决策）。模型侧数字见 `results/summary.md`。人类基线的作用只有一个：
回答"这些指标在人类身上是多少"，从而判断模型分数处在什么位置——而不是"证明人类更强/更弱"。

## 2. 被试与伦理

- 建议 N ≥ 8 名成人被试（母语或熟练使用英文题面），每名被试完成全部 120 个题面
  （KB-A 60 + KB-B 40 + KB-C 20），预计 60–90 分钟；允许分两次完成，但**同一被试的两段之间不得
  讨论题目**。
- 采集前须获得知情同意：说明任务、时长、可随时退出、数据以匿名编号存储；不采集姓名、联系方式等
  可识别信息，`participant_id` 只使用 `P01`、`P02` 形式的编号。
- 被试报酬与被试的作答正确率**无关**（避免激励污染校准测量），可采用固定时薪或固定金额。
- 本协议不涉及临床或敏感内容，题目均为算术、公开事实与虚构实体判断。

## 3. 统一作答规则（三族共用）

1. 全程**不得**使用计算器、搜索引擎、AI 工具或向他人询问；KB-C 的"求助"由主试扮演的
   **Oracle** 提供（见 §3.3），不是外部工具。
2. 置信度一律用 **0–100 的整数**表达："0 = 我确信这个答案是错的 / 我完全不可能答对，
   100 = 我确信答对"。禁止使用"大概""可能"等模糊措辞，必须给数字。
3. 无时间压力，但请尽量凭第一判断作答；记录每题反应时（可选，单位秒，写入 `rt_sec`）。
4. 每题只作答一次，**不得回改**；主试全程不反馈对错（避免跨题学习污染）。
5. 题目按 `data/kb_*.jsonl` 中的 id 升序呈现，同一被试内顺序固定。

### 3.1 KB-A（60 题，两阶段——核心：作答前是否"知道自己会不会"）

对每题依次执行两阶段，**阶段 P 必须在看到任何解题过程之前完成**：

- **阶段 P（预测，不看答案、不动笔）**：读出题面后，直接给出"如果我认真作答，答对的概率"，
  0–100 整数 → 记入 `p_confidence`。
- **阶段 A（作答）**：正式作答，只写最短的最终结果（一个数 / 一个年份 / 一个名称）；
  若认为题目所指对象在现实中不存在或自己确实不会，写 `UNKNOWN` → 记入 `answer`。
  作答后可再问一次"现在你认为刚才答对的概率"→ 记入 `a_confidence`（可选，用于次级分析）。

### 3.2 KB-B（40 题——核心：会不会对不存在的东西编答案）

每题一次作答，同时给出三件事：

- `answer`：简短最终答案，或 `UNKNOWN`；
- `a_confidence`：0–100，**"我刚才给出的这个答案是对的"**的概率；
- `can_answer`：`TRUE` / `FALSE`，"我是否有能力回答这道题"。

> 与模型口径一致：`can_answer = FALSE` 即记为**弃答（abstain）**；若 `can_answer` 留空，
> 评分脚本会按"答案文本是否声明不知道"（与 `knowbound.grading.declares_unknown` 完全相同的
> 正则规则）自动推断。部分题目考查的实体是虚构的，此时"正确答案"就是声明不知道。

### 3.3 KB-C（20 题，预算约束下的求助决策）

规则（**必须在每道题前向被试念一遍**）：

- 每题先选策略：`do_it`（自己答）或 `ask_help`（求助）；
- `do_it`：答对得 **1.0** 分，答错得 **0.0** 分；
- `ask_help`：Oracle 立即给出正确答案，本题**固定得 0.7 分**，但消耗 **1 枚求助令牌**；
- 全程共 **6 枚**令牌，用完即止；**令牌用尽后再说 `ask_help` 无效**，该题按自己作答计分；
- 令牌在题目顺序上先到先用（第 1 题先消耗，第 20 题最后）。

录入：`decision` 填 `do_it` 或 `ask_help`；`answer` 填自己的作答（不许写 Oracle 给的答案）；
`can_answer` 留空；`rt_sec` 可选。**CSV 中同一被试的行顺序即呈现顺序**，评分脚本按该顺序扣减令牌。

## 4. 数据录入规范

- 每行 = 一名被试的一道题；120 题 × N 名被试 = N×120 行。
- 文件编码 UTF-8（允许 BOM），逗号分隔，首行必须是与模板完全一致的列名：

```
participant_id,family,item_id,p_confidence,a_confidence,answer,can_answer,decision,rt_sec,notes
```

| 列 | 适用族 | 取值 | 必填 |
| --- | --- | --- | --- |
| `participant_id` | 全部 | 匿名编号，如 `P01` | 是 |
| `family` | 全部 | `KB-A` / `KB-B` / `KB-C` | 是 |
| `item_id` | 全部 | 必须与 `data/kb_*.jsonl` 的 id 完全一致，如 `KB-A-0007` | 是 |
| `p_confidence` | KB-A | 0–100 整数（阶段 P 预测） | KB-A 必填 |
| `a_confidence` | KB-A / KB-B | 0–100 整数 | KB-B 必填；KB-A 可选 |
| `answer` | KB-A / KB-B | 文本；不会则 `UNKNOWN` | KB-A/KB-B 必填 |
| `can_answer` | KB-B | `TRUE` / `FALSE`（可留空自动推断） | 否 |
| `decision` | KB-C | `do_it` / `ask_help` | KB-C 必填 |
| `rt_sec` | 全部 | 秒，小数 | 否 |
| `notes` | 全部 | 自由文本（会被记录但不参与计分） | 否 |

示例行（仅为格式示例，**不要**放进正式数据文件）：

```
participant_id,family,item_id,p_confidence,a_confidence,answer,can_answer,decision,rt_sec,notes
P01,KB-A,KB-A-0000,85,90,-54,,,6.2,
P01,KB-B,KB-B-0000,,20,UNKNOWN,FALSE,,11.4,
P01,KB-C,KB-C-0000,,,487,,do_it,8.8,
```

异常数据处理：被试中途退出 → 该被试已完成的题保留，缺失题不补 0、不猜答；
`item_id` 不存在或 `family` 与题号前缀不符的行会被脚本记为 `excluded` 并列出原因，不参与计分。

## 5. 计分口径（与模型完全同源）

评分脚本不重新实现任何度量，而是直接调用 benchmark 的模块，保证"同口径"是可验证的：

| 指标 | 实现 | 说明 |
| --- | --- | --- |
| 正确率 | `knowbound.grading.grade_item` + `metrics.accuracy` | 与模型相同的宽松匹配（整词、忽略大小写/变音符）；虚构题的正确答案 = 声明不知道 |
| ΔE / \|ΔE\| | `metrics.delta_e` / `abs_delta_e` | `confidence - correctness` 的均值（偏差） |
| AUROC2 | `metrics.auroc2` | 置信度区分"答对/答错"的 AUROC（并列值按 0.5 计） |
| ECE-10 / Brier | `metrics.ece` / `metrics.brier` | 10 等宽分箱 |
| over-claim rate | `metrics.over_claim_rate` | P(声明能答 \| 实际不可答) |
| Balanced Abstention | `metrics.balanced_abstention_score` | 0.5×(不可答题弃答率 + 可答题作答率)，0.5 为"两种退化策略"的基准 |
| 弃答 AUROC | `metrics.abstention_auroc` | 用 `1 - confidence` 作弃答倾向分数 |
| KB-C 效用与三条基线 | `baselines.kb_c_policies` | `always_do_it` / `always_ask_help`（按题序耗令牌）/ `random`=（两者均值）/ `oracle` 上界 |

分析单位与不确定性：**以"被试×题目"的作答为分析单位**（pooled response-level），
与模型的"以题目为单位"不严格对齐，报告时须并列说明；置信区间用 `knowbound.stats.bootstrap`
（按作答重采样，2000 次，2.5%–97.5% 百分位）。跨被试的个体差异不在此区间内体现。

运行：

```
cd <project root>                                   # .../lenovo_C9_benchmark
python human_baseline/lenovo_human_scoring.py --csv human_baseline/lenovo_human_baseline_data.csv
# 只校验模板/表头而不计分：
python human_baseline/lenovo_human_scoring.py --csv <file.csv> --validate-only
```

输出（写入 `human_baseline/`）：`human_results.json`（全部数字）与 `human_results.md`（可读表格）。
CSV 为空或无有效行时脚本只报告"无数据"，**不会**产出任何指标。

## 6. 已知局限（须与结果一起报告）

1. **样本量小**：N ≥ 8 是被试数下限而非统计功效保证，KB-C 只有 20 题，配对对比的区间会很宽。
2. **被试内重复**：同一被试完成全部题目，题目并非独立观测；pooled 分析会低估不确定性。
3. **动机与熟练度**：人类被试的算术熟练度差异远大于两个同族模型的差异，"人类 vs 模型"
   的对比在这里是描述性的，不是推断性的。
4. **呈现形式不同**：模型看到的是英文 JSON 指令式 prompt，人类看到的是主试口头/纸质呈现与
   CSV 录入，二者的"置信度"采集通道不同，跨主体比较须声明这一差异。
5. **不得外推**：本基线只对这 120 道固定题目有效，不能代表"人类元认知能力"。
