# KnowBound -- full-run results (real, reproducible)

- generated: 2026-10-05T13:20:47
- run tag: `full`
- bootstrap: 2000 resamples, alpha=0.05, unit=item, paired for model-vs-model
- every number below is computed from `logs/scored_*.jsonl` by `python -m knowbound compare`; nothing is hand-entered

## model `gemma4:e4b`

items: kb_a=60, kb_b=40, kb_c=20

### KB-A -- pre-answer confidence (does it know before answering?)

| metric | value | 95% CI (bootstrap over items) |
| --- | --- | --- |
| n | 60 | |
| accuracy | 0.7000 | 0.7000 [0.5833, 0.8167] |
| AUROC2 | 0.3869 | 0.3869 [0.2812, 0.5014] |
| ECE-10 | 0.5325 | 0.5325 [0.4083, 0.6567] |
| Brier | 0.5218 | 0.5218 [0.4001, 0.6462] |
| ΔE (signed) | 0.0558 | 0.0558 [-0.1300, 0.2301] |
| |ΔE| | 0.5358 | 0.5358 [0.4133, 0.6642] |

accuracy-binned AUROC2 (discrimination held at fixed accuracy):

| stratum | n | accuracy | AUROC2 | ECE-10 |
| --- | --- | --- | --- | --- |
| 1 | 10 | 0.7000 | 1.0000 | 0.2850 |
| 2 | 25 | 0.7200 | 0.5873 | 0.2720 |
| 3 | 25 | 0.6800 | 0.0588 | 0.8920 |

n-weighted pooled AUROC2 = 0.4359

per-domain:

| domain | n | acc | AUROC2 | ΔE |
| --- | --- | --- | --- | --- |
| arith | 15 | 0.7333 | 0.5000 | 0.2667 |
| fictional | 15 | 1.0000 | n/a | -0.9533 |
| longtail | 15 | 0.9333 | 0.4286 | 0.0600 |
| multihop | 15 | 0.1333 | 0.6923 | 0.8500 |

trivial-confidence baselines (identical items, identical metric code):

| policy | acc | AUROC2 | ECE-10 | Brier | ΔE |
| --- | --- | --- | --- | --- | --- |
| model | 0.7000 | 0.3869 | 0.5325 | 0.5218 | 0.0558 |
| random_confidence | 0.7000 | 0.4259 | 0.3864 | 0.3958 | -0.2448 |
| constant_100 | 0.7000 | 0.5000 | 0.3000 | 0.3000 | 0.3000 |
| constant_50 | 0.7000 | 0.5000 | 0.2000 | 0.2500 | -0.2000 |
| oracle_confidence | 0.7000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |

calibration ablation (temperature T = 50.000):

| stage | ECE-10 | AUROC2 | Brier |
| --- | --- | --- | --- |
| raw | 0.5325 | 0.3869 | 0.5218 |
| + temperature | 0.1689 | 0.3869 | 0.2550 |
| + isotonic | 0.2660 | 0.4365 | 0.2877 |

_calibrators are fitted and evaluated on the same items (optimistic ECE); temperature scaling is strictly monotone so its AUROC2 change is exactly 0, while isotonic creates ties, and the 0.5-credit tie convention can shift AUROC2 either way -- such a shift is an artefact, not extra discrimination; the raw AUROC2 is therefore the headline metric_

### KB-B -- knowledge-boundary detection (fictional vs real sources)

| metric | value | 95% CI |
| --- | --- | --- |
| n (answerable / unanswerable) | 40 (20 / 20) | |
| accuracy (overall) | 1.0000 | 1.0000 [1.0000, 1.0000] |
| accuracy (answerable only) | 1.0000 | 1.0000 [1.0000, 1.0000] |
| over-claim rate (unanswerable) | 0.0000 | 0.0000 [0.0000, 0.0000] |
| abstention AUROC | 0.7500 | 0.7500 [0.6389, 0.8571] |
| Balanced Abstention Score | 1.0000 | 1.0000 [1.0000, 1.0000] |
| AUROC2 (confidence) | n/a | n/a |
| ECE-10 | 0.2400 | 0.2400 [0.1175, 0.3676] |

| control | Balanced Abstention | note |
| --- | --- | --- |
| always abstain | 0.5000 | collapses to max abstention recall, zero answer recall |
| never abstain | 0.5000 | |
| model | 1.0000 | |

### KB-C -- strategic help-seeking under a budget

