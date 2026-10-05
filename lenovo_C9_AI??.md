---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 60ea5d0126731e33de81577b27285889_3ba0729bc08e11f1887c525400de85a5
    ReservedCode1: oxboPcYytqVsHyX62d/qQY7F2tkysGJ57XXhwk6U/C6QO7ytEdwLh6WDVvDxzTDrsgfU1wcpTGBWCen4qnzLxAtLGK2hE07vcVEwkntVt8eBirbTx/LHOBvfNDUC7gKmXSFemOL7SbAZQzUeWudS7GFi9W6B9u783tv+EKI/tmkCG0NKA812VrsmU/w=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 60ea5d0126731e33de81577b27285889_3ba0729bc08e11f1887c525400de85a5
    ReservedCode2: oxboPcYytqVsHyX62d/qQY7F2tkysGJ57XXhwk6U/C6QO7ytEdwLh6WDVvDxzTDrsgfU1wcpTGBWCen4qnzLxAtLGK2hE07vcVEwkntVt8eBirbTx/LHOBvfNDUC7gKmXSFemOL7SbAZQzUeWudS7GFi9W6B9u783tv+EKI/tmkCG0NKA812VrsmU/w=
---

# lenovo_C9_AI日志 — KnowBound 开发全过程 AI 使用记录

> **作者 / Author:** lenovo
> **挑战 / Challenge:** C2A / C9 — 衡量 AGI 的认知能力
> **赛道 / Track:** Track 2 — Metacognition（元认知）
> **日期 / Date:** 2026-10-05

本日志记录 C9 阶段从需求拆解到六份交付物落盘的全过程中，AI 在每一轮被要求做什么、产出了什么、哪里错了、怎么修。
**不是一句话流水账**：每一轮按"目标 → prompt 要点 → 输出问题 → 如何修正"四段写清。

---

## 1. 工具与分工

| 角色 | 具体承担 | 不承担 |
| --- | --- | --- |
| AI 助手（本地文件智能助手，具备本地文件读写、代码生成与执行、联网检索能力） | 需求拆解、benchmark 设计与代码实现、数据生成、报告渲染、结果解读、文档撰写、文献核验 | 不能替代人类做"该不该报这个 null result"的价值判断 |
| 本地推理服务 Ollama 0.35.1（`gemma4:e4b`、`Librellama/gemma4:e2b-Uncensored`） | 作为**被测对象**产生 360 次真实调用 | 不是开发工具，不参与任何代码或文档生成 |
| 联网深度检索 | 文献真实性核验（两轮共 21 条候选） | 不用于生成数值 |
| 本地脚本 / 命令行 | 文件系统操作、路径核对、字数统计、一致性检查 | — |

**分工原则**：数值只能来自 `logs/` 与 `results/`；AI 可以写代码去**采集**数字，但**不许"想"出数字**。这条边界是本日志所有"输出问题"的判定依据。

---

## 2. 时间线：多轮 prompt 迭代

### 第 0 轮 — 需求拆解与赛道定位
* **目标**：把"用户参赛、要 95 分"这一粗糙输入，压成可执行的交付清单。
* **prompt 要点**：请读取资料包的 `CHALLENGE.md`、`评分标准.md`、`rubric.json`，列出 C9 阶段的必交物、命名规范与红线扣分项。
* **输出问题**：首轮回答把 C2A 与 C9 的交付物混在一起，且把"六件文档"记成"五件"（漏了 AAR）。
* **如何修正**：要求 AI **逐字引用 rubric.json 的字段名与分值**再回答，并强制输出"文件名 → 是否存在 → 缺口"三列表。C2A 部分从本任务范围中显式剥离（本任务只产出 C9 六份）。

### 第 1 轮 — 任务族与构念设计
* **目标**：把 Track 2 的缺口（"现有 benchmark 测模型**能否**表达不确定性，而非它能否**准确**评估自身知识边界"）落成三个可测任务族。
* **prompt 要点**：围绕"预测性元认知"设计三族；要求每族同时给出任务形式、ground truth 来源、以及**一个具体示例题 JSON**；要求回答"如果模型使用退化策略会怎样"。
* **输出问题**：AI 首版提出"让模型列出自己知道/不知道的清单"，但**没有任何可验证的 ground truth**，属于自述式证据，无法判分。
* **如何修正**：加了一条硬约束——"每个指标必须能被一段不依赖模型的代码重算"。知识边界因此改为 **paired fictional/real 配对设计**（同模板、实体真假互换），让"该不该拒答"变成有客观真值的判定。

