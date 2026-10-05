# KnowBound -- results summary

- model: `Librellama/gemma4:e2b-Uncensored`
- tag: `full`
- items: kb_a=60, kb_b=40, kb_c=20
- generated: 2026-10-05 12:30:35

## KB-A  pre-answer confidence prediction

| metric | value |
| --- | --- |
| n | 60 |
| accuracy | 0.6500 |
| AUROC2 | 0.4408 |
| ECE-10 | 0.5152 |
| Brier | 0.5071 |
| delta_E (signed) | 0.0852 |
| |delta_E| | 0.5408 |

### per-domain

| domain | n | acc | AUROC2 | ΔE | |ΔE| |
| --- | --- | --- | --- | --- | --- |
| arith | 15 | 0.7333 | 0.4659 | 0.2573 | 0.2733 |
| fictional | 15 | 0.9333 | 0.0357 | -0.8600 | 0.9267 |
| longtail | 15 | 0.8667 | 0.6538 | 0.1200 | 0.1400 |
| multihop | 15 | 0.0667 | 0.7857 | 0.8233 | 0.8233 |

### baselines (identical items, identical metric code)

| policy | acc | AUROC2 | ECE-10 | Brier | ΔE |
| --- | --- | --- | --- | --- | --- |
| model | 0.6500 | 0.4408 | 0.5152 | 0.5071 | 0.0852 |
| random_confidence | 0.6500 | 0.4664 | 0.3698 | 0.3802 | -0.1948 |
| constant_100 | 0.6500 | 0.5000 | 0.3500 | 0.3500 | 0.3500 |
| constant_50 | 0.6500 | 0.5000 | 0.1500 | 0.2500 | -0.1500 |
| oracle_confidence | 0.6500 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |

### calibration ablation (calibration != metacognition)

temperature T = 50.000

| stage | ECE-10 | AUROC2 | Brier |
| --- | --- | --- | --- |
| raw | 0.5152 | 0.4408 | 0.5071 |
| temperature | 0.1267 | 0.4408 | 0.2563 |
| isotonic | 0.1917 | 0.5183 | 0.2840 |

_caveat_: calibrators are fitted and evaluated on the same items (optimistic ECE); temperature scaling is strictly monotone so its AUROC2 change is exactly 0, while isotonic creates ties, and the 0.5-credit tie convention can shift AUROC2 either way -- such a shift is an artefact, not extra discrimination; the raw AUROC2 is therefore the headline metric

### difficulty strata

| difficulty | n | acc | AUROC2 |
| --- | --- | --- | --- |
| 1 | 10 | 0.6000 | 0.8333 |
| 2 | 25 | 0.7200 | 0.7857 |
| 3 | 25 | 0.6000 | 0.0467 |

## KB-B  knowledge-boundary detection

| metric | value |
| --- | --- |
| n (answerable / unanswerable) | 40 (20 / 20) |
| accuracy (answerable only) | 1.0000 |
| over-claim rate on unanswerable | 0.2000 |
| abstention AUROC (from confidence) | 0.8000 |
| balanced abstention score | 0.9000 |
| AUROC2 (confidence) | 0.6562 |
| ECE-10 | 0.2337 |

| control | balanced abstention | note |
| --- | --- | --- |
| always abstain | 0.5000 | collapses to max abstention recall, zero answer recall |
| never abstain | 0.5000 | | |
| model | 0.9000 | |

## KB-C  strategic help-seeking

| metric | value |
| --- | --- |
| n | 20 |
| utility (mean points) | 0.4850 |
| help calls granted | 1 |
| ask-help AUROC vs unanswerable | 0.5833 |
| normalised utility vs oracle | -1.0238 |

| policy | utility |
| --- | --- |
| model | 0.4850 |
| always_do_it | 0.7000 |
| always_ask_help | 0.6600 |
| oracle | 0.9100 |

