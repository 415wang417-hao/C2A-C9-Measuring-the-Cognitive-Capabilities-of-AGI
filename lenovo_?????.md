---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 60ea5d0126731e33de81577b27285889_367067cdc08e11f1884b525400cd780f
    ReservedCode1: VK5QGfEzr4dvGK+0d9WJzht38nEEwjB4cETi+XB2XjLjUKom7uZQiPD8uMHk87jOqkK1EpEZ+nvjCcykFslIAdyqkCI0MxY+RD1p/ZOYJXqRN3x6vwjaCto3sMFH80uv+j6ta+Zd8Pud5NmTvmOMIfVgR2FrE/r37vjSgV7eK0hiY/uDdDqVQgXMtos=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 60ea5d0126731e33de81577b27285889_367067cdc08e11f1884b525400cd780f
    ReservedCode2: VK5QGfEzr4dvGK+0d9WJzht38nEEwjB4cETi+XB2XjLjUKom7uZQiPD8uMHk87jOqkK1EpEZ+nvjCcykFslIAdyqkCI0MxY+RD1p/ZOYJXqRN3x6vwjaCto3sMFH80uv+j6ta+Zd8Pud5NmTvmOMIfVgR2FrE/r37vjSgV7eK0hiY/uDdDqVQgXMtos=
---

# lenovo_交付物清单 — C2A / C9「衡量 AGI 的认知能力」挑战

