"""Serial runners: model calls -> grading -> per-item scored records.

The runner is deliberately dumb and auditable:

* one item at a time, never concurrent (8 GB VRAM / tight RAM);
* **every** model call is appended to a JSONL transcript before the next one
  starts, keyed by ``(model, item_id, stage)``; when a run is restarted the
  already-present keys are skipped, which gives crash-safe resume for free;
* a failure on one item (bad JSON, HTTP error, timeout) is recorded and the run
  continues with the next item -- a single broken item can never abort a session.

Outputs two artefacts per (family, model, tag):

* ``logs/transcript_{tag}_{family}_{model}.jsonl``  -- raw calls (with latency
  and the verbatim reply) for post-hoc auditing;
* ``logs/scored_{tag}_{family}_{model}.jsonl``      -- one graded record per item,
  consumed by :mod:`knowbound.report`.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, Iterable, List, Optional

from . import prompts
from .grading import grade_item
from .models import OllamaClient, coerce_bool, coerce_confidence

STAGES = {
    "kb_a": ("P", "A"),
    "kb_b": ("B",),
    "kb_c": ("C",),
}


def slug(model: str) -> str:
    return model.replace("/", "_").replace(":", "-").replace(" ", "")


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def load_done_keys(path: str) -> set:
    done = set()
    if not os.path.exists(path):
        return done
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            done.add((rec.get("model"), rec.get("item_id"), rec.get("stage")))
    return done


def append_jsonl(path: str, record: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def _call(client: OllamaClient, item_id: str, family: str, stage: str,
          messages: List[Dict[str, str]], transcript: str, done: set,
          question: str) -> Dict[str, Any]:
    """One transcript-checkpointed call. Returns the *stored* record."""
    key = (client.model, item_id, stage)
    if key in done:
        return _read_transcript_record(transcript, key)
    res = client.ask_json(messages)
    rec = {
        "model": client.model, "item_id": item_id, "family": family,
        "stage": stage, "question": question,
        "ok": bool(res.get("ok")),
        "latency_sec": res.get("latency_sec"),
        "raw_text": res.get("text") or "",
        "parse_strategy": res.get("parse_strategy"),
        "parsed": res.get("parsed"),
        "error": res.get("error"),
        "ts": _now(),
    }
    append_jsonl(transcript, rec)
    done.add(key)
    return rec


def _read_transcript_record(path: str, key) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if (rec.get("model"), rec.get("item_id"), rec.get("stage")) == key:
                return rec
    return {"ok": False, "parsed": None, "error": "transcript record missing",
            "latency_sec": None, "raw_text": ""}


def _answer_text(rec: Dict[str, Any]) -> str:
    parsed = rec.get("parsed") or {}
    val = parsed.get("answer")
    if val is None:
        return rec.get("raw_text") or ""
    return str(val)


# ---------------------------------------------------------------------------
# per-family runners
# ---------------------------------------------------------------------------

def run_kb_a(client: OllamaClient, items: Iterable[dict], log_dir: str, tag: str):
    transcript = os.path.join(log_dir, f"transcript_{tag}_kb_a_{slug(client.model)}.jsonl")
    scored_path = os.path.join(log_dir, f"scored_{tag}_kb_a_{slug(client.model)}.jsonl")
    done = load_done_keys(transcript)
    out = []
    for it in items:
        q = it["question"]
        rec_p = _call(client, it["id"], "KB-A", "P", prompts.p_stage(q),
                      transcript, done, q)
        rec_a = _call(client, it["id"], "KB-A", "A", prompts.a_stage(q),
                      transcript, done, q)
        conf = coerce_confidence((rec_p.get("parsed") or {}).get("confidence"))
        ans = _answer_text(rec_a)
        g = grade_item(it, ans)
        rec = {
            "item_id": it["id"], "family": "KB-A", "model": client.model,
            "domain": it.get("domain"), "difficulty": it.get("difficulty"),
            "question": q, "answerable": bool(it.get("answerable")),
            "confidence": conf,
            "model_answer": ans,
            "correct": bool(g["correct"]),
            "declared_unknown": bool(g["declared_unknown"]),
            "latency_p_sec": rec_p.get("latency_sec"),
            "latency_a_sec": rec_a.get("latency_sec"),
            "ok": bool(rec_p.get("ok") and rec_a.get("ok")),
            "parse_strategy_p": rec_p.get("parse_strategy"),
            "parse_strategy_a": rec_a.get("parse_strategy"),
            "error": rec_p.get("error") or rec_a.get("error"),
        }
        out.append(rec)
    _write_scored(scored_path, out)
    return out


def run_kb_b(client: OllamaClient, items: Iterable[dict], log_dir: str, tag: str):
    transcript = os.path.join(log_dir, f"transcript_{tag}_kb_b_{slug(client.model)}.jsonl")
    scored_path = os.path.join(log_dir, f"scored_{tag}_kb_b_{slug(client.model)}.jsonl")
    done = load_done_keys(transcript)
    out = []
    for it in items:
        q = it["question"]
        rec = _call(client, it["id"], "KB-B", "B", prompts.b_stage(q),
                    transcript, done, q)
        parsed = rec.get("parsed") or {}
        ans = _answer_text(rec)
        conf = coerce_confidence(parsed.get("confidence"))
        can_answer = coerce_bool(parsed.get("can_answer"))
        if can_answer is None:  # derive from the answer text when the key is absent
            can_answer = not grade_item(it, ans)["declared_unknown"] if ans else None
        g = grade_item(it, ans)
        out.append({
            "item_id": it["id"], "family": "KB-B", "model": client.model,
            "template": it.get("template"), "difficulty": it.get("difficulty"),
            "question": q, "answerable": bool(it.get("answerable")),
            "confidence": conf, "can_answer": can_answer,
            "abstain": (can_answer is False),
            "model_answer": ans, "correct": bool(g["correct"]),
            "declared_unknown": bool(g["declared_unknown"]),
            "latency_sec": rec.get("latency_sec"), "ok": bool(rec.get("ok")),
            "parse_strategy": rec.get("parse_strategy"), "error": rec.get("error"),
        })
    _write_scored(scored_path, out)
    return out


def run_kb_c(client: OllamaClient, items: List[dict], log_dir: str, tag: str,
             budget: int = 6, discount: float = 0.7):
    transcript = os.path.join(log_dir, f"transcript_{tag}_kb_c_{slug(client.model)}.jsonl")
    scored_path = os.path.join(log_dir, f"scored_{tag}_kb_c_{slug(client.model)}.jsonl")
    done = load_done_keys(transcript)
    tokens_left = budget
    out = []
    for it in items:
        q = it["question"]
        rec = _call(client, it["id"], "KB-C", "C", prompts.c_stage(q, tokens_left),
                    transcript, done, q)
        parsed = rec.get("parsed") or {}
        decision = parsed.get("decision")
        if isinstance(decision, str):
            d = decision.strip().lower()
            decision = "ask_help" if "help" in d else ("do_it" if d else None)
        else:
            decision = None
        ans = _answer_text(rec)
        conf = coerce_confidence(parsed.get("confidence"))
        granted = bool(decision == "ask_help" and tokens_left > 0)
        if granted:
            tokens_left -= 1
        if granted:
            # the oracle supplies the ground truth
            correct = True
            ans_for_score = "<oracle>" + ("UNKNOWN" if not it["answerable"] else it["answer"])
            points = discount
        else:
            g = grade_item(it, ans)
            correct = bool(g["correct"])
            ans_for_score = ans
            points = 1.0 if correct else 0.0
        out.append({
            "item_id": it["id"], "family": "KB-C", "model": client.model,
            "kind": it.get("kind"), "difficulty": it.get("difficulty"),
            "question": q, "answerable": bool(it.get("answerable")),
            "decision": decision, "help_granted": granted,
            "confidence": conf, "model_answer": ans,
            "answer_for_score": ans_for_score,
            "correct": correct, "points": points,
            "tokens_left_after": tokens_left,
            "latency_sec": rec.get("latency_sec"), "ok": bool(rec.get("ok")),
            "parse_strategy": rec.get("parse_strategy"), "error": rec.get("error"),
        })
    _write_scored(scored_path, out)
    return out


def _write_scored(path: str, records: List[dict]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------

FAMILY_RUNNERS = {"kb_a": run_kb_a, "kb_b": run_kb_b, "kb_c": run_kb_c}


def load_items(path: str, limit: Optional[int] = None) -> List[dict]:
    items = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items[:limit] if limit else items


def run_all(cfg: dict, project_root: str, data_dir: str, log_dir: str,
            model_name: Optional[str] = None, families: Optional[List[str]] = None,
            limit: Optional[int] = None, tag: str = "run") -> Dict[str, List[dict]]:
    m = cfg["model"]
    client = OllamaClient(
        model=model_name or m["name"], endpoint=m["endpoint"],
        temperature=m.get("temperature", 0.0), num_predict=m.get("num_predict", 256),
        timeout_sec=m.get("timeout_sec", 180), think=bool(m.get("think", False)),
        seed=int(m.get("seed", 0)), api=m.get("api", "auto"))

    os.makedirs(log_dir, exist_ok=True)
    results: Dict[str, List[dict]] = {}
    for fam in (families or ["kb_a", "kb_b", "kb_c"]):
        path = os.path.join(data_dir, f"{fam}.jsonl")
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"missing item file {path}; run `python -m knowbound generate` first")
        items = load_items(path, limit)
        started = time.time()
        recs = FAMILY_RUNNERS[fam](client, items, log_dir, tag)
        results[fam] = recs
        print(f"[{fam}] {len(recs)} items in {time.time() - started:.1f}s "
              f"(model={client.model})", flush=True)
    return results
