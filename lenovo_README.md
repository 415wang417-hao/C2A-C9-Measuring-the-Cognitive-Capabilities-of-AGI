---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 60ea5d0126731e33de81577b27285889_375eb7e2c08e11f1887c525400de85a5
    ReservedCode1: n/mXdYguMUZF6k/BlmGQB3I6scLq9Ks9ab1iRyJGq5SuD7ZkG5IM9n9+KhjIUllm4V90GPFJh7V/OGBBANiGxOH8uRCBnYGLM8FkN8XYV0Vn1bHdJx4RB3Z5Wk47i2TYaJKWFIr14hvgQnyCmWBC4XvSGJP29/f5EDx/XelyR99jhq80vkH7JrxF4U0=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 60ea5d0126731e33de81577b27285889_375eb7e2c08e11f1887c525400de85a5
    ReservedCode2: n/mXdYguMUZF6k/BlmGQB3I6scLq9Ks9ab1iRyJGq5SuD7ZkG5IM9n9+KhjIUllm4V90GPFJh7V/OGBBANiGxOH8uRCBnYGLM8FkN8XYV0Vn1bHdJx4RB3Z5Wk47i2TYaJKWFIr14hvgQnyCmWBC4XvSGJP29/f5EDx/XelyR99jhq80vkH7JrxF4U0=
---

# lenovo_README — C2A / C9「衡量 AGI 的认知能力」交付物总览

- **作者 / Author:** lenovo
- **挑战 / Challenge:** C2A（提案）+ C9（基准实现与实测）
- **赛道 / Track:** Track 2 — Metacognition（元认知）
- **日期 / Date:** 2026-10-05
- **交付物根目录:** `C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\`
- **配套文件:** `lenovo_交付物清单.md`（逐件清单与评分映射）、`lenovo_C2A_提案_迭代版本.md`（v1→v3 演进记录）

---

## 1. 交付物总览

本交付物包含两个阶段的完整成果：**C2A 阶段**给出一个可判分的元认知基准提案（KnowBound）；**C9 阶段**把该提案完整实现，并在两个本地模型上跑出 360 次真实调用、0 失败的全量实测结果。

| 挑战 | 交付内容 | 件数 | 状态 |
| --- | --- | --- | --- |
| **C2A** | 提案、AI 日志、拿来说明（+ 迭代版本留痕） | 3 件必交 + 1 件随附 | 已落盘 |
| **C9** | `lenovo_C9_benchmark\` 完整代码 + task说明、测试结果、反思报告、AI日志、拿来说明、AAR | 代码 1 套 + 6 份文档 | 已落盘 |
| **总览** | 本 README + 交付物清单 | 2 件 | 已落盘 |

**一句话概括两者的关系：** C2A 是"设计"，C9 是"实施"——提案中的每一个数字，都能在 C9 的 `logs\` 与 `results\` 里追溯到一条原始模型回复。

---

## 2. 目录结构树

```
C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\
├─ lenovo_README.md                      ← 本文件（总览 / 复现 / 命名 / 局限）
├─ lenovo_交付物清单.md                   ← 逐件清单 + 两套评分口径映射 + 红线自检
│
├─ 【C2A】提案
│   ├─ lenovo_C2A_proposal.md                 ← 提案定稿（四段式 20/40/20/20 + 18 条核验文献）
│   ├─ lenovo_C2A_提案_迭代版本.md         ← v1→v2→v3 演进记录 + 版本对照表 + 可复算对齐清单
│   ├─ lenovo_C2A_AI日志.md               ← AI 使用记录（10 轮迭代时间线 / 纠偏表 / 人工介入）
│   └─ lenovo_C2A_拿来说明.md             ← 拿来主义说明（缺口表逐行回应 / 10 条去掉 / 5 条改进）
│
├─ 【C9】文档
│   ├─ lenovo_C9_task说明.md              ← 任务说明（基准设计 / ground truth / 指标定义）
│   ├─ lenovo_C9_测试结果.md              ← 测试结果（360 次调用全量结果 / CI / 消融 / 分层）
│   ├─ lenovo_C9_反思报告.md              ← 反思报告（局限与解读纪律）
│   ├─ lenovo_C9_AI日志.md                ← AI 使用记录（实现与试错 / 4 个真实 bug）
│   ├─ lenovo_C9_拿来说明.md              ← 拿来主义说明（借鉴来源与自研边界）
│   └─ lenovo_C9_AAR.md                   ← After Action Review（A1–A6 改进项）
│
└─ 【C9】代码
    └─ lenovo_C9_benchmark\
        ├─ README.md                      ← 基准仓库自述（设计 / 指标 / 基线 / 结果 / 局限）
        ├─ requirements.txt               ← 依赖：requests>=2.28、numpy>=1.24
        ├─ run_all.ps1                    ← 一键入口（selftest / smoke / full / report / generate）
        ├─ configs\default.yaml           ← 固定 seed 20261005、模型与采样参数
        ├─ knowbound\                     ← 17 个模块：generate / runner / grading / metrics /
        │                                    baselines / calibrators / stats / compare / report /
        │                                    manifest / models / prompts / config / selftest …
        ├─ data\                          ← kb_a.jsonl / kb_b.jsonl / kb_c.jsonl / manifest.json
        ├─ logs\                          ← transcript_*.jsonl（原始 I/O）+ scored_*.jsonl（含判分）
        │                                    + run_manifest_full_*.json（运行溯源）
        ├─ results\                       ← metrics.json / summary.md + 按模型的 metrics/summary + smoke_report.md
        ├─ human_baseline\                ← 协议 / 空模板 CSV / 同代码打分脚本 / 文献参照
        └─ tests\test_knowbound.py        ← 离线自测
