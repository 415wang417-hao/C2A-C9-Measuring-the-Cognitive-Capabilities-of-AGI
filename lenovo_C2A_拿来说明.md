---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 60ea5d0126731e33de81577b27285889_357880b1c08e11f1887c525400de85a5
    ReservedCode1: AJ8EGLTlN3GaBhWUlLzaJ+cQaMUaWcVOOEF1WzeSSTOSXwGsI3I7XJ9WJDjSkI7NwRocHdtT9soWSCLpdAg6425hON4MyaWdHSXHsDaBtBxqTAMiztXX+qvR1uSlZBVHr+/KLdWKMkODBooJYI9/DYva6dHCJ+hx9kx/4ElwHypN8kfiuMBMBkx/bFk=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 60ea5d0126731e33de81577b27285889_357880b1c08e11f1887c525400de85a5
    ReservedCode2: AJ8EGLTlN3GaBhWUlLzaJ+cQaMUaWcVOOEF1WzeSSTOSXwGsI3I7XJ9WJDjSkI7NwRocHdtT9soWSCLpdAg6425hON4MyaWdHSXHsDaBtBxqTAMiztXX+qvR1uSlZBVHr+/KLdWKMkODBooJYI9/DYva6dHCJ+hx9kx/4ElwHypN8kfiuMBMBkx/bFk=
---

# lenovo_C2A_拿来说明 — 借鉴来源、取舍与改进

> **作者 / Author:** lenovo
> **挑战 / Challenge:** C2A / C9 — 衡量 AGI 的认知能力
> **赛道 / Track:** Track 2 — Metacognition（元认知）
> **日期 / Date:** 2026-10-05
> **对应提案:** `lenovo_C2A_提案.md`（KnowBound — 预测性元认知三族评测）

KnowBound 不是从零发明的。它的**问题定义**来自赛题资料包的 Track 2 缺口表，**结构**来自 `c2a-starter` 的示例模板，**写作框架**来自 `c2a-proposal-generator` 的 SKILL.md，**方法**来自认知科学与校准研究的一批公开文献。
本文档逐条说明：**拿了什么、去掉什么、改了什么、为什么改**。所有外部文献均经逐条核验（标题 / 作者 / 年份 / venue / 编号），核验不通过者已删除，最终引用 **18 条，全部通过核验**（核验过程与问题条目详见 `lenovo_C2A_AI日志.md` §4）。

---

## 1. 借鉴来源 / References

### 1.1 赛题资料包内的借鉴（本地来源，单列以免与外部文献混淆计数）

| 来源 / Source | 位置 / Location | 核心思想 / Key Idea |
| --- | --- | --- |
| **Track 2 缺口对照表**（`references/track_guidance.md`） | `C:\Users\lenovo\Desktop\C2A-C9 衡量AGI的认知能力_资料包\materials\c2a-starter.zip` → `c2a-starter\c2a-proposal-generator\references\track_guidance.md` | 四行缺口：ECE 校准指标只测概率输出、selective prediction 只测二元决策、verbalized confidence 可被"鹦鹉学舌"式模仿、TruthfulQA 测的是知识而非自我知识；**Key Gap = predictive metacognition**（作答前能否预测自己会成功还是失败） |
| **KSTAR 的 ΔE**（`challenge_spec.md` 五赛道表 + Track 2 段） | 同上 → `references\challenge_spec.md` | ΔE = R̂_E − R_E（预测置信 − 实际置信）；完美元认知 ⇒ 跨多样任务 ΔE ≈ 0；并给出三条推荐角度（pre-answer confidence / knowledge boundary / strategic help-seeking） |
| **`c2a-starter` 的 TestStudent 三份示例交付物** | 同上 → `c2a-starter\TestStudent_C2A_proposal.md`、`TestStudent_C2A_AI日志.md`、`TestStudent_C2A_拿来说明.md` | 四段式提案的**章节骨架**（中英双标题 + 元信息行 + 各节写法要点）、AI 日志的六节骨架、拿来说明的"拿来 / 去掉 / 改进"三分结构 |
| **`c2a-proposal-generator` 的 SKILL.md** | 同上 → `c2a-starter\c2a-proposal-generator.skill` → `c2a-proposal-generator\SKILL.md` | Step 0–6 工作流（取姓名与赛道 → 调研 → 起草 → AI 日志 → 拿来说明 → 打包 → 迭代）、固定提案模板、**10 条交付前质检清单**、命名规范 `{Name}_C2A_{content}.md` |

