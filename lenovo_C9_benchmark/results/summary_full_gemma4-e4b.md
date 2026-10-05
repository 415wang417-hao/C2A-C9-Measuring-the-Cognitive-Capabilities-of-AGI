# KnowBound -- results summary

- model: `gemma4:e4b`
- tag: `full`
- items: kb_a=60, kb_b=40, kb_c=20
- generated: 2026-10-05 13:19:40

## KB-A  pre-answer confidence prediction

| metric | value |
| --- | --- |
| n | 60 |
| accuracy | 0.7000 |
| AUROC2 | 0.3869 |
| ECE-10 | 0.5325 |
| Brier | 0.5218 |
| delta_E (signed) | 0.0558 |
| |delta_E| | 0.5358 |

### per-domain

| domain | n | acc | AUROC2 | ΔE | |ΔE| |
| --- | --- | --- | --- | --- | --- |
| arith | 15 | 0.7333 | 0.5000 | 0.2667 | 0.2667 |
| fictional | 15 | 1.0000 | nan | -0.9533 | 0.9533 |
| longtail | 15 | 0.9333 | 0.4286 | 0.0600 | 0.0733 |
| multihop | 15 | 0.1333 | 0.6923 | 0.8500 | 0.8500 |

### baselines (identical items, identical metric code)

| policy | acc | AUROC2 | ECE-10 | Brier | ΔE |
| --- | --- | --- | --- | --- | --- |
| model | 0.7000 | 0.3869 | 0.5325 | 0.5218 | 0.0558 |
| random_confidence | 0.7000 | 0.4259 | 0.3864 | 0.3958 | -0.2448 |
| constant_100 | 0.7000 | 0.5000 | 0.3000 | 0.3000 | 0.3000 |
| constant_50 | 0.7000 | 0.5000 | 0.2000 | 0.2500 | -0.2000 |
| oracle_confidence | 0.7000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |

### calibration ablation (calibration != metacognition)

temperature T = 50.000

| stage | ECE-10 | AUROC2 | Brier |
| --- | --- | --- | --- |
| raw | 0.5325 | 0.3869 | 0.5218 |
| temperature | 0.1689 | 0.3869 | 0.2550 |
| isotonic | 0.2660 | 0.4365 | 0.2877 |

_caveat_: calibrators are fitted and evaluated on the same items (optimistic ECE); temperature scaling is strictly monotone so its AUROC2 change is exactly 0, while isotonic creates ties, and the 0.5-credit tie convention can shift AUROC2 either way -- such a shift is an artefact, not extra discrimination; the raw AUROC2 is therefore the headline metric

### difficulty strata

| difficulty | n | acc | AUROC2 |
| --- | --- | --- | --- |
| 1 | 10 | 0.7000 | 1.0000 |
| 2 | 25 | 0.7200 | 0.5873 |
| 3 | 25 | 0.6800 | 0.0588 |

## KB-B  knowledge-boundary detection

| metric | value |
| --- | --- |
| n (answerable / unanswerable) | 40 (20 / 20) |
| accuracy (answerable only) | 1.0000 |
| over-claim rate on unanswerable | 0.0000 |
| abstention AUROC (from confidence) | 0.7500 |
| balanced abstention score | 1.0000 |
| AUROC2 (confidence) | nan |
| ECE-10 | 0.2400 |

| control | balanced abstention | note |
| --- | --- | --- |
| always abstain | 0.5000 | collapses to max abstention recall, zero answer recall |
| never abstain | 0.5000 | | |
| model | 1.0000 | |

## KB-C  strategic help-seeking

| metric | value |
| --- | --- |
| n | 20 |
| utility (mean points) | 0.5200 |
| help calls granted | 2 |
| ask-help AUROC vs unanswerable | 0.6667 |
| normalised utility vs oracle | -0.8571 |

| policy | utility |
| --- | --- |
| model | 0.5200 |
| always_do_it | 0.7000 |
| always_ask_help | 0.6600 |
| oracle | 0.9100 |

