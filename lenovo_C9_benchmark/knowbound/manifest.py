"""Provenance manifest for a run: ``logs/run_manifest_{tag}_{slug}.json``.

A benchmark result is only meaningful together with the exact runtime it was
produced on.  For every (tag, model) pair this module records:

* the **model tag** as passed to Ollama, its **digest**, **quantisation level**,
  parameter size and on-disk size (from ``POST /api/show``),
* the Ollama **server version** (from ``GET /api/version``),
* the decoding settings actually used (seed, temperature, num_predict, think),
* the item counts per family plus SHA-256 of the item files, so the scored logs
  can be tied back to an exactly identifiable item set.

Everything is read from the live server; if the server is unreachable the
manifest says so instead of inventing values.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Any, Dict, Optional

from .runner import slug


def _get(endpoint: str, path: str, timeout: float = 10.0) -> Optional[dict]:
    try:
        import requests
        r = requests.get(endpoint.rstrip("/") + path, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as exc:                                  # pragma: no cover
        return {"_error": f"{type(exc).__name__}: {exc}"}


def _post(endpoint: str, path: str, payload: dict, timeout: float = 20.0) -> Optional[dict]:
    try:
        import requests
        r = requests.post(endpoint.rstrip("/") + path, json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as exc:                                  # pragma: no cover
        return {"_error": f"{type(exc).__name__}: {exc}"}


def sha256_file(path: str) -> Optional[str]:
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def ollama_provenance(endpoint: str, model: str) -> Dict[str, Any]:
    ver = _get(endpoint, "/api/version") or {}
    show = _post(endpoint, "/api/show", {"model": model}) or {}
    info = (show.get("model_info") or {}) if isinstance(show, dict) else {}
    details = (show.get("details") or {}) if isinstance(show, dict) else {}
    keep = {k: v for k, v in info.items()
            if any(tok in k for tok in ("parameter_count", "context_length", "embedding_length",
                                        "block_count", "attention.head_count"))}
    return {
        "endpoint": endpoint,
        "ollama_version": ver.get("version"),
        "model": model,
        "digest": (show.get("digest") if isinstance(show, dict) else None),
        "quantization_level": details.get("quantization_level"),
        "parameter_size": details.get("parameter_size"),
        "family": details.get("family"),
        "format": details.get("format"),
        "template_present": bool(show.get("template")) if isinstance(show, dict) else None,
        "model_info_subset": keep,
        "server_probe_ok": not (isinstance(ver, dict) and ver.get("_error")),
        "show_probe_error": (show.get("_error") if isinstance(show, dict) else None),
    }


def build(log_dir: str, tag: str, cfg: dict, model: str, item_dir: str,
          families=("kb_a", "kb_b", "kb_c"), extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    m = cfg.get("model", {})
    endpoint = m.get("endpoint", "http://127.0.0.1:11434")
    s = slug(model)
    counts: Dict[str, int] = {}
    transcripts: Dict[str, Any] = {}
    for fam in families:
        tpath = os.path.join(log_dir, f"transcript_{tag}_{fam}_{s}.jsonl")
        spath = os.path.join(log_dir, f"scored_{tag}_{fam}_{s}.jsonl")
        n = 0
        if os.path.exists(spath):
            with open(spath, "r", encoding="utf-8") as fh:
                n = sum(1 for line in fh if line.strip())
        counts[fam] = n
        calls = 0
        if os.path.exists(tpath):
            with open(tpath, "r", encoding="utf-8") as fh:
                calls = sum(1 for line in fh if line.strip())
        transcripts[fam] = {"transcript": os.path.basename(tpath) if os.path.exists(tpath) else None,
                            "scored": os.path.basename(spath) if os.path.exists(spath) else None,
                            "calls": calls, "items": n}
    items = {}
    for fam in families:
        p = os.path.join(item_dir, f"{fam}.jsonl")
        items[fam] = {"file": p if os.path.exists(p) else None, "sha256": sha256_file(p)}
    payload = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "tag": tag,
        "items_per_family": counts,
        "item_files": items,
        "logs": transcripts,
        "decoding": {"seed": m.get("seed"), "temperature": m.get("temperature"),
                     "num_predict": m.get("num_predict"), "think": m.get("think"),
                     "timeout_sec": m.get("timeout_sec"), "api": m.get("api", "auto")},
        "runtime": ollama_provenance(endpoint, model),
    }
    if extra:
        payload.update(extra)
    os.makedirs(log_dir, exist_ok=True)
    path = os.path.join(log_dir, f"run_manifest_{tag}_{s}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    payload["_path"] = path
    return payload