| metric | value | 95% CI |
| --- | --- | --- |
| n | 20 | |
| net utility (model) | 0.5200 | 0.5200 [0.3050, 0.7250] |
| help calls | 2 | 0.1000 [0.0000, 0.2500] |
| ask-help AUROC vs unanswerable | 0.6667 | 0.6667 [0.5000, 0.8750] |
| normalised utility (vs always_do_it, / (oracle - always_do_it)) | -0.8571 | |

| policy | utility |
| --- | --- |
| model (metacognitive) | 0.5200 |
| always_do_it | 0.7000 |
| always_ask_help | 0.6600 |
| random (coin-flip mix of the two) | 0.6800 |
| oracle_policy (upper bound) | 0.9100 |
| share of help spent on unanswerable items | 1.0000 |

paired against the reference policies:

| contrast | Δ utility | 95% CI | verdict |
| --- | --- | --- | --- |
| model_minus_do_it | -0.1800 | [-0.5150, 0.2050] | indistinguishable from do_it at this n (95% CI [-0.5150, +0.2050] spans 0) |
| model_minus_ask_help | 0.3100 | [0.0950, 0.5152] | above ask_help (95% CI excludes 0) |
| model_minus_random | 0.0650 | [-0.2103, 0.3250] | indistinguishable from random at this n (95% CI [-0.2103, +0.3250] spans 0) |

_normalised utility is (model - always_do_it) / (oracle - always_do_it); 0 means the model's help-seeking matches simply always answering, 1 means it matches the oracle policy, negative means the help-seeking policy costs utility relative to never asking._

## model `Librellama/gemma4:e2b-Uncensored`

items: kb_a=60, kb_b=40, kb_c=20

### KB-A -- pre-answer confidence (does it know before answering?)

| metric | value | 95% CI (bootstrap over items) |
| --- | --- | --- |
| n | 60 | |
| accuracy | 0.6500 | 0.6500 [0.5167, 0.7667] |
| AUROC2 | 0.4408 | 0.4408 [0.3108, 0.5828] |
| ECE-10 | 0.5152 | 0.5152 [0.3982, 0.6440] |
| Brier | 0.5071 | 0.5071 [0.3905, 0.6254] |
| ΔE (signed) | 0.0852 | 0.0852 [-0.0942, 0.2505] |
| |ΔE| | 0.5408 | 0.5408 [0.4250, 0.6617] |

accuracy-binned AUROC2 (discrimination held at fixed accuracy):

| stratum | n | accuracy | AUROC2 | ECE-10 |
| --- | --- | --- | --- | --- |
| 1 | 10 | 0.6000 | 0.8333 | 0.2730 |
| 2 | 25 | 0.7200 | 0.7857 | 0.2540 |
| 3 | 25 | 0.6000 | 0.0467 | 0.8732 |

n-weighted pooled AUROC2 = 0.4857

per-domain:

| domain | n | acc | AUROC2 | ΔE |
| --- | --- | --- | --- | --- |
| arith | 15 | 0.7333 | 0.4659 | 0.2573 |
| fictional | 15 | 0.9333 | 0.0357 | -0.8600 |
| longtail | 15 | 0.8667 | 0.6538 | 0.1200 |
| multihop | 15 | 0.0667 | 0.7857 | 0.8233 |

trivial-confidence baselines (identical items, identical metric code):

| policy | acc | AUROC2 | ECE-10 | Brier | ΔE |
| --- | --- | --- | --- | --- | --- |
| model | 0.6500 | 0.4408 | 0.5152 | 0.5071 | 0.0852 |
| random_confidence | 0.6500 | 0.4664 | 0.3698 | 0.3802 | -0.1948 |
| constant_100 | 0.6500 | 0.5000 | 0.3500 | 0.3500 | 0.3500 |
| constant_50 | 0.6500 | 0.5000 | 0.1500 | 0.2500 | -0.1500 |
| oracle_confidence | 0.6500 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |

calibration ablation (temperature T = 50.000):

| stage | ECE-10 | AUROC2 | Brier |
| --- | --- | --- | --- |
| raw | 0.5152 | 0.4408 | 0.5071 |
| + temperature | 0.1267 | 0.4408 | 0.2563 |
| + isotonic | 0.1917 | 0.5183 | 0.2840 |

_calibrators are fitted and evaluated on the same items (optimistic ECE); temperature scaling is strictly monotone so its AUROC2 change is exactly 0, while isotonic creates ties, and the 0.5-credit tie convention can shift AUROC2 either way -- such a shift is an artefact, not extra discrimination; the raw AUROC2 is therefore the headline metric_

### KB-B -- knowledge-boundary detection (fictional vs real sources)