```

> `logs\` 是**每条数字的最终出处**（只追加）；`results\` 可由 `logs\` 随时重算（可丢弃）；`data\` 由固定 seed 字节确定重建。三层分离让"可追溯"成为结构保证而非承诺。
> 注：`lenovo_C9_benchmark\.pytest_cache\` 为测试运行缓存，非交付物内容，可删除。

---

## 3. 一句话摘要与核心结论

### 3.1 C2A — 提案

**一句话摘要：** 现有元认知 benchmark 测的是模型"能否表达不确定性"，不是它"能否准确评估自身知识边界"；KnowBound 把元认知操作化为一个可判分的**二阶判断**，用三族任务（预答置信 / 知识边界 / 策略性求助）把它从一阶能力中物理剥离。

**核心结论：**

1. **二阶区分度低于无信息线。** 两个模型在 KB-A 上的 AUROC2 为 **0.3869** 与 **0.4408**，而 `constant_50` 恰好是 **0.500**——预答置信不仅无信息，还轻微**反诊断**。
2. **校准 ≠ 元认知。** 温度缩放把 ECE 从 **0.5325 压到 0.1689**（e2b：0.5152→**0.1267**），AUROC2 **恰好停在原位**——事后校准买得到校准，买不到一比特元认知。
3. **ΔE 会翻转符号。** `multihop` 上 ΔE = **+0.8500 / +0.8233**（重度过度自信），`fictional` 上 **−0.9533 / −0.8600**（严重欠自信）；全局 signed ΔE 仅 +0.0558 / +0.0852 且 CI 跨 0，**"模型过度自信"这一笼统说法不成立**。
4. **会判断，不敢花。** KB-C 中两个模型的求助 **100% 花在不可答题上**（判断正确），但 6 次预算只用了 **2 次 / 1 次**，net utility **0.5200 / 0.4850** 反而低于 `always_do_it`（0.700），normalised utility **−0.8571 / −1.0238**。
5. **人类基线宁缺勿造。** 本轮人类数据未采集，交付物只含协议、空模板、同代码打分脚本与标注"非本机采集"的文献参照，**不含任何人类指标数字**。

### 3.2 C9 — 实现与实测

**一句话摘要：** KnowBound 的完整纯黑盒实现，固定 seed、可字节确定重建题目，全部指标由日志重算（无硬编码常数），在两个本地模型上完成 **180 + 180 = 360 次调用、0 失败、0 空回复、0 JSON 解析失败**。

**核心结论（按族）：**

| 任务族 | 关键读数（e4b / e2b） | 读法 |
| --- | --- | --- |
| KB-A（预答置信） | accuracy 0.7000 / 0.6500；AUROC2 **0.3869 [0.281, 0.501]** / **0.4408 [0.311, 0.583]**；ECE-10 0.5325 / 0.5152；\|ΔE\| 0.5358 / 0.5408 | **无 above-chance 二阶判别**（区间含或低于 0.5） |
| KB-B（知识边界） | 总体 accuracy 1.000 / 0.900；over-claim **0.000 [0, 0]** / **0.200 [0.048, 0.391]**；BAS **1.000** / **0.900**（退化对照均 0.500） | e4b 边界行为**双侧非退化**；e2b 在虚构题上**可测地更差**（成对 CI 排除 0） |
| KB-C（策略性求助） | utility **0.5200** / **0.4850**；求助 2 / 1 次（预算 6）；normalised **−0.8571** / **−1.0238**；oracle 上界 0.910 | 两模型均**低于"永远自己答"**，但与 `always_do_it` 的 CI 跨 0，故只写"不可区分" |
| 校准消融 | ECE 0.5325→0.1689 / 0.5152→0.1267，AUROC2 **分毫不动** | 校准与判别力解耦的因果级反例 |
| 分域分层 | 分层 3 的 AUROC2 **0.0588**（n=25）；pooled 0.436 / 0.486 | "反诊断"集中在最难层，一阶能力被 hold 住后仍成立 |
| 模型间比较 | KB-A、KB-C **无可检出差异**；KB-B 上四个指标分离 | 不主张"大模型元认知更好" |

**明确不支持的论断（写入文档、不做过度解读）：** 不主张大模型元认知更好；不主张求助策略优于直接作答；不主张对人类或其他 prompt / seed / 量化 / 运行时的一般性结论。

---

## 4. 如何复现 C9 评测

### 4.1 环境与依赖

| 项 | 要求 | 本机实测环境 |
| --- | --- | --- |
| 操作系统 | Windows（`run_all.ps1` 为 PowerShell） | Windows 11 (Build 26200) |
| Python 包 | `requests>=2.28`、`numpy>=1.24`（仅两项） | 已满足 |
| 本地推理服务 | Ollama，`http://127.0.0.1:11434` | Ollama **0.35.1** |
| 模型 | `gemma4:e4b`(7.5B, Q4_K_M)、`Librellama/gemma4:e2b-Uncensored`(4.6B, Q4_K_M) | 同上 |
| 硬件 | 消费级即可，约 8 GB 显存 | RTX 5060 Laptop 8 GB + i7-14650HX + 24 GB RAM |

