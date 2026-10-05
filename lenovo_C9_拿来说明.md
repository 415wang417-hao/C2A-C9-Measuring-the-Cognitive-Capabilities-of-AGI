---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 60ea5d0126731e33de81577b27285889_3c90534bc08e11f1884b525400cd780f
    ReservedCode1: ts8vtgirDTpr9bMSRd1aJBJBrDm3PinWT/JcWXawNXEZ224ov1AmFLhAWFmOEWMQ4eyW2jVaIemeiq9XcmSlqdMjliBUS1lm37GFKEr0/QKyFWLE4uk0bN9/OTe1RTJ3otcOog8S6Buf17i99ooyMTOCuP93wJDfrM4kC2iIpiBbNgwMIHQTUqsnmhg=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 60ea5d0126731e33de81577b27285889_3c90534bc08e11f1884b525400cd780f
    ReservedCode2: ts8vtgirDTpr9bMSRd1aJBJBrDm3PinWT/JcWXawNXEZ224ov1AmFLhAWFmOEWMQ4eyW2jVaIemeiq9XcmSlqdMjliBUS1lm37GFKEr0/QKyFWLE4uk0bN9/OTe1RTJ3otcOog8S6Buf17i99ooyMTOCuP93wJDfrM4kC2iIpiBbNgwMIHQTUqsnmhg=
---

# lenovo_C9_拿来说明 — 借鉴来源、取舍与改进

> **作者 / Author:** lenovo
> **挑战 / Challenge:** C2A / C9 — 衡量 AGI 的认知能力
> **赛道 / Track:** Track 2 — Metacognition（元认知）
> **日期 / Date:** 2026-10-05

KnowBound 不是从零发明的。它的每一个部件都能追溯到一项已有的 benchmark、度量或认知科学范式。
本文档逐条说明：**拿了什么、去掉了什么、改了什么、为什么改**。所有文献均经逐条核验（标题 / 作者 / 年份 / venue / arXiv 编号），
核验不通过者已删除，最终引用 **14 条，全部通过核验**（核验过程与不通过条目详见 `lenovo_C9_AI日志.md` §6）。

---

## 1. 借鉴来源 / References