- **作者 / Author:** lenovo
- **日期 / Date:** 2026-10-05
- **交付物根目录:** `C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\`
- **命名规范:** 全部以 `lenovo_` 为前缀（`{Name}_{C2A|C9}_{描述}.md`；赛道术语保留英文）
- **口径来源:** `C:\Users\lenovo\Desktop\C2A-C9 衡量AGI的认知能力_资料包\rubric.json`（机读）与 `评分标准.md`（正文表格）两套口径，本文档同时给出映射。
- **状态图例:** ✅ 已完成落盘 ｜ 📄 说明性文件（非赛题必交但建议随附） ｜ ⚠️ 已知偏差（见文末）

---

## 1. 交付物逐件清单

### 1.1 C2A 交付物（3 件必交 + 3 件随附）

| 序号 | 文件/目录名 | 类型 | 所属挑战 | 是否必需 | 路径 | 一句话说明 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `lenovo_C2A_提案.md` | Markdown 提案 | C2A | **是**（核心件） | `C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\lenovo_C2A_提案.md` | KnowBound 元认知基准提案定稿：四段式（问题定义 20% / 方法路线 40% / 创新点 20% / 可行性与人类基线 20%）+ 18 条核验文献，24560 字节 | ✅ |
| 2 | `lenovo_C2A_AI日志.md` | Markdown 日志 | C2A | **是**（红线件） | `C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\lenovo_C2A_AI日志.md` | AI 使用记录：任务拆解、10 轮 prompt 迭代时间线、失败纠偏表、人工介入与段位自评，22055 字节 | ✅ |
| 3 | `lenovo_C2A_拿来说明.md` | Markdown 说明 | C2A | **是**（单列评分） | `C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\lenovo_C2A_拿来说明.md` | 拿来主义说明：四类来源（文献 / 已有 benchmark / 框架 / 工具）、逐行回应 Track 2 缺口表、10 条"去掉的"与 5 条"改进的"，22724 字节 | ✅ |
| 4 | `lenovo_C2A_提案_迭代版本.md` | Markdown 提案（迭代留痕） | C2A | 建议随附 | `C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\lenovo_C2A_提案_迭代版本.md` | v1→v2→v3 演进记录 + 完整四段式定稿 + 版本对照表 + 与 C9 实测数据的可复算对齐清单，34083 字节 | 📄 |
| 5 | `lenovo_交付物清单.md` | Markdown 清单 | C2A + C9 | 建议随附 | `C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\lenovo_交付物清单.md` | 本文档：逐件清单 + 两套评分口径映射 + 红线条目自检结论 | 📄 |
| 6 | `lenovo_README.md` | Markdown 总览 | C2A + C9 | 建议随附 | `C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\lenovo_README.md` | 交付物总览、目录树、C2A/C9 摘要与核心结论、C9 复现步骤、命名规范、已知局限 | 📄 |

### 1.2 C9 交付物（benchmark 代码 + 6 份文档）

| 序号 | 文件/目录名 | 类型 | 所属挑战 | 是否必需 | 路径 | 一句话说明 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 7 | `lenovo_C9_benchmark\` | 代码目录（Python） | C9 | **是**（核心件） | `C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\lenovo_C9_benchmark\` | KnowBound 完整实现：`knowbound\` 17 个模块 + `configs\` + `data\` + `logs\` + `results\` + `tests\` + `human_baseline\` + `run_all.ps1` + `requirements.txt` + `README.md`（25502 字节），可离线 selftest、可一键复现 | ✅ |
| 8 | `lenovo_C9_task说明.md` | Markdown 文档 | C9 | **是** | `C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\lenovo_C9_task说明.md` | 任务说明：基准设计、三族题目构造与 ground truth、9 指标定义、边界与诚实声明，19052 字节 | ✅ |
| 9 | `lenovo_C9_测试结果.md` | Markdown 文档 | C9 | **是** | `C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\lenovo_C9_测试结果.md` | 测试结果：两模型 360 次调用全量结果、CI、基线族、校准消融、分域分层表，11200 字节 | ✅ |
| 10 | `lenovo_C9_反思报告.md` | Markdown 文档 | C9 | **是** | `C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\lenovo_C9_反思报告.md` | 反思报告：基准局限、结果解读纪律（CI 跨 0 不写成更好/更差）、负面结果如实呈报，3353 字节 | ✅ |
| 11 | `lenovo_C9_AI日志.md` | Markdown 文档 | C9 | **是**（红线件） | `C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\lenovo_C9_AI日志.md` | C9 阶段 AI 使用记录：代码实现、试错、4 个真实 bug 的发现与修复、文献核验，16234 字节 | ✅ |
| 12 | `lenovo_C9_拿来说明.md` | Markdown 文档 | C9 | **是**（单列评分） | `C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\lenovo_C9_拿来说明.md` | 拿来主义说明：基准/代码/指标借鉴来源与自研边界，14694 字节 | ✅ |
| 13 | `lenovo_C9_AAR.md` | Markdown 文档 | C9 | **是**（第 6 份文档） | `C:\Users\lenovo\Desktop\lenovo_C2A-C9_交付物\lenovo_C9_AAR.md` | After Action Review：A1–A6 改进项（题量、折扣档位、prompt/seed 稳健性、人类基线补齐、知识匹配子集），11176 字节 | ✅ |

### 1.3 `lenovo_C9_benchmark\` 内部结构拆解（支撑"可复现"的证据层）

| 子项 | 内容 | 作用 |
| --- | --- | --- |
| `knowbound\` | `__main__.py`、`generate.py`、`runner.py`、`grading.py`、`metrics.py`、`baselines.py`、`calibrators.py`、`stats.py`、`compare.py`、`report.py`、`manifest.py`、`models.py`、`prompts.py`、`config.py`、`selftest.py` 等 17 个模块 | 生成题 → 调用模型 → JSON 解析判分 → 指标聚合 → 报告渲染 的完整链路 |
| `configs\default.yaml` | 1753 字节 | 固定 seed `20261005`、模型、采样与预算参数 |
| `data\` | `kb_a.jsonl`(19303) / `kb_b.jsonl`(13507) / `kb_c.jsonl`(6157) / `manifest.json`(427) | 可字节确定重建的题目与 manifest（记录 seed、计数、版本、时间戳） |
| `logs\` | `transcript_*.jsonl`（原始 I/O）+ `scored_*.jsonl`（含判分字段）+ `run_manifest_full_*.json` | **每条数字的最终出处**，只追加不覆盖，可断点续跑 |
| `results\` | `metrics.json`(42560) / `summary.md`(18556) + 按模型与 tag 拆分的 metrics/summary | 由 `logs\` 重算生成，可随时丢弃重建 |
| `human_baseline\` | `lenovo_human_baseline_protocol.md` / `lenovo_human_baseline_template.csv`（**仅表头，96 字节**）/ `lenovo_human_scoring.py` / `lenovo_human_baseline_literature.md` | 人类基线的协议、空模板、同代码打分脚本与文献参照；**不含任何人类实测数字** |
| `tests\test_knowbound.py` | 1513 字节 | 离线自测（`python -m knowbound selftest` 无需模型） |
| `run_all.ps1` | 2915 字节 | 一键入口，支持 `selftest` / `smoke` / `full` / `report` 四种模式，不安装依赖、不删除数据 |
| `requirements.txt` | 630 字节 | 依赖仅 `requests>=2.28`、`numpy>=1.24` |
| `.pytest_cache\` | 运行缓存 | **非交付物**，可安全删除，不影响复现 |

---

## 2. 评分维度映射（两套口径）

### 2.1 口径 A — 机读 `rubric.json`（满分 100）

| rubric 维度 | 分值 | 承载交付物 | 命中要点 |
| --- | --- | --- | --- |
| `benchmarkDesign` | 25 | #1 提案 §2、#7 代码目录、#8 task说明 | 任务形式与 ground truth 定义清晰；9 指标公式可重算；5 类基线；纯黑盒可复现；校准消融有不变性对照 |
| `researchRigor` | 20 | #1 提案 §1/§3 + 参考文献、#3/#12 拿来说明、#9 测试结果 | 结论有边界（CI 跨 0 写"不可区分"）；负面结果如实呈报（AUROC2 < 0.5）；18 条文献逐条核验；未测的朴素阈值基线不写成结果 |
| `artifactCompleteness` | 15 | #7 代码 + #6 README + #5 清单 + `run_all.ps1` / `requirements.txt` | 目录齐全、README 有复现章节、依赖最小化、一键脚本四模式、结果可重建 |
| `aiUsage` | 20 | #2 C2A AI日志、#11 C9 AI日志、#13 AAR | 多轮迭代时间线、失败与纠偏逐条留痕、人工介入点、不隐藏 AI 参与 |
| `reflectionQuality` | 20 | #10 反思报告、#13 AAR | 局限清单（题量、CI 宽度、虚构保证非证明、判分偏差方向）；A1–A6 可执行改进项 |

### 2.2 口径 B — 正文 `评分标准.md` 表格

**C2A（认知科学理解 25 / 设计创新 25 / 拿来主义 20 / 可行性 15 / 表达 15）**

| 正文维度 | 分值 | 承载交付物 | 命中要点 |
| --- | --- | --- | --- |
| 认知科学理解 | 25 | #1 提案 §1（元认知两成分、预测性元认知、ΔE 与 \|ΔE\|） | 构念与 Flavell / KSTAR 对齐，且与一阶能力剥离 |
| 设计创新 | 25 | #1 提案 §3（四个创新点） | 每点绑定可复算数字（0.1689/0.3869、+0.8500/−0.9533、−0.8571/−1.0238、0.0588） |
| 拿来主义 | 20 | #3 拿来说明、#12 C9 拿来说明 | 缺口表逐行回应；明确"拿了什么 / 去掉了什么 / 改进了什么" |
| 可行性 | 15 | #1 提案 §4、#7 代码 | 360 次调用 0 失败的真实证据；8 GB 显存可跑；零 API 成本 |
| 表达清晰度 | 15 | #1 提案全文、#6 README | 四段式结构、每段标注评分要点、术语中英统一 |

**C9（基准质量 30 / 技术实现 20 / 测试有效性 20 / 拿来主义 15 / 反思 15）**

| 正文维度 | 分值 | 承载交付物 | 命中要点 |
| --- | --- | --- | --- |
| 基准质量 | 30 | #7 代码、#8 task说明 | 三族设计、配对控变量、双侧计分、预算经济学 |
| 技术实现 | 20 | #7 代码、#9 测试结果 | 模块化、断点续跑、JSON 四级解析策略留痕、selftest 离线可跑 |
| 测试有效性 | 20 | #9 测试结果、#7 `results\` | 360 次调用 0 失败、bootstrap CI、成对比较、校准消融三重对照 |
| 拿来主义 | 15 | #12 C9 拿来说明 | 借鉴来源与自研边界清楚 |
| 反思 | 15 | #10 反思报告、#13 AAR | 局限与改进项一一对应 |

### 2.3 两套口径的差异说明

- 口径 A 是**机读 rubric**，维度命名与分值为 `benchmarkDesign / researchRigor / artifactCompleteness / aiUsage / reflectionQuality = 25/20/15/20/20`，并把"C2A 与 C9"合并计分；口径 B 是**正文表格**，C2A 与 C9 分开列维度。
- 两套口径的"拿来说明"均**单独列项**（口径 A 计入 `researchRigor` 与 `reflectionQuality`，口径 B 在两端各占 20% / 15%），故交付物中拿来说明独立成件、不并入提案正文。
- 两套口径对"AI 日志"均为**红线件**：缺失即触发红线扣分（见 §3）。

---

## 3. 红线条目自检结论

| 红线项 | rubric 定义 | 自检结论 | 证据 |
| --- | --- | --- | --- |
| **核心件是否齐**（`missing_artifacts`） | 必交交付物缺失 → 封顶 5 分 | **未触发**：C2A 3 件 + C9 代码与 6 份文档全部落盘 | 根目录 11 个文件 + `lenovo_C9_benchmark\`；最小文档 `lenovo_C9_反思报告.md` 3353 字节，无空文件、无 TODO 占位 |
| **AI 日志是否在**（`no_ai_log`） | 无 AI 使用记录 → 封顶 5 分 | **未触发**：C2A 与 C9 各有一份独立 AI 日志，另加一份 AAR | `lenovo_C2A_AI日志.md` 22055 字节（10 轮迭代 + 纠偏表 + 人工介入）、`lenovo_C9_AI日志.md` 16234 字节、`lenovo_C9_AAR.md` 11176 字节 |
| **是否存在一句话单轮提交**（`one_shot_ai`） | 一次性生成、无迭代痕迹 → 封顶 5 分 | **未触发**：全过程可追溯为多轮迭代而非一次成稿 | C2A 日志记录 10 轮 prompt 迭代与 9 条纠偏；C9 日志记录 4 个真实 bug（Ollama 未监听、解析失败误计、冷启动未分离、isotonic 断言错误）的发现与修复；提案有 v1→v2→v3 三版演进与对照表 |

**自我披露的偏差（不影响红线判定，但如实列出）**

1. `lenovo_C2A_提案.md` 与 `lenovo_C2A_提案_迭代版本.md` 的正文长度**超出赛题建议的 800–1500 字**；取舍为"结论全部有据"优先。
2. 人类基线**未采集数据**，交付物中仅含协议 / 空模板 / 打分脚本 / 文献值，不含任何人类指标数字（主动取舍，非遗漏）。
3. `lenovo_C9_benchmark\.pytest_cache\` 为运行缓存，非交付物内容，可删除。
4. 本清单的"是否必需"列以 `rubric.json` 与 `评分标准.md` 的必交清单为准，标"建议随附"的三件为本任务额外产出，不影响红线判定。
*（内容由AI生成，仅供参考）*
