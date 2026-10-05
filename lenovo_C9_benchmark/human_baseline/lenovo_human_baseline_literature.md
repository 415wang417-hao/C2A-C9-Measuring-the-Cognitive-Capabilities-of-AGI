# 人类元认知参照值（文献，非本机采集）

> **性质声明**：本文件列出的是**已发表文献**中的参照数值，用于给 KnowBound 的模型数字提供外部
> 量级参照；它**不是**本地采集的人类数据，**不得**在报告、PPT 或答辩中当作本 benchmark 的人类
> 实测结果引用。本机的人类数据位于 `lenovo_human_baseline_template.csv` 所对应的正式数据文件
> （尚未采集），采集与计分口径见 `lenovo_human_baseline_protocol.md`。
>
> 检索方式与可信度：下列条目由联网检索（2026-10-05）汇总，**引用前须逐条核对原文/DOI**；
> 其中标注「经典」的 4 条为教科书级结论，风险最低。凡本文件未给出的数字，一律不得凭印象补写。

## 1. 置信度–正确率相关（confidence–accuracy correlation）

| 数值 | 范围/任务 | 出处 |
| --- | --- | --- |
| R = .22 | 跨被试总体（213 个数据集、约 9,132 名被试、约 390 万试次；元分析） | Jin, Verhaeghen & Rahnev (2022), *Psychonomic Bulletin & Review* 29:1748–1762, DOI 10.3758/s13423-022-02063-7 |
| R = .35 | 记忆任务子集（同一元分析；知觉任务更低） | 同上 |
| r ≈ .58 | 被试内（面孔识别/目击证词，平均相关） | Read, Lindsay & Nicholls (1998)（转引自 Sporer 1993 等综述） |
| r = .15，95% CI [.06, .24] | 临床判断（36 项研究、1,485 名临床医生） | Miller, Spengler & Spengler (2015), *Journal of Counseling Psychology* 62(4):553–567 |

## 2. 过度自信幅度（overconfidence bias）

| 数值 | 范式 | 出处 |
| --- | --- | --- |
| 90% 置信区间实际仅含真值 ~50%（缺口 ~40 个百分点） | overprecision（区间估计） | Klayman, Soll, González-Vallejo & Barlas (1999), *OBHDP*；Alpert & Raiffa (1969/1982)【经典】 |
| 高估表现 5–10 个百分点 | overestimation（二选一强迫选择） | Klayman et al. (1999)；Moore (2020) 综述 |
| 100% 确信时实际正确率 70%–85%（即 15–30 个百分点过度自信） | 校准曲线端点 | Lichtenstein, Fischhoff & Phillips (1982), *Judgment under Uncertainty*【经典】 |
| 难任务过度自信、易任务欠自信 | "hard–easy effect" | Lichtenstein & Fischhoff (1977)【经典】 |

## 3. Type-2 AUROC（aROC，与 KnowBound 的 AUROC2 同构）

| 数值 | 任务 | 出处 |
| --- | --- | --- |
| 约 0.65–0.80（多数研究报告均值 ~0.70） | 知觉辨别（人类健康成人） | Fleming et al. (2010)；Faivre et al. (2018, *Self-Knowledge Dim-Out*)；Wilterson & Soon (2021) |
| 0.82–0.85 | 注意/可见性评分任务 | Wokke et al. (2022), *Journal of Vision*, DOI 10.1167/jov.22.10.20 |
| meta-γ（置信–正确 gamma 相关）人类 0.16–0.34 | 开放题与选择题 | Yoshizawa et al. (2026), *Frontiers in Artificial Intelligence* 9:1694192 |

**方法学提醒**（写进报告时必带）：aROC 与一阶任务表现正相关，跨条件比较必须匹配正确率
（Fleming & Lau, 2014）；更纯净的指标是 meta-d′/d′（Maniscalco & Lau, 2012），但其信度较低
（ICC 在 400 试次仅约 0.42）。KnowBound 用"准确率分箱后的 AUROC2"作部分补偿，见
`results/summary.md` 的 *accuracy-binned AUROC2* 表。

## 4. 用于本项目的推论（可写进报告的口径）

1. 人类在**被试内/trial 级**元认知敏感性通常显著高于 0.5（aROC ≈ 0.65–0.80）；因此若被测模型
   的 KB-A AUROC2 95% CI 上界仍低于 0.5，可以说"低于人类常见区间且方向为反诊断"，但不能说
   "低于人类被试"——本机未采集人类数据，且不匹配任务与正确率。
2. 人类存在稳健的过度自信（尤其高置信端点）；模型若在 KB-A 的 `multihop` 域出现 ΔE ≈ +0.8，
   量级大于人类文献中的过度自信幅度，属于"远超人类常见水平"的观察，但**任务不可比**，
   只能作为方向性陈述。
3. 人类跨被试的置信–正确率相关本身只有 R ≈ .22（元分析），因此**不要把"相关不高"直接解释为
   模型缺陷**；这也是 KnowBound 用 AUROC2（个体内 trial 级区分度）而非相关系数作头条指标的原因。