| metric | value | 95% CI |
| --- | --- | --- |
| n (answerable / unanswerable) | 40 (20 / 20) | |
| accuracy (overall) | 0.9000 | 0.9000 [0.8000, 0.9750] |
| accuracy (answerable only) | 1.0000 | 1.0000 [1.0000, 1.0000] |
| over-claim rate (unanswerable) | 0.2000 | 0.2000 [0.0476, 0.3913] |
| abstention AUROC | 0.8000 | 0.8000 [0.6842, 0.9048] |
| Balanced Abstention Score | 0.9000 | 0.9000 [0.8043, 0.9762] |
| AUROC2 (confidence) | 0.6562 | 0.6562 [0.4147, 0.8529] |
| ECE-10 | 0.2337 | 0.2337 [0.1238, 0.3563] |

| control | Balanced Abstention | note |
| --- | --- | --- |
| always abstain | 0.5000 | collapses to max abstention recall, zero answer recall |
| never abstain | 0.5000 | |
| model | 0.9000 | |

### KB-C -- strategic help-seeking under a budget

| metric | value | 95% CI |
| --- | --- | --- |
| n | 20 | |
| net utility (model) | 0.4850 | 0.4850 [0.2700, 0.6850] |
| help calls | 1 | 0.0500 [0.0000, 0.1500] |
| ask-help AUROC vs unanswerable | 0.5833 | 0.5833 [0.5000, 0.7500] |
| normalised utility (vs always_do_it, / (oracle - always_do_it)) | -1.0238 | |

| policy | utility |
| --- | --- |
| model (metacognitive) | 0.4850 |
| always_do_it | 0.7000 |
| always_ask_help | 0.6600 |
| random (coin-flip mix of the two) | 0.6800 |
| oracle_policy (upper bound) | 0.9100 |
| share of help spent on unanswerable items | 1.0000 |

paired against the reference policies:

| contrast | Δ utility | 95% CI | verdict |
| --- | --- | --- | --- |
| model_minus_do_it | -0.2150 | [-0.5650, 0.1850] | indistinguishable from do_it at this n (95% CI [-0.5650, +0.1850] spans 0) |
| model_minus_ask_help | 0.2750 | [0.0746, 0.4900] | above ask_help (95% CI excludes 0) |
| model_minus_random | 0.0300 | [-0.2550, 0.3050] | indistinguishable from random at this n (95% CI [-0.2550, +0.3050] spans 0) |

_normalised utility is (model - always_do_it) / (oracle - always_do_it); 0 means the model's help-seeking matches simply always answering, 1 means it matches the oracle policy, negative means the help-seeking policy costs utility relative to never asking._

## model-vs-model (paired bootstrap)

diff = `Librellama/gemma4:e2b-Uncensored` - `gemma4:e4b`, same items, paired resampling.

### KB-A (pre-answer confidence)

| metric | Δ | 95% CI of Δ | verdict |
| --- | --- | --- | --- |
| abs_delta_e | 0.0050 | [-0.0780, 0.0977] | no detectable difference at this n (95% CI [-0.0780, +0.0977] spans 0) |
| accuracy | -0.0500 | [-0.1333, 0.0333] | no detectable difference at this n (95% CI [-0.1333, +0.0333] spans 0) |
| auroc2 | 0.0539 | [-0.0361, 0.1484] | no detectable difference at this n (95% CI [-0.0361, +0.1484] spans 0) |
| brier | -0.0147 | [-0.1029, 0.0775] | no detectable difference at this n (95% CI [-0.1029, +0.0775] spans 0) |
| delta_e | 0.0293 | [-0.0587, 0.1289] | no detectable difference at this n (95% CI [-0.0587, +0.1289] spans 0) |
| ece10 | -0.0173 | [-0.0946, 0.0838] | no detectable difference at this n (95% CI [-0.0946, +0.0838] spans 0) |

### KB-B (knowledge-boundary detection)

| metric | Δ | 95% CI of Δ | verdict |
| --- | --- | --- | --- |
| abstention_auroc_from_confidence | 0.0500 | [0.0000, 0.1250] | no detectable difference at this n (95% CI [+0.0000, +0.1250] spans 0) |
| accuracy_on_answerable | 0.0000 | [0.0000, 0.0000] | no detectable difference at this n (95% CI [+0.0000, +0.0000] spans 0) |
| accuracy_overall | -0.1000 | [-0.2000, -0.0250] | separates the two models (95% CI excludes 0) |
| auroc2_confidence | n/a | [n/a, n/a] | undefined (too few defined resamples) |
| balanced_abstention_score | -0.1000 | [-0.1945, -0.0250] | separates the two models (95% CI excludes 0) |
| delta_e | 0.1987 | [0.0563, 0.3763] | separates the two models (95% CI excludes 0) |
| ece10 | -0.0063 | [-0.1037, 0.1025] | no detectable difference at this n (95% CI [-0.1037, +0.1025] spans 0) |
| over_claim_rate | 0.2000 | [0.0435, 0.3750] | separates the two models (95% CI excludes 0) |