安装依赖（`run_all.ps1` 会自动检测并安装，也可手动）：

```powershell
cd C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\lenovo_C9_benchmark
python -m pip install -r requirements.txt
```

### 4.2 复现命令（四级：离线 → 冒烟 → 全量 → 重建报告）

**① 离线自测（不需要模型、不需要联网）**

```powershell
python -m knowbound selftest
# 或
.\run_all.ps1 -Mode selftest
```

预期输出：全部断言通过（含"温度缩放的 AUROC2 变化恰好为 0"与 isotonic 的 ±0.5 界），秒级返回。

**② 生成题目（固定 seed，字节确定）**

```powershell
python -m knowbound generate
```

预期输出：`generated {'kb_a': 60, 'kb_b': 40, 'kb_c': 20} -> ...\data`，并写出 `data\manifest.json`（记录 seed、计数、generator 配置、版本、时间戳）。

**③ 冒烟测试（端到端链路验证，3 题 / 族）**

```powershell
python -m knowbound smoke --model "gemma4:e4b"
# 或
.\run_all.ps1 -Mode smoke -Model "gemma4:e4b"
```

预期输出：`results\smoke_report.md`——9 题 / 12 次调用全部成功、0 解析失败；测得**热身调用延迟 0.678 s**（冷启动 16.824 s，已排除在估算之外），据此估算全量 180 次调用约 2.3 分钟。**冒烟实际耗时约 1 分钟。**

**④ 全量评测（每模型 180 次调用）**

```powershell
python -m knowbound run --model "gemma4:e4b" --tag full
python -m knowbound run --model "Librellama/gemma4:e2b-Uncensored" --tag full
# 或一次性
.\run_all.ps1 -Mode full
```

预期输出：

- `results\metrics_full_gemma4-e4b.json`、`results\summary_full_gemma4-e4b.md`
- `results\metrics_full_Librellama_gemma4-e2b-Uncensored.json`、`results\summary_full_Librellama_gemma4-e2b-Uncensored.md`
- `logs\transcript_full_*.jsonl`（原始 I/O，含解析策略、延迟、时间戳）与 `logs\scored_full_*.jsonl`（含判分字段）
- 控制台：`[full] {'kb_a': 60, 'kb_b': 40, 'kb_c': 20} in <elapsed>s -> ...\results`

**实测耗时：** e4b 模型时间 **137.1 s**、e2b **76.0 s**（`temperature=0`、`num_predict=256`、严格串行），两模型合计 **≈3.6 分钟**；0 失败。

**⑤ 两模型聚合与交叉比较（2000 次 bootstrap + 成对 CI）**

```powershell
python -m knowbound compare --tag full --n-boot 2000
```

预期输出：`results\metrics.json`（机读）与 `results\summary.md`（含逐族主指标、按域分解、难度分层、校准消融、全部基线策略、模型间成对区间）。**实测耗时 3.8 s。**

**⑥ 不调用模型、仅从日志重建报告（离线可复现）**

```powershell
python -m knowbound report --tag full --model "gemma4:e4b"
# 或
.\run_all.ps1 -Mode report
```

预期输出：由 `logs\scored_*.jsonl` 重算并覆盖对应的 `results\metrics_*.json` 与 `summary_*.md`——这是"结论可复算、无硬编码常数"的直接验证方式。