### 第 2 轮 — 代码骨架与数据生成
* **目标**：生成 `knowbound` 包（generate / prompts / models / grading / metrics / calibrators / baselines / stats / runner / report / compare / manifest / selftest / config / `__main__`）。
* **prompt 要点**：要求"每个模块顶部写清职责与不可动摇的口径"；要求 metric 定义**以 docstring 形式**写进代码；要求固定 seed。
* **输出问题**：AI 首版把置信度内部量纲直接定为 `0-100`，而后续指标公式 `(c−k)²` 隐含 `[0,1]`，量纲不一致会静默产生错误的 Brier 与 ΔE；且 AI 首版把 60 题写成"随机抽样"，破坏了可复现性。
* **如何修正**：内部统一 `[0,1]`、入口统一经 `coerce_confidence` 归一；数据改为**生成器 + 固定 seed 20261005 + manifest 记录**，使重建字节确定。

### 第 3 轮 — 首轮整批调用失败 → 纠偏
* **目标**：跑通第一次真实调用。
* **prompt 要点**：直接执行冒烟切片。
* **输出问题**：`ConnectionError (WinError 10061)`，整批失败——**Ollama 没在监听**。AI 事后一度把原因叙述成"模型不支持"，属**错误归因**。
* **如何修正**：要求 AI 先把原始报错逐字贴出再解释（禁止跳步归因）；`run_all.ps1` 增加端口探测与明确提示；runner 改为**每次调用先写 checkpoint**，失败也留痕，并支持按键跳过已完成的 `(model, item_id, stage)`。

### 第 4 轮 — 自检断言错误 → 纠偏
* **目标**：建立不依赖模型的离线断言（`python -m knowbound selftest`）。
* **prompt 要点**：给校准器写断言，验证"校准不制造元认知"。
* **输出问题**：AI 写的断言是"isotonic 校准永不改变 AUROC2"，实测被自己的数据推翻（+0.0496 / +0.0775）。
* **如何修正**：要求 AI 解释"为什么断言会被推翻"，而不是直接删断言。定位到根因是 isotonic 产生 tie、tie 在 0.5 计分下影响秩和。断言改为**有界位移**，并在 README 与本文档中把该位移标注为**伪影**。这是本日志中"AI 的错误被保留下来当证据"的一条。

### 第 5 轮 — 报告虚报解析失败 → 纠偏
* **目标**：让冒烟报告如实反映链路质量。
* **prompt 要点**：输出每次调用的解析策略分布。
* **输出问题**：报告把 6 条 P 阶段记录（本就没有答案阶段，故无 `parse_strategy_a` 键）计成 parse failure，**虚报 6 例失败**。
* **如何修正**：要求 AI 说明"这个数字的分母是什么"；改为按 stage 分别统计，并把空回复数单列。全量运行最终报告：`calls == 180/180`、`empty == 0`、`parse failures == 0`。

### 第 6 轮 — 全量评测执行
* **目标**：两模型各 180 次调用，产出可引用的头条数字。
* **prompt 要点**：串行执行、0 温度、每次调用落 checkpoint；跑完立即 `compare --n-boot 2000`。
* **输出结果（真实）**：e4b 墙钟 12:18:03 → 12:20:12（模型耗时 137.1 s），e2b 12:20:21 → 12:21:29（模型耗时 76.0 s）；合计 360 次调用、0 失败、0 解析失败；多模型聚合 `compare` 耗时 3.8 s。
* **输出问题**：AI 首版报告把"冷启动加载（约 9 s）"混进单次调用成本，使每调用成本看起来贵约 5 倍。
* **如何修正**：要求把冷/热延迟分开报告（冒烟切片：热 0.678 s vs 首次 16.824 s）。

### 第 7 轮 — 结果解读（本轮的关键纠偏）
* **目标**：解释 KB-A 的 AUROC2 < 0.5。
* **prompt 要点**：给出原始数值，要求三种解释并各自给出可判定的证据。
* **输出问题**：AI 首版给出"模型过度自信导致"这一**全局结论**，但其实测 ΔE 只有 +0.056（CI 跨 0），全局过度自信并不成立；真正的结构在分域（`multihop` +0.850 / `fictional` −0.953）。
* **如何修正**：要求 AI **先做分域分解再下结论**，并把"两模型 CI 全部跨 0 ⇒ 不可区分"写进结论，禁止把 null result 写成胜负。

### 第 8 轮 — 人类基线材料
* **目标**：给出可落地的人类基线。
* **prompt 要点**：写协议 + CSV 模板 + 同口径评分脚本 + 文献参照。
* **输出问题**：AI 一度直接填入"人类 AUROC2 ≈ 0.65"这类数字。
* **如何修正**：明令"**人类数据未采集 ⇒ 仓库里不许出现人类数字**"。改为：模板留空、脚本在空表上拒绝出数且不写文件、文献值单独标注"非本机采集、仅作参照"。