| 来源 / Source | 链接 / Link | 核心思想 / Key Idea |
| --- | --- | --- |
| Flavell (1979), *Metacognition and cognitive monitoring* | [10.1037/0003-066X.34.10.906](https://doi.org/10.1037/0003-066X.34.10.906) | 元认知两成分：metacognitive knowledge（知道什么）+ metacognitive regulation（监控与调节）；本 benchmark 的构念来源 |
| Maniscalco & Lau (2012), meta-d′ | [10.1016/j.concog.2011.09.021](https://doi.org/10.1016/j.concog.2011.09.021) | 把"元认知效率"从一阶任务表现中**剥离出来**的经典手段；对应本文的"分层内再评估" |
| Fleming et al. (2010), *Relating introspective accuracy to individual differences in brain structure*（Science） | [10.1126/science.1191883](https://doi.org/10.1126/science.1191883) | type-2 AUROC 的跨被试个体差异；提供了"元认知可被稳定测量且有个体差异"的证据 |
| Jin, Verhaeghen & Rahnev (2022)（Psychon. Bull. Rev. 29(4):1405–1413） | [10.3758/s13423-022-02063-7](https://doi.org/10.3758/s13423-022-02063-7) | AI 的置信度校准与人类可比（R ≈ .22）；人类基线预期的锚点 |
| Klayman et al. (1999)（OBHDP） | [Google Scholar 检索](https://scholar.google.com/scholar?q=Klayman+Overconfidence+in+the+performance+of+others+1999) | 过度精确（over-precision）与"我答对了吗"的自我判断偏差；`fictional` 域欠自信现象的解释框架 |
| Lichtenstein, Fischhoff & Phillips (1982), *Calibration of probabilities* | [Google Scholar 检索](https://scholar.google.com/scholar?q=Lichtenstein+Fischhoff+Phillips+Calibration+of+probabilities+1982) | 人类在"确信 100% 正确"时实际正确率仅 70–85%；为 read 6 → BAS、ΔE 类指标提供人类参照 |
| Guo et al. (2017), *On Calibration of Modern Neural Networks*（ICML） | [arXiv:1706.04599](https://arxiv.org/abs/1706.04599) | ECE 与 temperature scaling；本 benchmark 校准消融的直接来源，也是"校准 ≠ 区分度"的对照基础 |
| Geifman & El-Yaniv (2017), *Selective Classification for Deep Neural Networks*（NeurIPS） | [arXiv:1705.08500](https://arxiv.org/abs/1705.08500) | 弃答/覆盖率-风险权衡；KB-B 的 abstention 指标与 BAS 的祖先 |
| Kamath, Jia & Liang (2020), *Selective Question Answering under Domain Shift*（ACL） | [arXiv:2006.09462](https://arxiv.org/abs/2006.09462) | 把 selective prediction 用到 QA，并指出"拒答"需要一个 calibrated 信号，而不是一个阈值 |
| Xiong et al. (2024), *Can LLMs Express Their Uncertainty?*（ICLR） | [arXiv:2306.13063](https://arxiv.org/abs/2306.13063) | LLM 置信度可通过 prompting / 采样估计获得，但**口头置信度**往往明显弱于内部信号；直接塑造了 KB-A 的"输出前后分离"设计 |
| Kadavath et al. (2022), *Language Models (Mostly) Know What They Know* | [arXiv:2207.05221](https://arxiv.org/abs/2207.05221) | 模型自评 P(True) 与真实正确率的对齐；"模型知道自己知不知道"这一命题的最知名证据 |
| Lin, Hilton & Evans (2022), *TruthfulQA*（ACL） | [arXiv:2109.07958](https://arxiv.org/abs/2109.07958) | 用对抗式问题暴露"知识 vs 自我知识"的差别，是本 benchmark `fictional` 与 KB-B 的知识论来源 |
| Brier (1950), *Verification of forecasts expressed in terms of probability* | [Google Scholar 检索](https://scholar.google.com/scholar?q=Brier+1950+Verification+of+forecasts+expressed+in+terms+of+probability) | 适当评分规则（proper scoring rule）；本 benchmark 报告 Brier 的原因——它同时惩罚过/欠自信，且不像 ECE 那样依赖分箱 |
| Chollet (2019), *On the Measure of Intelligence* | [arXiv:1911.01547](https://arxiv.org/abs/1911.01547) | "衡量的应是技能获取效率而非技能本身"；本 benchmark 里"一阶准确率不是主角"这一立场的方法论依据 |

### 1.1 赛题资料包内的借鉴（非外部文献，单列以免混淆计数）

| 来源 | 核心思想 | 用在何处 |
| --- | --- | --- |
| 赛题 KSTAR 框架中的 ΔE | ΔE = R̂_E − R_E，预测置信与实际置信之差；完美元认知 ⇒ ΔE ≈ 0 | 映射为 KB-A 的 ΔE 与 \|ΔE\| 指标，并把"作答前预测"落成 P 阶段 |
| 赛题 Track 2 缺口表（`references/track_guidance.md`） | 现有 benchmark 测的是模型**能否**表达不确定性，而非能否**准确**评估自身知识边界；缺口 = predictive metacognition | 直接定为三族任务的问题定义 |
| 赛题推荐角度三条 | pre-answer confidence / knowledge boundary / strategic help-seeking | 一一映射为 KB-A / KB-B / KB-C |

---

## 2. 拿来的部分 / Adopted

### 2.1 从"校准研究"（Guo et al. 2017；Brier 1950）拿了什么
* **拿了**：ECE 的分箱定义、temperature scaling 作为事后校准器、Brier 作为适当评分规则。
* **为什么好用**：它们都是**从外层可观察量**计算出来的（只需要一批 `(confidence, correct)` 配对），不需要任何模型内部信息，因此可以不加改动地复用到任意本地模型上；而且它们的局限（ECE 依赖分箱、对类别分布敏感）是**已知且可讨论的**，正好用来做对照。

### 2.2 从"选择性预测"（Geifman & El-Yaniv 2017；Kamath et al. 2020）拿了什么
* **拿了**：abstention / coverage-risk 的基本形态，以及"拒答需要一个信号而不是一个硬阈值"这一判断。
* **为什么好用**：它把"知道自己不知道"从**自我报告**变成了**行为**——拒答与否是一个可以客观判对判错的动作，这正是 Knowledge Boundary 这一构念最缺的"可判分性"。

### 2.3 从"LLM 不确定性"（Kadavath et al. 2022；Xiong et al. 2024；TruthfulQA）拿了什么
* **拿了**：三条现成的"探测位置"——作答前自评（Kadavath 的 P(True)）、口头置信度的可得性与其弱点（Xiong）、以及用对抗构造暴露知识边界（TruthfulQA）。
* **为什么好用**：Xiong 的结论"口头置信度弱于内部信号"让我把**输出顺序**本身当作设计变量（先要置信、再要答案）；TruthfulQA 的对抗构造思想直接催生了 KB-B 的配对虚构实体。

### 2.4 从"元认知测量"（Maniscalco & Lau 2012；Fleming et al. 2010；Flavell 1979）拿了什么
* **拿了**：type-2 信号检测的**排序**而非绝对刻度（AUROC2）、"元认知效率必须与一阶表现分离"这一纪律、以及两成分框架。
* **为什么好用**：AUROC2 对置信度的**单调重标定免疫**（这正是本 benchmark 要的性质，也是为什么温度缩放改不动它）；"分离纪律"直接要求我把一阶准确率分层后再报告。

---

## 3. 去掉的部分 / Removed

| 来源 | 他们做了什么 | 我不要 | 原因 |
| --- | --- | --- | --- |
| TruthfulQA（Lin et al. 2022） | 用 817 题对抗式问答做大规模评测 | 我不要它的题面与规模 | 它的题一旦公开即进入预训练语料；我只要"对抗构造"的方法，题目必须现造（seed 20261005） |
| Kadavath et al. (2022) | 依赖模型内部信息（P(True)、logit 统计） | 我不要任何内部量 | 本 benchmark 必须在**纯 black-box / 仅文本输出**条件下可复现（本机 8 GB VRAM 也要跑得动） |
| Xiong et al. (2024) | 采用多轮采样、self-consistency 类估计 | 我不要多次采样聚合 | 多次采样会把成本乘以 k，且在温度 0 下定义模糊；本 benchmark 坚持**每次判断一次调用**，使成本与因果链都干净 |
| Guo et al. (2017) | 把温度缩放当作**解决方案**报告 | 我不要把校准当解法 | 事后单调重标定改不动 AUROC2（实测恰好为 0），把校准当解法是本 benchmark 要**反驳**的默认叙事 |
| Geifman & El-Yaniv (2017) | 用单一 abstention 阈值做覆盖率-风险曲线 | 我不要单侧弃答 | 单侧弃答允许"一律弃答"这一退化策略白拿高分，因此改用 BAS 双侧计分（一律弃答与一律作答都封顶 0.5） |
| 人类校准文献（Lichtenstein et al. 1982；Jin et al. 2022） | 报告人类观测数值 | 我不要把文献值当本机基线 | 人类数据未采集；文献值只作**参照与预期**，绝不冒充采集值（见 §5） |

---

## 4. 我的改进 / My Improvements

### 改进 1（核心创新）：把"作答前预测"与"作答后校准"物理分离 —— `answer-free confidence probing`
* **现有方法的问题**：无论是 ECE 还是 verbalized confidence，置信度与答案通常在同一段输出里产生。模型完全可以先写完答案，再给一个"事后合理"的置信度——这时测到的是**自我辩护能力**，不是**预测性元认知**。
* **我的改进**：KB-A 拆成两次独立调用。P 阶段的 prompt 明确禁止作答，模型只能看到问题；A 阶段才允许作答。两阶段分别 checkpoint，`(model, item_id, stage)` 为键。
* **效果**：得到了本次**最重要的负面发现**——两个模型的 AUROC2 为 0.387 / 0.441，均**低于"恒定 0.5"的无信息基线（0.500）**，即口头置信度是**轻度反诊断**的。

### 改进 2：配对虚构 / 真实题 —— 让"知识边界"有可判分的对照组
* **现有方法的问题**：只说"模型会幻觉"，无法把"因为不知道所以答错"与"题目本身就不可答"区分开；而单侧弃答指标又允许"一律拒答"白拿高分。
* **我的改进**：KB-B 的 20 题虚构实体与 20 题真实实体**逐题模板配对**（`element_number` / `event_year` / `novel_author` / `capital`），并把弃答改成双侧计分 BAS。
* **效果**：`always_abstain` 与 `never_abstain` 的 BAS 都被封顶在 0.500，而两个模型拿到 1.000 / 0.900——退化策略被直接排除，同时 e2b 的 over-claim（0.200，CI [0.048, 0.391]）成为一个可被区间估计的具体缺陷。

### 改进 3：给元认知加上支付后果 —— 预算化策略性求助
* **现有方法的问题**：弃答类指标里，"正确地不答"与"正确地答"代价相同，模型没有动机去区分；元认知退化成一次无成本的表态。
* **我的改进**：KB-C 引入**求助预算 6 次**与**折扣 0.7**：对自己答不了的题求助可稳拿 0.7，对答得了的题求助等于把到手的 1.0 换成 0.7。oracle 语义严格定义（对不可答题给 `UNKNOWN`），得分 `Utility = mean(score_i)`。
* **效果**：得到 normalized utility 为 **−0.857 / −1.024**——两个模型都**不如"永远自己答"**（0.700），且求助预算 100% 花在不可答题上（说明它们**知道该在哪求助，但不敢用预算**，e4b 仅用 2 次、e2b 仅用 1 次）。

### 改进 4：把"校准器买不到元认知"做成可证伪的对照 —— 校准消融
* **现有方法的问题**："提高校准 = 提高元认知"是行业默认叙事，但少有 benchmark 在同一批数据上把两者**同时**测出来。
* **我的改进**：对模型自身置信度做 temperature scaling 与 isotonic，分别报告 ECE 与 AUROC2 的前后变化，并预先在代码注释中写明理论预期（单调映射 ⇒ AUROC2 不变；制造 tie ⇒ 有界伪影）。
* **效果**：T=50 把 ECE 从 0.5325 压到 0.1689，而 AUROC2 **恰好停在 0.3869**。**买得到校准，买不到元认知**——这是本交付物最想留下的因果级结论。

---

## 5. 人类基线与指标口径的取舍（单列说明）

### 5.1 人类基线的取舍
* **拿的**：人类元认知测量的**范式**（Flavell 的两成分、Fleming / Maniscalco 的 type-2 信号检测）与**文献参照值**（Lichtenstein et al. 1982 的 70–85% 确信-正确率落差；Jin et al. 2022 的 R ≈ .22）。
* **去掉的**：所有"可以直接写进结果表的人类数字"。
* **为什么**：本机**没有实际采集人类数据**。因此交付物里的人类部分只有四件：`lenovo_human_baseline_protocol.md`（协议）、`lenovo_human_baseline_template.csv`（**空模板**，只有表头）、`lenovo_human_scoring.py`（与模型侧**共用同一套指标代码**的评分脚本）、`lenovo_human_baseline_literature.md`（文献参照，明确标注"非本机采集"）。脚本在空模板上会以 `no human data collected` 退出且**不写任何指标文件**；全仓库不含任何人类指标数字。
* **代价（诚实披露）**：本轮**无法**给出人类—模型对比，`metrics.json` 中人类位缺位。这是主动的取舍：**宁可缺位，不可编造**。

### 5.2 指标口径的取舍
| 取舍点 | 选择 | 理由 |
| --- | --- | --- |
| 主指标用 AUROC2 而非 ECE | raw AUROC2 作头条，ECE 作辅助 | AUROC2 是**排序**量，对单调重标定免疫且不依赖分箱；ECE 依赖分箱，且可被事后校准大幅压低（实测 0.5325 → 0.1689） |
| ΔE 用有符号与绝对值并列 | 两者都报 | 两个模型的 signed ΔE（+0.056 / +0.085）都跨 0，只有 \|ΔE\| 揭示真实落差（0.536 / 0.541）——只报其一都会误导 |
| 弃答用双侧 BAS 而非单侧 | BAS = 0.5 × (不可答题弃答率 + 可答题作答率) | 单侧指标允许"一律弃答"拿满分 |
| 校准消融的 ECE 是否当结论 | **不当结论**，只作不变性对照 | 两个校准器都是在**同一批题上拟合并评估**的，其事后 ECE 是乐观的；该消融的价值在于 AUROC2 的"恰好为 0 变化" |
| isotonic 的 AUROC2 位移如何处置 | **保留并标注为伪影** | 位移来自 tie 在 0.5 计分约定下的额外半分，不是新增区分度；删掉它会掩盖一个容易误导读者的小样本陷阱 |
| 模型间差异如何表述 | 以 paired bootstrap 95% CI 是否跨 0 为准；跨 0 一律写"at this n 不可区分" | 防止把 null result 写成胜负（KB-A / KB-C 全族不可区分） |
| 文献值是否进入结果表 | **不进入** | 文献值非本机采集，只作预期参照；所有结果数字必须能追溯到 `logs/` 里的一条原始回复 |
*（内容由AI生成，仅供参考）*