### KB-C (strategic help-seeking)

| metric | Δ | 95% CI of Δ | verdict |
| --- | --- | --- | --- |
| ask_help_auroc_vs_unanswerable | -0.0833 | [-0.2500, 0.0000] | no detectable difference at this n (95% CI [-0.2500, +0.0000] spans 0) |
| help_call_rate | -0.0500 | [-0.1500, 0.0000] | no detectable difference at this n (95% CI [-0.1500, +0.0000] spans 0) |
| model_minus_ask_help | -0.0350 | [-0.2000, 0.1300] | no detectable difference at this n (95% CI [-0.2000, +0.1300] spans 0) |
| model_minus_do_it | -0.0350 | [-0.2000, 0.1150] | no detectable difference at this n (95% CI [-0.2000, +0.1150] spans 0) |
| model_minus_random | -0.0350 | [-0.2000, 0.1300] | no detectable difference at this n (95% CI [-0.2000, +0.1300] spans 0) |
| utility | -0.0350 | [-0.2000, 0.1300] | no detectable difference at this n (95% CI [-0.2000, +0.1300] spans 0) |

### discrimination summary

- **KB-A (pre-answer confidence)**
  - separates the two models: none
  - no detectable difference at this n: abs_delta_e, accuracy, auroc2, brier, delta_e, ece10
- **KB-B (knowledge-boundary detection)**
  - separates the two models: accuracy_overall, balanced_abstention_score, delta_e, over_claim_rate
  - no detectable difference at this n: abstention_auroc_from_confidence, accuracy_on_answerable, auroc2_confidence, ece10
- **KB-C (strategic help-seeking)**
  - separates the two models: none
  - no detectable difference at this n: ask_help_auroc_vs_unanswerable, help_call_rate, model_minus_ask_help, model_minus_do_it, model_minus_random, utility

## what these numbers do and do not support