### 第 9 轮 — 文献核验（两轮，共 21 条候选）
* **目标**：拿来说明中的每一条文献都必须真实可查。
* **prompt 要点**：逐条核验"标题 / 作者 / 年份 / venue"是否一致，不一致必须给出正确版本或删除。
* **输出问题**：见 §6——首轮浮出 4 条不实（Wokke 2022 作者与 DOI 对不上、Moore 2020 并非期刊综述、Lin/Mausam/Doshi 2022 作者张冠李戴、Read 1998 venue 与原始表述不符），另有 2 条需修正（Jin 2022 页码、Fleming 2010 venue 实为 Science）。
* **如何修正**：删除不实的 4 条；修正的 2 条按核验结果写；最终**只引用核验通过的 14 条**。本条即"防止文献幻觉"的落地。

### 第 10 轮 — 六份文档撰写与一致性核对
* **目标**：产出六份文档且互不矛盾。
* **prompt 要点**：每份开头写元信息块；所有数字标注来源文件；写完后做一次交叉核对。
* **输出问题**：AI 初稿在 `测试结果` 与 `反思报告` 里对"报告虚报解析失败"的条数描述不一致（6 例 vs "若干"），且在 `task说明` 中误写了一条不存在的子命令。
* **如何修正**：要求以 `logs/` 与 `results/` 为唯一真值做交叉表核对；子命令改为**实际核对过**的 `generate / run / smoke / report / compare / manifest / selftest`。

---

## 3. 工作流设计与工具分工（结构性说明）

```
需求拆解 → 构念设计 → 代码实现 → 数据生成（seed 20261005）
   → 离线自检(selftest) → 冒烟(smoke, 3题/族) → 全量(run, 180调用/模型)
   → 聚合(compare, n_boot=2000) → 结果解读 → 文档撰写 → 交叉一致性核对
```

* **产物分层**：`data/`（可重建）→ `logs/`（原始 I/O 与判分，只追加）→ `results/`（由 logs 重算，可随时丢弃重建）。
  这条分层让"所有数字可追溯到一条原始回复"成为结构保证，而不是纪律要求。
* **可复现设计**：固定 seed + 字节确定生成 + checkpoint 断点续跑 + `-Mode report` 纯离线重建。
* **成本控制**：8 GB VRAM 下**严格串行**、`num_predict=256`、`think=false`；KB-A 用"只问置信度"的 P 阶段，避免长推理开销。

---

## 4. 失败与纠偏记录（汇总）

| # | 失败 | 根因 | 修复 | 是否留下可见痕迹 |
| --- | --- | --- | --- | --- |
| 1 | 首轮整批调用失败 | Ollama 未监听，AI 误归因于"模型不支持" | 端口探测提示 + 每次调用先写 checkpoint | 是（日志与文档均记录） |
| 2 | 自检断言错误 | 未预见 isotonic 制造 tie | 断言改为有界位移，位移标注为伪影 | 是（消融表单独列 isotonic 行） |
| 3 | 报告虚报 6 例解析失败 | 两阶段 checkpoint 混算，分母不清 | 按 stage 分算 + 空回复单列 | 是（本日志保留该错误） |
| 4 | 单次调用成本高估约 5 倍 | 冷启动未分离 | 冷/热延迟分开报告 | 是 |
| 5 | 人类基线一度出现编造数字 | AI 用文献值冒充采集值 | 模板留空 + 脚本拒出数 + 标注非本机采集 | 是（明确声明未采集） |
| 6 | 4 条文献不实 | 文献幻觉 | 逐条核验后删除 | 是（§6 列出） |
| 7 | 六份文档初稿互相不一致 | 未做交叉核对 | 建立"以 logs/results 为唯一真值"的核对表 | 是 |

---

## 5. 人工判断介入点（哪些事 AI 不做，是人定的）

1. **是否报告 null result**：KB-A 的 AUROC2 < 0.5 是一个"不好看但是真的"结果。决定**照实报告并把它作为主要发现**，是人的判断。
2. **校准 ≠ 元认知的定位**：把温度缩放"ECE 大降、AUROC2 不变"提升为全篇核心论点，是人定的叙事优先级。
3. **人类基线宁缺勿造**：AI 曾提出用文献值"估算"人类数字，被明确否决。
4. **文献取舍**：核验发现 4 条不实后，决定删除而不是"改个年份继续用"。
5. **不主张边界**：明确禁止把 KB-B 的 4 项可检测差异写成"大模型元认知更好"。
6. **不被指标牵着走**：决定保留 isotonic 这一"看起来能提升 AUROC2"的对照并把它标成伪影，而不是删掉这个不好解释的行。

---

## 6. 文献核验过程与结果（两轮，21 条候选 → 引用 14 条）