### 1.2 外部公开文献（链接均可查）

| 来源 / Source | 链接 / Link | 核心思想 / Key Idea |
| --- | --- | --- |
| Google DeepMind (2026), *Measuring Progress Toward AGI: A Cognitive Framework* | [官方 PDF](https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/measuring-progress-toward-agi/measuring-progress-toward-agi-a-cognitive-framework.pdf) | 把通用智能拆成 10 项认知能力；本次赛题的五赛道与 Track 2 缺口表的来源文献（**无 arXiv 编号**） |
| Kaggle × DeepMind 比赛 | [kaggle.com/competitions](https://www.kaggle.com/competitions) | 全球参赛平台与提交口径 |
| Flavell (1979), *Metacognition and cognitive monitoring* | [10.1037/0003-066X.34.10.906](https://doi.org/10.1037/0003-066X.34.10.906) | 元认知两成分：metacognitive knowledge（知道什么）+ metacognitive regulation（监控与调节）；本 benchmark 的构念来源 |
| Maniscalco & Lau (2012), meta-d′ | [10.1016/j.concog.2011.09.021](https://doi.org/10.1016/j.concog.2011.09.021) | 把"元认知效率"从一阶任务表现中**剥离出来**的经典手段；对应本文的分层内再评估 |
| Fleming et al. (2010), Science | [10.1126/science.1191883](https://doi.org/10.1126/science.1191883) | type-2 AUROC 的跨被试个体差异；证明"元认知可被稳定测量且有个体差异" |
| Jin, Verhaeghen & Rahnev (2022), Psychon. Bull. Rev. | [10.3758/s13423-022-02063-7](https://doi.org/10.3758/s13423-022-02063-7) | LLM 置信度校准与人类可比（R ≈ .22）；人类基线预期的锚点 |
| Klayman et al. (1999), OBHDP | [Google Scholar](https://scholar.google.com/scholar?q=Klayman+Overconfidence+in+the+performance+of+others+1999) | 过度精确（over-precision）与自我判断偏差；`fictional` 域欠自信现象的解释框架 |
| Lichtenstein, Fischhoff & Phillips (1982) | [Google Scholar](https://scholar.google.com/scholar?q=Lichtenstein+Fischhoff+Phillips+Calibration+of+probabilities+1982) | 人类"确信 100% 正确"时实际正确率仅 70–85%；为 BAS / ΔE 提供人类参照 |
| Guo et al. (2017), ICML | [arXiv:1706.04599](https://arxiv.org/abs/1706.04599) | ECE 与 temperature scaling；校准消融的直接来源，也是"校准 ≠ 区分度"的对照基础 |
| Geifman & El-Yaniv (2017), NeurIPS | [arXiv:1705.08500](https://arxiv.org/abs/1705.08500) | 弃答 / 覆盖率-风险权衡；KB-B 的 abstention 指标与 BAS 的祖先 |
| Kamath, Jia & Liang (2020), ACL | [arXiv:2006.09462](https://arxiv.org/abs/2006.09462) | 把 selective prediction 用到 QA；"拒答需要一个 calibrated 信号，而不是一个阈值" |
| Xiong et al. (2024), ICLR | [arXiv:2306.13063](https://arxiv.org/abs/2306.13063) | LLM 口头置信度往往弱于内部信号；直接塑造了 KB-A 的"输出前后物理分离"设计 |
| Kadavath et al. (2022) | [arXiv:2207.05221](https://arxiv.org/abs/2207.05221) | 模型自评 P(True) 与真实正确率的对齐；"模型知道自己知不知道"的知名证据 |
| Lin, Hilton & Evans (2022), *TruthfulQA*, ACL | [arXiv:2109.07958](https://arxiv.org/abs/2109.07958) | 用对抗式问题暴露"知识 vs 自我知识"的差别；KB-B 配对虚构实体的知识论来源 |
| Yin et al. (2023), Findings of ACL | [arXiv:2305.18153](https://arxiv.org/abs/2305.18153) | LLM 对"自己不知道什么"的自我认知；**作答前自评**这一探测位置的最新实证 |
| Kuhn, Gal & Farquhar (2023), ICLR Spotlight | [arXiv:2302.09664](https://arxiv.org/abs/2302.09664) | 语义熵：不确定性可由语义层面的不变性估计；解释了"多采样能测不确定性但代价高" |
| Azaria & Mitchell (2023), Findings of EMNLP | [arXiv:2304.13734](https://arxiv.org/abs/2304.13734) | 模型内部状态携带"是否说谎"的信号（SAPLMA）；"内外信号不一致"的证据基础 |
| Brier (1950), Monthly Weather Review | [Google Scholar](https://scholar.google.com/scholar?q=Brier+1950+Verification+of+forecasts+expressed+in+terms+of+probability) | 适当评分规则；报告 Brier 的理由——同时惩罚过自信与欠自信，且不像 ECE 那样依赖分箱 |
| Chollet (2019), *On the Measure of Intelligence* | [arXiv:1911.01547](https://arxiv.org/abs/1911.01547) | "衡量的应是技能获取效率而非技能本身"；"一阶准确率不是主角"这一立场的方法论依据 |

---

## 2. 拿来的部分 / Adopted

### 2.1 从 **Track 2 缺口表**拿了什么（本提案的问题定义）

- **拿了**：四条缺口逐行点名的对象（ECE / selective prediction / verbalized confidence / TruthfulQA），以及它给出的**Key Gap 判断**——"现有 benchmark 测的是模型**能否**表达不确定性，而非它能否**准确**评估自身知识边界"，缺口即 **predictive metacognition**。
- **改造**：我没有停在"缺口表给了个方向"这一层，而是**把四行缺口逐行转化为一条设计约束**，构成提案第 1 节的"逐项回应"：

| 缺口表原文 | 缺口 | 我在 KnowBound 中的对应设计 |
| --- | --- | --- |
| Calibration metrics (ECE) | 只测概率输出，不测行为适应 | KB-A 用 **AUROC2**（排序量，对单调重标定免疫）作头条，ECE 降为辅助；并用消融证明校准改不动判别力 |
| Selective prediction | 只测二元决策，不测细粒度自我知识 | KB-B 用 **paired fictional / real 配对** + **双侧 BAS**，把"该不该拒答"变成有客观真值的判定 |
| Verbalized confidence | 模型可以"鹦鹉学舌"式模仿不确定性 | KB-A 拆成**两次独立调用**：P 阶段禁止作答、只报置信；A 阶段才允许作答 |
| TruthfulQA | 测的是知识，不是自我知识 | 不用它来测知识，而是用它的**对抗构造思想**现造 `fictional` 题（seed 20261005），使其不可能来自预训练记忆 |

- **为什么好用**：缺口表的每一行都是**已发表方法的一个已知失效模式**，把它们当作"必须绕开的坑"比当作"竞争对手"更划算——提案的贡献因此可以被表述为"逐行补缺"，而这正是评分表里"设计创新性 25% + 拿来主义质量 20%"最容易被看见的形式。

### 2.2 从 **KSTAR 的 ΔE** 拿了什么

- **拿了**：`ΔE = R̂_E − R_E`（预测置信 − 实际置信）这一形式化，以及"完美元认知 ⇒ ΔE ≈ 0"的判据；并采纳其推荐的三个角度（pre-answer confidence / knowledge boundary / strategic help-seeking）。
- **改造**：把三条推荐角度**一一映射为三个任务族**（KB-A / KB-B / KB-C），并做了两处关键改造：① ΔE **同时报 signed 与 |ΔE|**（两个模型的 signed ΔE 均跨 0，只有 |ΔE| 揭示真实落差 0.5358 / 0.5408）；② ΔE 不只算全局，还**按域分解**（`multihop` +0.8500 / `fictional` −0.9533），因为全局近零的 ΔE 会掩盖两个方向相反的极端域。
- **为什么好用**：ΔE 本身是一个**无需训练、无需模型内部量**的可计算量，与"每个指标必须能被一段不依赖模型的代码重算"的纪律天然兼容。

### 2.3 从 **`c2a-starter` 的 TestStudent 三份示例**拿了什么

- **拿了**：① 提案的**骨架**——中英双标题 + 元信息行（赛道 / 作者 / 日期）+ 四段结构 + 每节内部的"小节化"写法（2.1 任务描述 / 2.2 为何测目标能力 / 2.3 设计灵感 / 2.4 示例测试项）；② AI 日志的**六节骨架**（工具 / 论文精读 / benchmark 调研 / 提案撰写 / 手动步骤说明 / 段位自评）；③ 拿来说明的**三分结构**（拿来 / 去掉 / 改进）与表格化表达（来源 | 链接 | 核心思想）。
- **改造**：
  - 示例模板的**内容**（Track 1 的"合成规则宇宙"、三阶段学习协议）**一条未用**——它属于 Learning 赛道，与 Track 2 的构念无关；我只吸收了"结构"这一层，这本身即"拿来主义"的应有之义。
  - 在"2.3 设计灵感"之外，把我的版本升级为**"逐项回应缺口表"的对照表**（见 2.1），使"拿来"的痕迹可逐行核对。
  - AI 日志按示例骨架扩充为**三段式主体（拆解 / 迭代 / 边界）+ 文献核验与纠偏汇总**，并加入"失败与纠偏记录"表，把错误当证据保留。
- **为什么好用**：示例交付物给的是**被赛题评审认可过的信息密度**（每节都要有表、有具体数字、有明确取舍），照此骨架填真实内容，能避免"四段俱全但空话连篇"这一最常见的低分形态。

### 2.4 从 **`c2a-proposal-generator` 的 SKILL.md** 拿了什么

- **拿了**：① **Step 0–6 工作流**（确认赛道与想法 → 拿来主义调研 → 起草 → AI 日志 → 拿来说明 → 打包 → 迭代）；② **固定提案模板**的四段划分与"每节至少一个具体示例测试项"的硬要求；③ **10 条交付前质检清单**（字数区间、四段权重、至少 3 个已有 benchmark、KSTAR 连接、创新点句式、可行性诚实、AI 日志如实、命名规范、提交语）；④ **边界情况处理**（只想用中文写 ⇒ 可为纯中文但术语保留英文；已有草稿 ⇒ 不要从零重生成而是找缺口手术式改进）。
- **改造**：
  - 模板中"参考文献"一节的**默认缺失**（示例模板只列 8 条、且无核验要求）被我加强为**强制的逐条核验 + 通过率统计**——提案的 18 条文献全部给出可点击链接并在 AI 日志中记录核验结论。
  - 质检清单的"字数区间"一条按**信息密度优先**处理（见 §4）。
  - 模板面向 Kaggle 提交的英文提案，我按"中文为主、技术术语保留英文"落地（这是 SKILL.md 明确允许的边界情况）。
- **为什么好用**：SKILL.md 提供的不是内容而是**流程与围栏**——它把"研究密集"的部分（调研、结构、支撑论证）标准化，使人可以把精力集中在真正属于自己的洞察上（本提案里即"三族同时上 + 校准与判别力解耦"这一主线）。

### 2.5 从**外部文献**拿了什么（方法与指标）

- **从校准研究（Guo et al. 2017；Brier 1950）**拿了：ECE 的分箱定义、temperature scaling 作为事后校准器、Brier 作为适当评分规则。它们只需一批 `(confidence, correct)` 配对即可计算，可原样复用到本地模型；其已知局限（依赖分箱、对分布敏感）正好用作对照。
- **从选择性预测（Geifman & El-Yaniv 2017；Kamath et al. 2020）**拿了：abstention / coverage-risk 的基本形态与"拒答需要一个信号而非硬阈值"的判断——它把"知道自己不知道"从**自我报告**变成**行为**，从而可客观判分。
- **从 LLM 不确定性（Kadavath 2022；Xiong 2024；Yin 2023；Kuhn 2023；Azaria 2023）**拿了：三条现成的"探测位置"（作答前自评 / 口头置信度的可得性与弱点 / 内外信号可能不一致），并把**输出顺序本身**当作设计变量。
- **从元认知测量（Flavell 1979；Maniscalco & Lau 2012；Fleming 2010）**拿了：type-2 信号检测的**排序**而非绝对刻度（AUROC2）、"元认知效率必须与一阶表现分离"的纪律、以及两成分框架。
- **从 Chollet (2019)** 拿了"衡量的应是能力获取效率而非能力本身"的立场，支撑"一阶准确率不是主角"。

---

## 3. 去掉的部分 / Removed

| 来源 | 他们做了什么 | 我不要 | 原因 |
| --- | --- | --- | --- |
| TruthfulQA（Lin et al. 2022） | 用 817 题对抗式问答做大规模评测 | 不要它的**题面与规模** | 题面一旦公开即进入预训练语料；我只保留"对抗构造"的方法，题目必须现造（seed 20261005） |
| Kadavath et al. (2022) | 依赖模型**内部**信息（P(True)、logit 统计） | 不要任何内部量 | 本 benchmark 必须在**纯黑盒 / 仅文本输出**条件下可复现（8 GB VRAM 也要跑得动） |
| Kuhn et al. (2023) / Xiong et al. (2024) | 采用多轮采样、语义熵 / self-consistency 类估计 | 不要**多次采样聚合** | 采样会把成本乘以 k，且在温度 0 下定义模糊；本 benchmark 坚持"每次判断一次调用" |
| Guo et al. (2017) | 把温度缩放当作**解决方案**报告 | 不要把校准当解法 | 事后单调重标定改不动 AUROC2（实测恰好为 0）；把校准当解法正是本 benchmark 要**反驳**的默认叙事 |
| Geifman & El-Yaniv (2017) | 用**单侧** abstention 阈值做覆盖率-风险曲线 | 不要单侧弃答 | 单侧指标允许"一律弃答"白拿高分；改用 **BAS 双侧计分**（一律弃答与一律作答都封顶 0.5） |
| 缺口表的"四行并列"呈现方式 | 把四条缺口平铺为互不关联的四行 | 不要"平铺"，要**逐行转成设计约束** | 只说"它们都没测 Y"不够，必须给出"我如何测 Y"（见 2.1 对照表），否则创新性无法被验证 |
| TestStudent 示例的 Track 1 内容 | 合成规则宇宙 + 三阶段学习协议 + 学习增益指标 | 不要其**赛道内容** | 属 Learning 赛道，与 Track 2 的构念无交集；只拿结构层 |
| SKILL.md 模板的"英文提案 / 8 条参考文献"默认值 | 面向 Kaggle 的英文短提案 | 不要其**语言与文献量的默认值** | 按赛题允许的边界情况改为"中文为主、术语留英文"；参考文献扩容至 18 条并**逐条核验** |
| 人类校准文献的**观测数值**（Lichtenstein 1982；Jin 2022） | 报告人类实测数字 | 不要把它们当本机基线 | 本机**未采集**人类数据；文献值只作"预期与参照"，并明确标注"非本机采集" |
| 官方博客口径 "A Cognitive Framework" 与论文正文题名 "A Cognitive Taxonomy" 的**混用** | 两个口径并存 | 不要混用 | 统一按赛题资料包口径写作 "A Cognitive Framework"，并在 AI 日志中记录该差异与处置 |

---

## 4. 我的改进 / My Improvements

### 改进 1（核心创新）：把"作答前预测"与"作答后校准"物理分离 —— answer-free confidence probing

- **现有方法的问题**：无论 ECE 还是 verbalized confidence，置信度与答案通常在同一段输出里产生。模型完全可以先写完答案，再给一个"事后合理"的置信度——此时测到的是**自我辩护能力**，不是**预测性元认知**。
- **我的改进**：KB-A 拆成两次独立调用。P 阶段的 prompt 明确禁止作答，模型只看到问题；A 阶段才允许作答。两阶段分别 checkpoint，键为 `(model, item_id, stage)`。
- **效果**：得到本次**最重要的负面发现**——两个模型的 AUROC2 为 **0.3869 / 0.4408**，均**低于"恒定 0.5"这一无信息线**（`constant_50` 与 `constant_100` 的 AUROC2 都恰好是 0.5000），即作答前置信度是**轻度反诊断**的。

### 改进 2：配对虚构 / 真实题 —— 让"知识边界"有可判分的对照组

- **现有方法的问题**：只说"模型会幻觉"无法把"因为不知道所以答错"与"题目本身就不可答"区分开；而单侧弃答指标又允许"一律拒答"白拿高分。
- **我的改进**：KB-B 的 20 题虚构实体与 20 题真实实体**逐题模板配对**（`element_number` / `event_year` / `novel_author` / `capital`），弃答改为**双侧计分 BAS**。
- **效果**：`always_abstain` 与 `never_abstain` 的 BAS 都被封顶在 **0.500**，而两个模型拿到 **1.000 / 0.900**——退化策略被直接排除；同时 e2b 的 over-claim（0.2000，CI [0.0476, 0.3913]）成为一个**可被区间估计**的具体缺陷。

### 改进 3：给元认知加上支付后果 —— 预算化策略性求助

- **现有方法的问题**：弃答类指标里"正确地不答"与"正确地答"代价相同，模型没有动机去区分，元认知退化成一次无成本表态。
- **我的改进**：KB-C 引入**求助预算 6 次**与**折扣 0.7**：对自己答不了的题求助可稳拿 0.7，对答得了的题求助等于把到手的 1.0 换成 0.7；oracle 语义严格定义为"对不可答题给 `UNKNOWN`"，得分 `Utility = mean(score_i)`。
- **效果**：normalised utility 为 **−0.8571 / −1.0238**——两个模型都**不如"永远自己答"**（always_do_it = 0.7000；oracle 上界 0.9100）；且求助 100% 花在不可答题上，却分别只用了 **2 次 / 1 次**（预算 6）——**知道该在哪求助，但不敢用预算**。

### 改进 4：把"校准器买不到元认知"做成可证伪的对照 —— 校准消融

- **现有方法的问题**："提高校准 = 提高元认知"是行业默认叙事，但少有 benchmark 在同一批数据上把两者**同时**测出来。
- **我的改进**：对模型自身置信度做 temperature scaling 与 isotonic，分别报告 ECE 与 AUROC2 的前后变化，并**预先在代码注释中写明理论预期**（单调映射 ⇒ AUROC2 不变；制造 tie ⇒ 有界伪影）。
- **效果**：T = 50 把 ECE 从 **0.5325 / 0.5152 压到 0.1689 / 0.1267**，而 AUROC2 **恰好停在 0.3869 / 0.4408**。**买得到校准，买不到元认知**——这是本交付物最想留下的因果级结论。

### 改进 5：不做全局结论，改做分域分层诊断

- **现有方法的问题**：把"模型过度自信"当作全局结论，会掩盖结构。本次实测 signed ΔE 只有 +0.0558（CI 跨 0），全局过度自信**并不成立**。
- **我的改进**：把 ΔE 与 AUROC2 **按域分解**（arith / fictional / longtail / multihop），并额外做**准确率分层内**再评估（三层）。
- **效果**：暴露出两个方向相反的极端域——`multihop` ΔE **+0.8500**（准确率仅 0.1333，严重过自信）、`fictional` ΔE **−0.9533**（准确率 1.0000，严重欠自信）；分层 3 的 AUROC2 掉到 **0.0588**。这说明"全局 ΔE ≈ 0"是两种相反偏差相互抵消的结果——**分域分层诊断**因此成为第四点创新。

---

## 5. 口径与篇幅的取舍（诚实披露）

| 取舍点 | 选择 | 理由 |
| --- | --- | --- |
| 主指标用 AUROC2 而非 ECE | raw AUROC2 作头条，ECE 作辅助 | AUROC2 是**排序**量，对单调重标定免疫且不依赖分箱；ECE 可被事后校准大幅压低（实测 0.5325 → 0.1689） |
| ΔE 用有符号与绝对值并列 | 两者都报 | 两个模型的 signed ΔE（+0.0558 / +0.0852）都跨 0，只有 \|ΔE\| 揭示真实落差（0.5358 / 0.5408）——只报其一都会误导 |
| 弃答用双侧 BAS 而非单侧 | BAS = 0.5 ×（不可答题弃答率 + 可答题作答率） | 单侧指标允许"一律弃答"拿满分 |
| 模型间差异如何表述 | 以 paired bootstrap 95% CI 是否跨 0 为准；跨 0 一律写"at this n 不可区分" | 防止把 null result 写成胜负（KB-A / KB-C 全族不可区分） |
| 文献值是否进入结果表 | **不进入** | 文献值非本机采集；所有结果数字必须能追溯到 `logs\` 里的一条原始回复 |
| 人类基线 | **主动缺位** | 本机未采集人类数据。宁可缺位，不可编造——人类部分只保留协议与文献参照（标注"非本机采集"） |
| 提案篇幅 | 以**信息密度优先**，正文显著长于赛题建议的 800–1500 字 | 赛题同时要求"逐项回应已有 benchmark 缺口 + 给出可落地实现方案"，而本提案还需承载 C9 阶段已跑通的真实实验（360 次调用、9 个指标、消融表）。因此保留完整公式与数据；若评审要求严格合规，可按四段权重裁剪第 2 节的公式推导与对照表，**结论与数值不受影响** |
| 是否附迭代版本文件 | 不附 | 交付物严格按赛题「必须提交的文件」三件套收口，不额外增删文件 |

---

## 6. 一句话总结

**缺口表给了问题，示例模板给了骨架，SKILL.md 给了流程，文献给了方法；而"三族同时上、用 AUROC2 与 ΔE 把校准和判别力解耦、用预算化求助给元认知加上支付后果、用分域分层拆穿全局近零的假象"——这四件事是本提案自己的。**
*（内容由AI生成，仅供参考）*
