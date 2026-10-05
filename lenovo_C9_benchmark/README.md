# KnowBound — a metacognition benchmark for knowledge boundaries

**KnowBound** measures whether a language model can **predict its own errors before it makes them**,
and whether it can **tell the difference between a question it can answer and one it cannot**.
It is designed for *Track 2 — Metacognition*: the target construct is the model's **second-order
judgement about its own first-order ability**, not its knowledge as such.

Four design decisions separate KnowBound from the existing landscape (ECE on logits,
binary selective prediction, verbalised-confidence probing, TruthfulQA-style knowledge tests):

| Design decision | Why it matters |
| --- | --- |
| **Answer-free confidence probing (KB-A)** | The confidence stage sees the *question only*; no answer, no draft. The model cannot rationalise an already-produced answer. |
| **Paired fictional / real items (KB-B)** | Every fictional entity is matched to a real entity of the *same template*, so item format, difficulty and domain are held constant; only **existence** differs. A model that always abstains is detected by the balanced abstention score. |
| **Behavioural consequence (KB-C)** | Metacognition must *pay off*: the model spends a limited help budget (6 calls) and is scored on realised utility, not on a self-report. |
| **Difficulty stratification** | Accuracy is reported inside difficulty strata so that *calibration/discrimination* can be compared between models whose first-order accuracy differs. |


**Status:** the full run is **done** on two local models — `gemma4:e4b` and
`Librellama/gemma4:e2b-Uncensored`, 180 model calls each, 360 calls total, 0 failures, 0 parse
failures. Headline numbers are in §8 (`results/summary.md`, `results/metrics.json`); the
human-baseline materials are in §9. The headline finding is a **null result** on KB-A (no
above-chance second-order discrimination) and **two-sided** boundary behaviour on KB-B.

---

## 1. Requirements