**核验方式**：对每一条候选，用联网深度检索核对"标题 / 作者 / 年份 / 发表 venue / arXiv 编号"五项是否一致；不一致者标为不通过。
**核验纪律**：核验不通过的**必须替换或删除**，不允许"差不多就引用"。

### 6.1 通过并引用（14 条，全部通过）

| 文献 | 核验结果 |
| --- | --- |
| Flavell (1979), *Metacognition and cognitive monitoring*, American Psychologist | 通过 |
| Maniscalco & Lau (2012), meta-d′，Consciousness and Cognition | 通过 |
| Fleming et al. (2010), *Relating introspective accuracy…*，**Science** | 通过（venue 修正：原写 Frontiers，实为 Science） |
| Klayman et al. (1999), Organizational Behavior and Human Decision Processes | 通过 |
| Lichtenstein, Fischhoff & Phillips (1982)，收于 *Judgment Under Uncertainty* | 通过 |
| Jin, Verhaeghen & Rahnev (2022), Psychonomic Bulletin & Review **29(4)**:1405–1413 | 通过（页码修正） |
| Guo et al. (2017), *On Calibration of Modern Neural Networks*，ICML | 通过 |
| Geifman & El-Yaniv (2017), *Selective Classification for Deep Neural Networks*，NeurIPS | 通过 |
| Kamath, Jia & Liang (2020), *Selective Question Answering under Domain Shift*，ACL，arXiv:2006.09462 | 通过 |
| Xiong et al. (2024), *Can LLMs Express Their Uncertainty?*，ICLR，arXiv:2306.13063 | 通过 |
| Kadavath et al. (2022), *Language Models (Mostly) Know What They Know*，arXiv:2207.05221 | 通过 |
| Lin, Hilton & Evans (2022), *TruthfulQA*，ACL，arXiv:2109.07958 | 通过 |
| Brier (1950), Monthly Weather Review 78(1):1–3 | 通过 |
| Chollet (2019), *On the Measure of Intelligence*，arXiv:1911.01547 | 通过 |

### 6.2 核验发现的问题条目（7 条，均已处置）

| 候选 | 核验结论 | 处置 |
| --- | --- | --- |
| Wokke et al. (2022), *Journal of Vision* | **不通过**（该 DOI 对应作者为 Davidson 等，作者不实） | **删除** |
| Moore (2020) | **不通过**（并非同行评审期刊综述，实为著作 *Perfectly Confident*） | **删除** |
| Lin, Mausam & Doshi (2022) | **不通过**（作者张冠李戴，与 TruthfulQA 作者混淆） | **删除** |
| Read et al. (1998) | **不通过**（venue 与原始表述不符，实为书章） | 修正后**未引用** |
| Yoshizawa et al. (2026), Frontiers in Artificial Intelligence | 文章真实存在，但**无 meta-gamma 相关内容**，原主题描述不实 | 修正描述后**未引用** |
| Miller et al. (2015) | 通过（r ≈ .15），与本文主题非核心 | 通过但**未引用** |
| Sporer et al. (1995), Psychological Bulletin | 通过，记忆置信度主题非核心 | 通过但**未引用** |

**统计**：候选 **21** 条 → 核验**通过** 14 条 + 通过未引用 2 条 + 修正后未引用 1 条 + 删除 4 条（不通过与"主题不实"合并计 4 条：Wokke、Moore、Lin/Mausam/Doshi、Yoshizawa）。
**最终引用 14 条，核验通过 14 条（通过率 14/14）。** 没有一条未核验的文献进入交付物。

---

## 7. AI 段位自评

**🟣 驾驭（Orchestration）**

理由：
1. **AI 承担了完整的工程流水线**——从构念设计、代码实现、数据生成、断点续跑，到自动报告、消融实验与文档撰写，并且**每一环都能被离线复算**（`selftest` + `-Mode report`）。这不是"让 AI 写一段代码"，而是把 AI 放进一个有验证闭环的系统里。
2. **人类的判断被显式插在关键位置**（§5 六条）：该不该报 null result、该不该造人类数字、该不该删除不实文献、该不该把 isotonic 位移标成伪影。这些是 AI 不会自己做的价值判断，也正是"驾驭"与"被 AI 驾驭"的分界。
3. **AI 的错误被保留成证据**：误归因、错断言、虚报解析失败都写进了本日志与反思报告，而不是被清理掉——这说明协作方式是"人审查 AI"，而非"AI 输出、人签收"。
4. **未达 🔴 创造**：本轮的构念与三个任务族**全部在人类设定的框内**（Track 2 缺口 + KSTAR ΔE 对齐 + "指标必须能被代码重算"），AI 的贡献是高质量的工程化与自我批判，不是从零提出新的元认知理论。诚实地说，这里是 🟣，还不是 🔴。
*（内容由AI生成，仅供参考）*
