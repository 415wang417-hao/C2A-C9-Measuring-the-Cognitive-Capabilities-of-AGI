# KnowBound -- results summary

- model: `gemma4:e4b`
- tag: `smoke`
- items: kb_a=3, kb_b=3, kb_c=3
- generated: 2026-10-05 12:08:56

## KB-A  pre-answer confidence prediction

| metric | value |
| --- | --- |
| n | 3 |
| accuracy | 0.6667 |
| AUROC2 | 0.5000 |
| ECE-10 | 0.3333 |
| Brier | 0.3333 |
| delta_E (signed) | 0.3333 |
| |delta_E| | 0.3333 |

### per-domain

| domain | n | acc | AUROC2 | ΔE | |ΔE| |
| --- | --- | --- | --- | --- | --- |
| arith | 3 | 0.6667 | 0.5000 | 0.3333 | 0.3333 |

### baselines (identical items, identical metric code)

| policy | acc | AUROC2 | ECE-10 | Brier | ΔE |
| --- | --- | --- | --- | --- | --- |
| model | 0.6667 | 0.5000 | 0.3333 | 0.3333 | 0.3333 |
| random_confidence | 0.6667 | 1.0000 | 0.5271 | 0.3473 | -0.4241 |
| constant_100 | 0.6667 | 0.5000 | 0.3333 | 0.3333 | 0.3333 |
| constant_50 | 0.6667 | 0.5000 | 0.1667 | 0.2500 | -0.1667 |
| oracle_confidence | 0.6667 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |

### calibration ablation (calibration != metacognition)

temperature T = 19.932

| stage | ECE-10 | AUROC2 | Brier |
| --- | --- | --- | --- |
| raw | 0.3333 | 0.5000 | 0.3333 |
| temperature | 0.0000 | 0.5000 | 0.2222 |
| isotonic | 0.0000 | 0.5000 | 0.2222 |

_caveat_: calibrators are fitted and evaluated on the same items (optimistic ECE); temperature scaling is strictly monotone so its AUROC2 change is exactly 0, while isotonic creates ties, and the 0.5-credit tie convention can shift AUROC2 either way -- such a shift is an artefact, not extra discrimination; the raw AUROC2 is therefore the headline metric

### difficulty strata

| difficulty | n | acc | AUROC2 |
| --- | --- | --- | --- |
| 1 | 1 | 1.0000 | nan |
| 2 | 1 | 1.0000 | nan |
| 3 | 1 | 0.0000 | nan |

## KB-B  knowledge-boundary detection

| metric | value |
| --- | --- |
| n (answerable / unanswerable) | 3 (1 / 2) |
| accuracy (answerable only) | 1.0000 |
| over-claim rate on unanswerable | 0.0000 |
| abstention AUROC (from confidence) | 0.7500 |
| balanced abstention score | 1.0000 |
| AUROC2 (confidence) | nan |
| ECE-10 | 0.3333 |

| control | balanced abstention | note |
| --- | --- | --- |
| always abstain | 0.5000 | collapses to max abstention recall, zero answer recall |
| never abstain | 0.5000 | | |
| model | 1.0000 | |

## KB-C  strategic help-seeking

| metric | value |
| --- | --- |
| n | 3 |
| utility (mean points) | 0.2333 |
| help calls granted | 1 |
| ask-help AUROC vs unanswerable | 1.0000 |
| normalised utility vs oracle | -1.8571 |

| policy | utility |
| --- | --- |
| model | 0.2333 |
| always_do_it | 0.6667 |
| always_ask_help | 0.7000 |
| oracle | 0.9000 |