### 4.3 人类基线（协议就绪，数据未采集）

```powershell
python human_baseline\lenovo_human_scoring.py --validate-only
```

预期输出：仅检查 CSV 表头与形状，**不计算任何指标**；对空模板正式运行会以 `no human data collected` 退出且**不写任何文件**。该脚本导入的是 `knowbound.grading` / `metrics` / `baselines` / `stats`——与模型侧**同一套指标代码**，确保人与模型在同一尺度上比较。

### 4.4 注意事项

- `logs\transcript_*.jsonl` 支持**断点续跑**：中断后重跑只补发缺失调用，单题失败不会中断整轮。
- 若报 `ConnectionError … [WinError 10061]`，说明 **Ollama 服务未监听**（`127.0.0.1:11434` 端口关闭）——先启动 Ollama 应用或 `ollama serve`，`GET /api/version` 返回版本号即恢复。
- `run_all.ps1` **不安装多余依赖、不删除任何数据**；串行执行是为了在参考硬件上避免内存压力（推理时可用内存曾降至约 2.3 GB）。

---

## 5. 文件命名规范

| 规则 | 说明 | 示例 |
| --- | --- | --- |
| **统一前缀** | 所有交付文件以 `lenovo_` 开头（本人姓名拼音） | `lenovo_C2A_proposal.md` |
| **结构** | `lenovo_{C2A\|C9}_{描述}.md`；代码目录为 `lenovo_C9_benchmark\` | `lenovo_C9_测试结果.md` |
| **语言** | 正文以中文论述，**专业术语保留英文**（AUROC2 / ECE / BAS / over-claim / bootstrap 等） | — |
| **不改既有文件** | `lenovo_C9_benchmark\` 内既有文件在本任务中**未被修改**，新增文档一律落在根目录 | — |
| **数据文件** | 沿用 `kb_a` / `kb_b` / `kb_c` 与 `{tag}_{model-slug}` 命名，便于脚本解析 | `metrics_full_gemma4-e4b.json` |

---

## 6. 已知局限

**评测规模与稳健性**

1. **两模型、各跑一轮、各一套 prompt。** 全量运行已完成，但**未做** prompt 改写、seed 波动或量化研究，因此对稳定性不作任何声明；冒烟切片（3 题 / 族）仅是链路证据。
2. **CI 是 item 级的**，只覆盖题目抽样，`n = 60 / 40 / 20`，每题仅一次生成；KB-C 的 utility CI 半宽约 ±0.21，分辨不了 0.02 量级差异。
3. **串行执行**（为避免内存压力），未做并行加速。

**结果解读**

4. **KB-A 是零结果，且被如实报告。** AUROC2 低于 0.5 且 CI 跨 0.5，不能据此主张"普遍轻微反诊断"——只在本题目集上成立，且信号主要来自 `multihop` 域（accuracy 0.1333 / 0.0667）。
5. **天花板域导致部分指标无定义。** `fictional` 题按构造"正确答案即 UNKNOWN"，accuracy 1.000 使该域 AUROC2 不可定义；e4b 的 KB-B AUROC2 同为 `n/a`（置信度无变异）。
6. **KB-B 无法完全分离"知识差"与"元认知差"。** e2b 的 over-claim 0.200 也可被"知识更少 / uncensored 削弱拒答"解释（改进项 A6）。
7. **KB-C 是简化经济学。** 单一求助价（×0.7）与单一预算（6），无时延成本，也不给"在可答题上求助"部分分。

**方法边界**

8. **自动判分对自由文本是脆的。** 可接受答案列表刻意收窄，`longtail` 与 KB-B 真实题可能因措辞被判错——偏差方向是**低估 accuracy**，已显式声明。
9. **虚构保证是尽力而为的结构性保证，不是证明。** 词素构造 + 黑名单比对无法穷尽证明"某虚构实体不存在于预训练语料"；模型偶尔蒙对会被计为 over-claim。
10. **校准消融的校准器与评估集相同**，故事后 ECE 偏乐观；该消融的目的是**不变性对照**（温度缩放 AUROC2 恒不变），不是头条 ECE。
11. **人类基线尚无实测数据。** 已交付协议、空模板、同代码打分脚本与文献参照值（明确标注"非本机采集"），仓库内**不出现任何人类指标数字**，因此不主张任何模型—人类差异。

**已知偏差（主动披露）**

12. C2A 提案正文长度**超出赛题建议的 800–1500 字**；取舍为"结论全部有据"优先于字数达标（摘要可单独抽出作为短版）。
13. 未实测的朴素阈值基线（naive threshold）**未被写成实测结果**，仅列为下一版实现（AAR A1 / A6）。
*（内容由AI生成，仅供参考）*
