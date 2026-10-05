"""KnowBound: a metacognition benchmark (knowledge boundary & pre-answer prediction).

C9 deliverable / Track 2 (Metacognition).  Pure Python, optional dependency:
``requests`` (falls back to ``urllib`` when absent), plus ``numpy`` or ``yaml``
are optional.  Nothing else is required to reproduce the benchmark.
"""

__version__ = "0.1.0"
__all__ = ["generate", "grading", "metrics", "calibrators", "models",
           "baselines", "runner", "report", "config", "prompts"]
