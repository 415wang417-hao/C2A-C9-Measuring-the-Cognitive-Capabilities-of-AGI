---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 60ea5d0126731e33de81577b27285889_3aa77a16c08e11f1884b525400cd780f
    ReservedCode1: o9rbn2X5qAIwiePEessO5nmcqVWQMDksQpf9f3xB/IG5y0ha1oQM3kgZyCk3aaM1wDF8RjSb9ozI3mbG2kyf5V+I5AIBsl0mI7rM+kQnVTm0k37dwYk20skupSIfkag66OCPal8tANEvycgrp/2FAnmxLt/qONgZ3OKghO2m6MSHWtHC1QETZN8Q+Ig=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 60ea5d0126731e33de81577b27285889_3aa77a16c08e11f1884b525400cd780f
    ReservedCode2: o9rbn2X5qAIwiePEessO5nmcqVWQMDksQpf9f3xB/IG5y0ha1oQM3kgZyCk3aaM1wDF8RjSb9ozI3mbG2kyf5V+I5AIBsl0mI7rM+kQnVTm0k37dwYk20skupSIfkag66OCPal8tANEvycgrp/2FAnmxLt/qONgZ3OKghO2m6MSHWtHC1QETZN8Q+Ig=
---

# lenovo_C9_反思报告 — KnowBound 开发与被测过程的反思

> **作者 / Author:** lenovo
> **挑战 / Challenge:** C2A / C9 — 衡量 AGI 的认知能力
> **赛道 / Track:** Track 2 — Metacognition（元认知）
> **日期 / Date:** 2026-10-05

## 一、四个真实的失败经验

**1）首轮整批失败：Ollama 没在监听。** 第一次发起真实模型调用时，`127.0.0.1:11434` 直接返回 `ConnectionError (WinError 10061)`，整批请求在毫秒级全军覆没，transcript 里没有落下任何一条记录。根因是我把"服务已安装"当成了"服务正在运行"。修复：脚本先探测端口，runner 改为每次调用先写 checkpoint。教训：**环境前置条件必须显式验证，不能靠假设**。

**2）自检里写了一条错的断言。** 自检最初断言"isotonic 校准永不改变 AUROC2"，实测却出现位移（e4b +0.0496、e2b +0.0775）。根因是我没想清楚 isotonic 会制造 tie，而 tie 在 0.5 计分约定下会改变秩和。修复：断言改为"位移有界"（仅在存在 tie 时允许小幅双向移动），并在文档中把该位移明确标注为**约定伪影**。教训：**断言要写"允许发生什么"，而不是"我希望发生什么"**。

**3）报告曾虚报 JSON 解析失败。** 冒烟阶段的报告按"缺少 `parse_strategy_a` 键"计数，把 6 条 P 阶段记录误判为解析失败——它们根本没有被请求过答案阶段。根因是两个阶段的 checkpoint 被混在一起统计。修复：按 stage 分开统计，并同时报告空回复数。教训：**自造指标若不定义清楚分母，就会自己骗自己**。

**4）人类基线最终没有采集到数据。** 协议、空 CSV 模板、同口径评分脚本、文献参照值都已建好，脚本在空模板上会明确拒绝出数、不写任何指标文件——但人类侧证据在本轮就是**缺失**的，人类—模型对比不可得。这是主动选择的诚实：宁可留空，也不填一组编造的数字。

## 二、结果层面的两个意外发现

**1）AUROC2 低于 0.5。** 两个模型的预答置信度 AUROC2 为 0.387 与 0.441，都低于"恒定给 0.5"这一无信息基线（= 0.500）。这不是"校准得不好"，而是**轻度反诊断**：越自信越容易错。真正的结构藏在分层结果里——`multihop` 域 ΔE 高达 +0.850（重度过度自信），`fictional` 域 ΔE 低至 −0.953（答对了却不敢信）。**元认知的失败是领域驱动的，方向还会翻转**，全局均值没有解释力。

**2）ECE 能被温度缩放压低，AUROC2 一动不动。** T=50 把 ECE 从 0.5325 压到 0.1689，而 AUROC2 恰好停在 0.3869。这说明两者测的是**两件事**：ECE 问"标签读数是否可信"，AUROC2 问"模型能否按对错给自己的题排序"。事后校准只是单调重标定，**买得到校准，买不到元认知**。这是整个 benchmark 最想留下的结论。

## 三、改进方案

把 KB-C 从 20 题扩到 120 题以上（当前 utility 的 CI 宽约 ±0.21，分辨不了 0.02 量级的策略差异）；KB-A 每域补到 30 题以上以稳定分层；补一轮 prompt 改写与 seed 方差实验；真正采集人类基线（10–20 名被试）；再加入"作答后置信"作为对照臂，直接检验预测性元认知与事后校准的分离。
*（内容由AI生成，仅供参考）*
