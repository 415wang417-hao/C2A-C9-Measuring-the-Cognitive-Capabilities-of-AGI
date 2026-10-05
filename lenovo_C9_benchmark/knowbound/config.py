"""Configuration loading.

``yaml`` is used when available; otherwise a tiny built-in parser understands the
subset of YAML used by ``configs/default.yaml`` (nested maps of scalars only), so
the benchmark runs on a bare Python installation.
"""

from __future__ import annotations

import os
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "seed": 20261005,
    "paths": {"data": "data", "logs": "logs", "results": "results"},
    "generator": {
        "kb_a": {"per_domain": 15},
        "kb_b": {"n_real": 20, "n_fictional": 20},
        "kb_c": {"n_total": 20, "n_fictional": 6, "n_hard": 6,
                 "n_medium": 5, "n_easy": 3},
    },
    "model": {
        "name": "gemma4:e4b",
        "endpoint": "http://127.0.0.1:11434",
        "api": "auto",
        "temperature": 0.0,
        "num_predict": 256,
        "timeout_sec": 180,
        "think": False,
        "seed": 20261005,
    },
    "budget": {"kb_c_help_budget": 6, "kb_c_help_discount": 0.7},
    "smoke": {"per_family": 3},
}


def _mini_yaml(text: str) -> Dict[str, Any]:
    """Parse the restricted YAML subset (nested maps + scalars + inline {})."""
    root: Dict[str, Any] = {}
    stack = [(-1, root)]
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, _, value = line.strip().partition(":")
        value = value.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if value == "" or value == "{}":
            node: Dict[str, Any] = {}
            parent[key] = node
            stack.append((indent, node))
            continue
        parent[key] = _scalar(value)
    return root


def _scalar(value: str):
    v = value.strip().strip('"').strip("'")
    low = v.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("null", "none", "~"):
        return None
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


def _deep_update(base: Dict[str, Any], extra: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in (extra or {}).items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_update(base[k], v)
        else:
            base[k] = v
    return base


def load_config(path: str | None = None) -> Dict[str, Any]:
    cfg = {k: (dict(v) if isinstance(v, dict) else v) for k, v in DEFAULT_CONFIG.items()}
    for k, v in DEFAULT_CONFIG.items():
        if isinstance(v, dict):
            cfg[k] = _deep_update({}, v)
    if path is None or not os.path.exists(path):
        return cfg
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    try:
        import yaml  # type: ignore
        loaded = yaml.safe_load(text) or {}
    except Exception:
        loaded = _mini_yaml(text)
    return _deep_update(cfg, loaded)


def resolve(root: str, rel: str) -> str:
    """Resolve a config-relative path against the project root."""
    return rel if os.path.isabs(rel) else os.path.join(root, rel)
