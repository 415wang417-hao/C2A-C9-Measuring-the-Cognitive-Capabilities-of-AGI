"""pytest wrapper around the offline self-test suite.

Run either way:
    pytest -q tests/
    python -m knowbound selftest
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowbound import selftest as ST  # noqa: E402


def _run(name):
    for check_name, fn in ST.CHECKS:
        if check_name == name:
            return fn()
    raise AssertionError(f"unknown check {name}")


def test_metrics():
    _run("metrics: AUROC / AUROC2 / ECE / Brier / delta_E on hand-computed data")


def test_abstention():
    _run("metrics: over-claim / balanced abstention / abstention AUROC")


def test_extract():
    _run("models: JSON extraction across strict / fenced / prose / broken replies")


def test_grading():
    _run("grading: answerable items need content, unanswerable need an explicit refusal")


def test_generate():
    _run("generate: deterministic, well-shaped, matched KB-B halves, KB-C budget pool")


def test_baselines():
    _run("baselines: oracle is separable, constants are degenerate, AUROC2 is monotone-invariant")


def test_kb_c_policies():
    _run("baselines: KB-C policies are ordered do_it <= model <= oracle")


def test_config():
    _run("config: default.yaml loads and the mini-parser agrees with the shipped file")


def test_report():
    _run("report: aggregation runs on synthetic records and emits JSON-safe numbers")


if __name__ == "__main__":
    raise SystemExit(ST.main())