* Windows 10/11 (PowerShell 5.1+) or any OS with the same Python entry points
* Python 3.9+ with `requests` and `numpy` (nothing heavier is used or needed)
* [Ollama](https://ollama.com) reachable at `http://127.0.0.1:11434` with the model under test, e.g.

```powershell
ollama pull gemma4:e4b        # 7.5B, Q4_K_M — the reference configuration
ollama list
```

Calls are issued **strictly serially** (the reference machine had ~2.3 GB free RAM and an 8 GB
laptop GPU), with a per-item checkpoint after every call.

## 2. One-click reproduction

```powershell
cd <project root>
.\run_all.ps1                  # offline self-test + generate + smoke test (3 items/family, ~1 min)
.\run_all.ps1 -Mode full       # full evaluation (180 model calls) + full report
.\run_all.ps1 -Mode report     # rebuild every report from the stored transcripts, no model calls
.\run_all.ps1 -Mode selftest   # offline, no model required
```

Equivalent manual invocation:

```powershell
python -m knowbound selftest
python -m knowbound generate
python -m knowbound smoke  --model "gemma4:e4b" --limit 3
python -m knowbound run    --model "gemma4:e4b"          # full: 60/40/20 items
python -m knowbound report --tag smoke --model "gemma4:e4b"
```

`tests\test_knowbound.py` is a thin pytest-compatible wrapper around the same assertions
(`python tests\test_knowbound.py` runs it without pytest installed).

Scoring a human-baseline CSV with the *same* metric code as the model runs:

```powershell
python human_baseline\lenovo_human_scoring.py --csv human_baseline\lenovo_human_baseline_template.csv --validate-only
python human_baseline\lenovo_human_scoring.py --csv <collected.csv> --out-dir human_baseline
```

## 3. Directory layout

```
lenovo_C9_benchmark/
├─ knowbound/
│  ├─ generate.py     # programmatic item generators (fixed seed) -> data/*.jsonl
│  ├─ prompts.py      # system/user prompts; every prompt demands a single JSON object
│  ├─ models.py       # Ollama client: serial calls, think:false, robust JSON extraction, latency log
│  ├─ grading.py      # answer normalisation + grading (text/number/set matching, UNKNOWN handling)
│  ├─ metrics.py      # DeltaE, AUROC2, ECE-10, Brier, over-claim, BAS, abstention AUROC, strata
│  ├─ calibrators.py  # temperature scaling + isotonic regression (PAVA)
│  ├─ baselines.py    # random / constant / oracle baselines + calibration ablation
│  ├─ runner.py       # per-family runners, JSONL transcript checkpointing, resume
│  ├─ report.py       # aggregation -> metrics_*.json / summary_*.md / smoke_report.md
│  ├─ selftest.py     # 9 offline assertion groups (numeric ground truth by hand)
│  ├─ config.py       # config loader (YAML via PyYAML if present, else built-in mini parser)
│  └─ __main__.py     # CLI: generate | run | smoke | report | selftest
├─ configs/default.yaml
├─ data/              # generated items + manifest.json (seed, counts, generator config)
├─ logs/              # transcript_*.jsonl (raw model I/O) and scored_*.jsonl
├─ results/           # metrics_*.json, summary_*.md, smoke_report.md
├─ human_baseline/    # collection protocol + CSV template + scoring script (same metric code)
│  ├─ lenovo_human_baseline_protocol.md      # how to collect, CSV spec, same-footing scoring rules
│  ├─ lenovo_human_baseline_template.csv     # header-only template (no invented data)
│  ├─ lenovo_human_scoring.py                # scores a CSV via knowbound.{grading,metrics,baselines,stats}
│  └─ lenovo_human_baseline_literature.md    # real, citable human reference values (NOT collected here)
├─ tests/test_knowbound.py
├─ requirements.txt
└─ run_all.ps1
```

## 4. Task families and item schema

### KB-A — pre-answer confidence prediction (2 stages, 4 domains × 15 items = 60)

Two calls per item, checkpointed separately:

* **P stage** — the model sees only the question and must return `{"confidence": <0-100>}`;
  answering is forbidden by the prompt. Confidence is stored on [0, 1].
* **A stage** — the model answers; the answer is graded automatically.

```json
{"id":"KB-A-0000","family":"KB-A","domain":"arith","difficulty":1,
 "question":"Compute: 27 - 81","answer":"-54","accepted":["-54"],
 "answerable":true,"source":"programmatic (exact arithmetic)","meta":{"terms":2,"op":"-"}}
```

Domains: `arith` (programmatic arithmetic, 15), `multihop` (multi-hop symbolic chains with a
declared operator, 15), `longtail` (curated real long-tail facts, each carrying its `source`, 15),
`fictional` (**entities that cannot exist**; `answerable=false`, 15).

### KB-B — knowledge-boundary detection (40 = 20 fictional + 20 real)

Each fictional item is emitted from the same generator template as a real counterpart, so the two
halves are format-matched:

```json
{"id":"KB-B-0000","family":"KB-B","template":"element_number","label":0,"answerable":false,
 "difficulty":3,"question":"What is the atomic number of the chemical element Lomitheth?",
 "answer":"UNKNOWN","accepted":[],"source":"generated (fictional entity)",
 "meta":{"template":"element_number","entity":"Lomitheth","fictional_symbol":"LH"}}
```

Templates: `element_number`, `event_year`, `novel_author`, `capital` (10 items each half).
Per item the model returns `{"answer":…, "confidence":…, "can_answer":true|false}`; declaring
`UNKNOWN` / `can_answer=false` is the abstention signal.
Fictional entities are built from constructed morphemes and rejected against a blacklist of real
place names, elements and historical periods — a **best-effort structural** guarantee, not a proof.

### KB-C — strategic help-seeking (20 items, one pass, help budget 6)

Difficulty mix: 6 hard, 5 medium, 3 easy, 6 unanswerable (fictional). For each item the model must
choose `{"action":"do_it"|"ask_help", …}`. `ask_help` is only granted while budget remains; the
ground-truth answer is then supplied and the item scores **0.7 × 1.0** instead of 1.0.
`do_it` scores 1.0 when correct, 0.0 otherwise. Utility = mean score over the 20 items.

## 5. Metrics (all computed from the stored transcripts — nothing is hard-coded)

Let `c_i ∈ [0,1]` be the stated confidence and `k_i ∈ {0,1}` the graded correctness of item `i`.

| Metric | Formula | Read as |
| --- | --- | --- |
| accuracy | `mean(k_i)` | first-order ability |
| ΔE | `mean(c_i - k_i)` | signed bias (over/under-confidence) |
| \|ΔE\| | `mean(|c_i - k_i|)` | mean calibration gap |
| AUROC2 | `AUROC(conf, correct)` — rank-based, tie-aware | **second-order discrimination**: can the model's self-assessment sort *its own* correct from incorrect answers? |
| separation strength | `2·|AUROC2 − 0.5|` | scale-free variant when a signal may be inverted |
| ECE-10 | `Σ_b (n_b/N)·|acc_b − conf_b|` over 10 equal-width bins | calibration error |
| Brier | `mean((c_i − k_i)²)` | proper scoring rule |
| over-claim rate (KB-B) | `P(can_answer = true \| item unanswerable)` | hallucinated competence |
| abstention AUROC (KB-B/C) | `AUROC(need_help_score, unanswerable)` | can the model *rank* unanswerable items as riskier? |
| BAS (KB-B) | `0.5·(abstain-rate on unanswerable + answer-rate on answerable)` | balanced abstention; **an always-abstain policy is capped at 0.5 and flagged** |
| KB-C utility | `mean(score_i)`, score ∈ {1.0 correct, 0.7 helped, 0.0 wrong} | realised payoff of the policy |
| KB-C normalised utility | `(U_model − U_always_do_it) / (U_oracle − U_always_do_it)` | skill above the trivial `do_it` policy |

Stratified analysis reports `accuracy` and `AUROC2` inside difficulty bins, so a weak model and a
strong model can be compared on metacognition without first-order accuracy confounding the picture.

## 6. Baselines and the "calibration ≠ metacognition" ablation

`baselines.py` re-scores each run's own `(confidence, correct)` pairs under trivial policies, using
exactly the same metric code as the model:

* `random_confidence` — uniform noise, `constant_100`, `constant_50`
* `oracle_confidence` — upper bound (`1.0` iff correct); its AUROC2 = 1 by construction
* first-order controls for KB-B/KB-C: `always_abstain`, `never_abstain`, `always_do_it`,
  `always_ask_help`, `chance`, `oracle_policy`

The calibration ablation re-calibrates the model's own confidences with **temperature scaling** and
**isotonic regression (PAVA)** and reports ECE and AUROC2 before/after:

* Temperature scaling is **strictly monotone** ⇒ its AUROC2 change is *exactly* 0. A calibrator can
  therefore buy ECE without buying a single bit of metacognitive discrimination.
* Isotonic regression is monotone but **creates ties**; because the tie-corrected AUROC awards 0.5
  credit to tied pairs, such a map can move AUROC2 slightly in *either* direction. This is an
  artefact of the tie convention, not extra discrimination, so the **raw AUROC2** is the headline
  metric and the isotonic deltas are reported transparently.

That contrast is the empirical form of the argument that *good calibration is not the same thing as
metacognition*, and it is why KnowBound reports both families of metrics.

## 7. Reproducibility, robustness and logging

* **Fixed seed** (`seed: 20261005`) in `configs/default.yaml`; `data/manifest.json` records seed,
  counts, generator configuration, version and timestamp. Regenerating is byte-deterministic.
* **Every model call is written to `logs/transcript_<tag>_<family>_<model>.jsonl`** with the raw
  response text, the parse strategy used, the parsed object, latency and timestamp. `scored_*.jsonl`
  adds the graded fields. Interrupted runs resume from the transcripts and re-issue only missing
  calls; a single failing item never aborts the run.
* **JSON extraction** tries, in order: the raw response as JSON → the first fenced ```json block →
  the first balanced `{...}` span → a regex key/value fallback. Each strategy is recorded, so parse
  brittleness is measurable instead of silent.
* Requests send `"think": false` and a system prompt that forbids all output except one JSON object.

### Measured smoke test (real numbers, `results/smoke_report.md`)

Environment: Ollama 0.35.1, `gemma4:e4b` (7.5B, Q4_K_M), RTX 5060 Laptop 8 GB, i7-14650HX, 24 GB RAM.
3 items per family, 9 items, 12 model calls, single run:

| family | items | ok items | calls | mean call latency (s) | mean latency per item (s) | cold start (s) | JSON parse failures |
| --- | --- | --- | --- | --- | --- | --- | --- |
| kb_a | 3 | 3 | 6 | 3.461 | 6.921 | 16.824 | 0 |
| kb_b | 3 | 3 | 3 | 0.569 | 0.569 | 0.716 | 0 |
| kb_c | 3 | 3 | 3 | 0.603 | 0.603 | 0.737 | 0 |

* **End-to-end chain proven**: generate → prompt → local model → JSON parse → grade → aggregate → report.
* **9/9 items OK, 12/12 calls succeeded, 0 JSON parse failures** (all `strict`), 0 errors.
* Warm call latency **0.678 s** (median regime; the 16.8 s first call is model load), so the planned
  full run of 60 + 40 + 20 items = **180 calls** is estimated at **≈2.3 min** excluding that load.

Bugs found and fixed during the smoke work (kept for the record):

1. The very first smoke attempt failed with
   `ConnectionError … [WinError 10061] 目标计算机积极拒绝` on `127.0.0.1:11434` — the Ollama server was
   not listening (no `ollama` process, port closed). Fix: start the local server
   (`ollama serve` / the Ollama app); `GET /api/version` then returned `{"version":"0.35.1"}` and the
   run above went through. The failed attempt is also why the runner's transcript checkpoint matters:
   its cached `ok=false` records were cleared before re-running so the calls were genuinely retried.
2. The smoke report counted absent `parse_strategy_a` keys as parse failures (6 spurious "failures").
   Fixed to count only keys that exist and are literally `failed`.
3. The report did not separate cold-start latency from warm latency, which made per-call cost look
   5× worse than it is. Fixed: cold start, warm mean, per-item latency and a computed full-run
   estimate are now reported separately.
4. The self-test initially asserted that isotonic regression can never raise AUROC2. Measurement
   showed +0.125 on a deliberately anti-correlated toy signal, which led to the corrected
   understanding documented in section 6 (tie convention), and the assertion now checks the
   documented ±0.5 bound plus exact invariance for temperature scaling.

## 8. Full-run results (two models, real numbers)

**Run conditions.** Date 2026-10-05, tag `full`. Models `gemma4:e4b` (7.5B, Q4_K_M) and
`Librellama/gemma4:e2b-Uncensored` (4.6B, Q4_K_M), served by Ollama 0.35.1 at `127.0.0.1:11434`.
Decoding: seed 20261005, temperature 0, `num_predict` 256, `think:false`, serial calls with a
checkpoint after every call. Items: KB-A 60 (×2 stages = 120 calls), KB-B 40, KB-C 20 →
**180 calls per model, 360 calls total**. Every number below is produced by
`python -m knowbound compare --tag full` from `logs/scored_*.jsonl`; full tables (per-domain,
accuracy-binned, calibration ablation, per-contrast CIs, all baseline policies) are in
`results/summary.md`, machine-readable in `results/metrics.json`.

**Cost actually paid.** `gemma4:e4b`: 180/180 calls OK, 137.1 s of model time, wall span
12:18:03→12:20:12 (≈2.3 min including a 9.2 s model load). `e2b-Uncensored`: 180/180 OK, 76.0 s of
model time, 12:20:21→12:21:29 (≈1.3 min including an 8.5 s load). Combined **360 calls in ≈3.6 min**,
0 errors, 0 empty responses, **0 JSON parse failures (all `strict`)**. Total session time including
generation, manifests, comparison (3.8 s), report rendering and self-tests stayed far below the
40-minute budget.

### 8.1 Headline metrics (95% CI = item-level bootstrap, 2000 resamples)

| family | metric | `gemma4:e4b` | `gemma4:e2b-Uncensored` |
| --- | --- | --- | --- |
| KB-A | accuracy | 0.700 [0.583, 0.817] | 0.650 [0.517, 0.767] |
| KB-A | **AUROC2** | **0.387 [0.281, 0.501]** | **0.441 [0.311, 0.583]** |
| KB-A | ECE-10 | 0.533 [0.408, 0.657] | 0.515 [0.398, 0.644] |
| KB-A | Brier | 0.522 | 0.507 |
| KB-A | ΔE (signed) | +0.056 [−0.130, +0.230] | +0.085 [−0.094, +0.251] |
| KB-A | \|ΔE\| | 0.536 | 0.541 |
| KB-A | pooled accuracy-binned AUROC2 | 0.436 | 0.486 |
| KB-B | accuracy (overall) | 1.000 [1.000, 1.000] | 0.900 [0.800, 0.975] |
| KB-B | accuracy (answerable only) | 1.000 | 1.000 |
| KB-B | **over-claim rate** (unanswerable) | **0.000 [0.000, 0.000]** | **0.200 [0.048, 0.391]** |
| KB-B | abstention AUROC | 0.750 [0.639, 0.857] | 0.800 [0.684, 0.905] |
| KB-B | Balanced Abstention Score | 1.000 [1.000, 1.000] | 0.900 [0.804, 0.976] |
| KB-B | AUROC2 (confidence) | n/a (no variation) | 0.656 [0.415, 0.853] |
| KB-C | net utility | 0.520 [0.305, 0.725] | 0.485 [0.270, 0.685] |
| KB-C | help calls used (budget 6) | 2 | 1 |
| KB-C | ask-help AUROC vs unanswerable | 0.667 [0.500, 0.875] | 0.583 [0.500, 0.750] |
| KB-C | normalised utility | −0.857 | −1.024 |

### 8.2 Baseline family (same items, same metric code)

| policy | e4b KB-A AUROC2 / ECE-10 / Brier | e2b KB-A AUROC2 / ECE-10 / Brier |
| --- | --- | --- |
| random_confidence | 0.426 / 0.386 / 0.396 | 0.466 / 0.370 / 0.380 |
| constant_100 | 0.500 / 0.300 / 0.300 | 0.500 / 0.350 / 0.350 |
| constant_50 | 0.500 / 0.200 / 0.250 | 0.500 / 0.150 / 0.250 |
| oracle_confidence (upper bound) | 1.000 / 0.000 / 0.000 | 1.000 / 0.000 / 0.000 |

* **KB-B controls**: `always_abstain` and `never_abstain` both score BAS = 0.500, versus 1.000
  (e4b) and 0.900 (e2b) for the models — the models' boundary behaviour is **two-sided**, not a
  degenerate always-answer or always-refuse policy.
* **KB-C reference policies**: `always_do_it` = 0.700, `always_ask_help` = 0.660, `random` = 0.680,
  `oracle_policy` (upper bound) = 0.910. Both models score **below `always_do_it`**, and their CIs
  against `always_do_it` span 0 (e4b: −0.180 [−0.515, +0.205]; e2b: −0.215 [−0.565, +0.185]), while
  both beat `always_ask_help` (e4b: +0.310 [+0.095, +0.515]; e2b: +0.275 [+0.075, +0.490]).
  100% of granted help calls went to unanswerable items in both runs.

### 8.3 Calibration ≠ metacognition (empirical form of the argument)

| model | stage | ECE-10 | AUROC2 | Brier |
| --- | --- | --- | --- | --- |
| e4b | raw | 0.5325 | 0.3869 | 0.5218 |
| e4b | + temperature scaling (T = 50) | **0.1689** | **0.3869** (exactly unchanged) | 0.2550 |
| e4b | + isotonic (PAVA) | 0.2660 | 0.4365 | 0.2877 |
| e2b | raw | 0.5152 | 0.4408 | 0.5071 |
| e2b | + temperature scaling (T = 50) | **0.1267** | **0.4408** (exactly unchanged) | 0.2563 |
| e2b | + isotonic (PAVA) | 0.1917 | 0.5183 | 0.2840 |

Post-hoc calibration cuts ECE by 0.36–0.39 while temperature scaling moves AUROC2 by **exactly
zero** — a calibrator buys apparent calibration without buying one bit of metacognitive
discrimination. (Calibrators are fitted and evaluated on the same items, so these ECEs are
optimistic; isotonic shifts are tie-convention artefacts.)

### 8.4 Model-vs-model (paired bootstrap, same items)

| family | separated by (CI excludes 0) | indistinguishable (CI spans 0) |
| --- | --- | --- |
| KB-A | none | accuracy, AUROC2, ECE-10, Brier, ΔE, \|ΔE\| |
| KB-B | overall accuracy (−0.100 [−0.200, −0.025]), Balanced Abstention (−0.100 [−0.195, −0.025]), ΔE (+0.199 [+0.056, +0.376]), over-claim (+0.200 [+0.044, +0.375]) | abstention AUROC, accuracy on answerable items, AUROC2, ECE-10 |
| KB-C | none | utility, help-call rate, ask-help AUROC, all three policy contrasts |

### 8.5 What these numbers do and do not support

**Supported**

1. **Neither model shows above-chance second-order discrimination on KB-A.** AUROC2 = 0.387
   [0.281, 0.501] (e4b) and 0.441 [0.311, 0.583] (e2b): both intervals include or sit below 0.5,
   while `constant_50` scores exactly 0.500 and random confidence 0.426/0.466 on the same items. On
   this item set the stated confidence is not merely uninformative but mildly *anti*-diagnostic.
2. **Calibration error is domain-driven and flips sign**, so a blanket "the model is over-confident"
   claim is false: largest over-confidence in `multihop` (ΔE = +0.850 at accuracy 0.133 for e4b;
   +0.823 at 0.067 for e2b), largest under-confidence in `fictional` (ΔE = −0.953 at accuracy 1.000
   for e4b; −0.860 at 0.933 for e2b). Global ECE hides this.
3. **The boundary behaviour of e4b on KB-B is genuinely two-sided**: over-claim 0.000
   [0.000, 0.000] with answerable accuracy 1.000, BAS 1.000 versus 0.500 for both degenerate
   controls.
4. **The smaller "uncensored" model is measurably worse on KB-B, not on KB-A or KB-C**: e2b
   over-claims on fictional items at 0.200 and is separated on four KB-B metrics, while KB-A and
   KB-C are statistically indistinguishable.
5. **Post-hoc calibration is not metacognition**: temperature scaling moves ECE by 0.36–0.39 and
   AUROC2 by exactly 0.

**Not supported**

1. Any claim that the larger model is *better at metacognition*: KB-A and KB-C show no detectable
   difference, and the KB-B gap is compatible with a pure knowledge/first-order account.
2. Any claim that help-seeking beats simply answering in KB-C: both models' normalised utility is
   negative and the contrast against `always_do_it` spans 0 at n = 20.
3. Any claim about "LLMs" in general, or about other prompts, seeds, quantizations or runtimes.
   CIs are item-level (they account for item sampling only), with n = 60/40/20 per family, one
   generation per item.

## 9. Human baseline

The materials in `human_baseline/` exist so that a human comparison is *reproducible on the same
footing as the models* — but **no human data has been collected, so no human numbers appear anywhere
in this repository**. Nothing here is a placeholder for a measurement.

| File | Role |
| --- | --- |
| `lenovo_human_baseline_protocol.md` | Collection protocol: participant/session rules, per-family task wording, CSV field-by-field specification, same-footing scoring rules (confidence on [0, 100] → [0, 1], same grading, same KB-C budget of 6 at discount 0.7), and the statement of known limitations. |
| `lenovo_human_baseline_template.csv` | **Header-only** template. The scoring script exits with "no human data collected" and writes no metrics file while it is empty — a human baseline is never invented. |
| `lenovo_human_scoring.py` | Scores a filled CSV. It imports `knowbound.grading`, `knowbound.metrics`, `knowbound.baselines` and `knowbound.stats` — the same modules that produced §8 — and only adds CSV IO, per-participant grouping and the presentation-order budget rule. Writes `human_results.json` + `human_results.md`. `--validate-only` checks the header/shape without computing anything. |
| `lenovo_human_baseline_literature.md` | Real, citable human reference values (confidence–accuracy correlation, overprecision in 90% intervals, hit rate at certainty, type-2 AUROC ranges) with sources, explicitly flagged as **literature reference values, not measurements from this machine**. |

The scoring path was verified end-to-end on a **synthetic** CSV (240 rows, 2 pseudo-participants)
written only to the session temp directory: metrics, bootstrap CIs, baselines and the markdown
report all rendered, and no synthetic row was ever written into the delivery tree.

## 10. Known limitations

* **Two models, one run each, one prompt each.** The full run now exists for both models, but no
  prompt-paraphrase, seed-variance or quantization study was performed, so nothing is claimed about
  stability; the smoke slice (3 items/family) remains plumbing evidence only.
* **The KB-A result is a null result, and it is reported as such.** AUROC2 below 0.5 with CIs
  crossing 0.5 does not license a claim of mild anti-diagnosticity in general — only on this item
  set, and the KB-A `multihop` domain (accuracy 0.133 / 0.067) is where most of the signal lives.
* **One KB-A domain hits the ceiling**: `fictional` items are answerable-by-construction as
  "UNKNOWN", so accuracy 1.000 makes AUROC2 undefined there; the KB-B AUROC2 for e4b is `n/a` for the
  same reason (no confidence variation).
* **Human comparison is not empirical yet.** §9 provides protocol, template, same-code scorer and
  literature reference values; there is **no collected human data**, so no model-vs-human difference
  is claimed anywhere in this repository.
* **Self-grading is brittle for free text.** Automatic grading normalises numbers and strings, but
  KB-A `longtail` and KB-B real items can be failed for phrasing reasons; the accepted-answer lists
  are deliberately narrow, which biases accuracy *downwards*.
* **Fiction guarantee is best-effort structural.** Fictional entities are morpheme-built and
  blacklist-checked; a truly exhaustive proof that they appear nowhere in the pretraining corpus is
  impossible. A model could in principle answer one correctly by coincidence (it would then be scored
  as an over-claim).
* **Calibrators are fitted and evaluated on the same items** in the ablation, so the post-hoc ECEs are
  optimistic; the ablation's purpose is the *invariance contrast*, not a headline ECE.
* **KB-C utility is a simplified economics.** One help price (×0.7) and one budget (6) with no
  cost for latency, and no partial credit for "asked for help on an answerable item".
* **Serial execution only.** Parallelism would speed up the full run but was rejected on the
  reference hardware because free RAM dropped to ~2.3 GB during inference.
