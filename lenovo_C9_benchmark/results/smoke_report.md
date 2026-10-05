# KnowBound -- smoke test report

Purpose: prove the full chain `generate -> prompt -> local model -> JSON parse -> grade -> aggregate` works end to end on a small slice, and measure the per-call latency needed to size the full run.

| field | value |
| --- | --- |
| model | `gemma4:e4b` |
| items (per family) | {'kb_a': 3, 'kb_b': 3, 'kb_c': 3} |
| total items | 9 |
| generated | 2026-10-05 12:08:56 |

## per family

| family | items | ok items | raw calls | mean call latency (s) | mean latency per item (s) | first-call (cold) latency (s) | JSON parse failures |
| --- | --- | --- | --- | --- | --- | --- | --- |
| kb_a | 3 | 3 | 6 | 3.461 | 6.921 | 16.824 | 0 |
| kb_b | 3 | 3 | 3 | 0.569 | 0.569 | 0.716 | 0 |
| kb_c | 3 | 3 | 3 | 0.603 | 0.603 | 0.737 | 0 |

## per item

| item | family | latency sum (s) | ok | parse | correct | confidence | model answer |
| --- | --- | --- | --- | --- | --- | --- | --- |
| KB-A-0000 | kb_a | 17.402 | yes | strict|strict | yes | 1.00 | -54 |
| KB-A-0001 | kb_a | 1.675 | yes | strict|strict | yes | 1.00 | x^2+15x+54 |
| KB-A-0002 | kb_a | 1.687 | yes | strict|strict | no | 1.00 | 2496 |
| KB-B-0000 | kb_b | 0.716 | yes | strict | yes | 1.00 | UNKNOWN |
| KB-B-0001 | kb_b | 0.501 | yes | strict | yes | 1.00 | 74 |
| KB-B-0002 | kb_b | 0.489 | yes | strict | yes | 0.00 | UNKNOWN |
| KB-C-0000 | kb_c | 0.737 | yes | strict | no | 1.00 | 1007 |
| KB-C-0001 | kb_c | 0.558 | yes | strict | no | 1.00 | 104 |
| KB-C-0002 | kb_c | 0.514 | yes | strict | yes | 0.00 | UNKNOWN |

## errors

- none

## sizing implication for the full run

- planned items: {'kb_a': 60, 'kb_b': 40, 'kb_c': 20} (KB-A is two-stage, so 60x2 calls)
- planned model calls: 180
- measured warm call latency: 0.678 s (cold start 16.824 s, excluded)
- estimated full-run wall clock: 2.3 min (180 calls + one model load)