- **gemma4:e4b / KB-A**: above-chance metacognitive discrimination is **not** supported -- AUROC2 = 0.387 with 95% CI [0.2812, 0.5014], which straddles or sits below 0.5 (ΔE = +0.056, |ΔE| = 0.536); a constant-confidence policy scores exactly 0.500 on the same items and random confidence 0.4259, so the model's confidence is not merely uninformative but on this item set mildly *anti*-diagnostic.
- **gemma4:e4b / KB-A**: calibration error is domain-driven and flips sign: largest over-confidence in `multihop` (ΔE = +0.850, acc = 0.133), largest under-confidence in `fictional` (ΔE = -0.953, acc = 1.000). Global ECE-10 = 0.532 hides that sign flip, so a blanket 'the model is over-confident' claim is only true per-domain.
- **gemma4:e4b / KB-B**: over-claim rate on fictional sources = 0.000 (95% CI [0.0000, 0.0000]) with answerable accuracy 1.000; Balanced Abstention = 1.000 (95% CI [1.0000, 1.0000]) against 0.500 for both 'always abstain' and 'never abstain', so the boundary behaviour is two-sided here, not a degenerate always-answer or always-refuse policy.
- **gemma4:e4b / KB-C**: under the budget the model's net utility (0.520) is not significantly below `always_do_it` (0.700); Δ = -0.180 (95% CI [-0.515, +0.205]). It spends 2/20 help calls, 100% of them on unanswerable items, and the oracle policy is 0.910 -- so there is headroom, but at n=20 this run cannot claim the help-seeking policy beats simply answering.
- **Librellama/gemma4:e2b-Uncensored / KB-A**: above-chance metacognitive discrimination is **not** supported -- AUROC2 = 0.441 with 95% CI [0.3108, 0.5828], which straddles or sits below 0.5 (ΔE = +0.085, |ΔE| = 0.541); a constant-confidence policy scores exactly 0.500 on the same items and random confidence 0.4664, so the model's confidence is not merely uninformative but on this item set mildly *anti*-diagnostic.
- **Librellama/gemma4:e2b-Uncensored / KB-A**: calibration error is domain-driven and flips sign: largest over-confidence in `multihop` (ΔE = +0.823, acc = 0.067), largest under-confidence in `fictional` (ΔE = -0.860, acc = 0.933). Global ECE-10 = 0.515 hides that sign flip, so a blanket 'the model is over-confident' claim is only true per-domain.
- **Librellama/gemma4:e2b-Uncensored / KB-B**: over-claim rate on fictional sources = 0.200 (95% CI [0.0476, 0.3913]) with answerable accuracy 1.000; Balanced Abstention = 0.900 (95% CI [0.8043, 0.9762]) against 0.500 for both 'always abstain' and 'never abstain', so the boundary behaviour is two-sided here, not a degenerate always-answer or always-refuse policy.
- **Librellama/gemma4:e2b-Uncensored / KB-C**: under the budget the model's net utility (0.485) is not significantly below `always_do_it` (0.700); Δ = -0.215 (95% CI [-0.565, +0.185]). It spends 1/20 help calls, 100% of them on unanswerable items, and the oracle policy is 0.910 -- so there is headroom, but at n=20 this run cannot claim the help-seeking policy beats simply answering.
- **Librellama/gemma4:e2b-Uncensored vs gemma4:e4b / KB-A (pre-answer confidence)**: the two models are indistinguishable on every metric at this n (abs_delta_e, accuracy, auroc2, brier, delta_e, ece10); the smaller model is not measurably worse here.
- **Librellama/gemma4:e2b-Uncensored vs gemma4:e4b / KB-B (knowledge-boundary detection)**: separated by accuracy_overall, balanced_abstention_score, delta_e, over_claim_rate; indistinguishable on abstention_auroc_from_confidence, accuracy_on_answerable, auroc2_confidence, ece10.
- **Librellama/gemma4:e2b-Uncensored vs gemma4:e4b / KB-C (strategic help-seeking)**: the two models are indistinguishable on every metric at this n (ask_help_auroc_vs_unanswerable, help_call_rate, model_minus_ask_help, model_minus_do_it, model_minus_random, utility); the smaller model is not measurably worse here.
- **Scope limit**: n = 60/40/20 items per family, one local Ollama runtime, one generation per item (temperature 0), two Q4_K_M models. Intervals are item-level bootstrap and account for sampling of *items* only -- not for prompt phrasing, decoding seed or runtime version. Claims about 'LLMs' in general are outside what this data can support.

## runtime, failures, degradation

| model | family | items | calls | ok | mean call (s) | first call (s) | parse strategies | failed items |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gemma4:e4b | kb_a | 60 | 120 | 60 | 0.873 | 9.212 | {"strict": 120} | none |
| gemma4:e4b | kb_b | 40 | 40 | 40 | 0.506 | 0.692 | {"strict": 40} | none |
| gemma4:e4b | kb_c | 20 | 20 | 20 | 0.604 | 0.736 | {"strict": 20} | none |
| Librellama/gemma4:e2b-Uncensored | kb_a | 60 | 120 | 60 | 0.430 | 8.497 | {"strict": 120} | none |
| Librellama/gemma4:e2b-Uncensored | kb_b | 40 | 40 | 40 | 0.391 | 0.424 | {"strict": 40} | none |
| Librellama/gemma4:e2b-Uncensored | kb_c | 20 | 20 | 20 | 0.439 | 0.469 | {"strict": 20} | none |

## reproduce

```
cd <project root>                      # .../lenovo_C9_benchmark
# 0. runtime must be up:  ollama serve   (listens on 127.0.0.1:11434)
python -m knowbound generate           # rebuild data/kb_*.jsonl from the fixed seed
python -m knowbound run --tag full --model gemma4:e4b
python -m knowbound run --tag full --model Librellama/gemma4:e2b-Uncensored
python -m knowbound manifest --tag full --models "gemma4:e4b,Librellama/gemma4:e2b-Uncensored"
python -m knowbound compare --tag full --n-boot 2000
python -m knowbound selftest           # offline assertions, no model needed
python -m pytest tests -q              # if pytest is available
```

Per-model files written by `run`: `results/metrics_full_<slug>.json`, `results/summary_full_<slug>.md`, `logs/transcript_full_<fam>_<slug>.jsonl` (raw prompt + raw response + latency + tag/quant/ollama version/seed), `logs/scored_full_<fam>_<slug>.jsonl` (parsed answer/confidence/outcome) and `logs/run_manifest_full_<slug>.json`. The multi-model files read by a human are `results/metrics.json` and `results/summary.md`, produced by `compare`.

