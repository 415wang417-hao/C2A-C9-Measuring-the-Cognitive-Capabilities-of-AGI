"""Command line entry point:  ``python -m knowbound <command>``

Commands
--------
generate   write data/kb_a.jsonl, data/kb_b.jsonl, data/kb_c.jsonl (+ manifest)
run        full (or partial) evaluation of a model against the item files
smoke      end-to-end smoke test: N items per family, writes results/smoke_report.md
report     recompute results/metrics.json + results/summary.md from the logs
compare    multi-model aggregation -> results/metrics.json + results/summary.md
           (per-model metrics + bootstrap CIs + paired model-vs-model intervals)
manifest   write logs/run_manifest_{tag}_{slug}.json (model digest, quantisation,
           Ollama version, seed, item-file hashes) for provenance
selftest   run the offline assertion suite (no model, no network)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

from . import __version__, compare as CMP, config as C, manifest as MNF
from . import report as R, runner as RUN
from .generate import generate_all

PKG_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.dirname(PKG_DIR)


def _root(args) -> str:
    return os.path.abspath(args.project_root or DEFAULT_ROOT)


def _dump_jsonl(path: str, items) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")


def cmd_generate(args, cfg, root) -> int:
    data_dir = C.resolve(root, cfg["paths"]["data"])
    seed = int(cfg["seed"])
    fam = generate_all(seed, cfg["generator"])
    counts = {}
    for name, items in fam.items():
        _dump_jsonl(os.path.join(data_dir, f"{name}.jsonl"), items)
        counts[name] = len(items)
    manifest = {"seed": seed, "counts": counts, "version": __version__,
                "generator": cfg["generator"], "timestamp": _now()}
    with open(os.path.join(data_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    print(f"generated {counts} -> {data_dir}")
    return 0


def _now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _do_run(args, cfg, root, tag: str, limit, families) -> int:
    data_dir = C.resolve(root, cfg["paths"]["data"])
    log_dir = C.resolve(root, cfg["paths"]["logs"])
    out_dir = C.resolve(root, cfg["paths"]["results"])
    model = args.model or cfg["model"]["name"]
    started = time.time()
    records = RUN.run_all(cfg, root, data_dir, log_dir, model_name=model,
                          families=families, limit=limit, tag=tag)
    elapsed = time.time() - started
    try:                       # provenance is best-effort, never blocks a run
        MNF.build(log_dir, tag, cfg, model, data_dir,
                  families=tuple(records.keys()) or ("kb_a", "kb_b", "kb_c"),
                  extra={"elapsed_sec": round(elapsed, 1),
                         "counts": {k: len(v) for k, v in records.items()}})
    except Exception as exc:
        print(f"[manifest] skipped: {type(exc).__name__}: {exc}")
    metrics = R.compute_all(records, seed=int(cfg["seed"]))
    counts = {k: len(v) for k, v in records.items()}
    meta = {"model": model, "tag": tag, "counts": counts,
            "timestamp": _now(), "elapsed_sec": round(elapsed, 1)}
    stem = f"{tag}_{RUN.slug(model)}" if tag != "smoke" else tag
    R.write_outputs(out_dir, metrics, "", metrics_name=f"metrics_{stem}.json")
    summary = R.render_summary(metrics, meta)
    with open(os.path.join(out_dir, f"summary_{stem}.md"), "w", encoding="utf-8") as fh:
        fh.write(summary)
    if tag == "smoke":
        sizing = dict(cfg)
        sizing.update({"timestamp": meta["timestamp"], "counts": counts})
        with open(os.path.join(out_dir, "smoke_report.md"), "w", encoding="utf-8") as fh:
            fh.write(R.render_smoke(records, sizing, model))
    print(f"[{tag}] {counts} in {elapsed:.1f}s -> {out_dir}")
    return 0


def cmd_run(args, cfg, root) -> int:
    fams = None if not args.families or args.families == "all" else args.families.split(",")
    return _do_run(args, cfg, root, args.tag or "full", args.limit, fams)


def cmd_smoke(args, cfg, root) -> int:
    n = int(args.limit or cfg["smoke"]["per_family"])
    fams = None if not args.families or args.families == "all" else args.families.split(",")
    return _do_run(args, cfg, root, "smoke", n, fams)


def cmd_report(args, cfg, root) -> int:
    log_dir = C.resolve(root, cfg["paths"]["logs"])
    out_dir = C.resolve(root, cfg["paths"]["results"])
    tag = args.tag or "full"
    model = args.model or cfg["model"]["name"]
    records = R.collect(log_dir, tag, model)
    metrics = R.compute_all(records, seed=int(cfg["seed"]))
    counts = {k: len(v) for k, v in records.items()}
    meta = {"model": model, "tag": tag, "counts": counts, "timestamp": _now()}
    stem = f"{tag}_{RUN.slug(model)}" if tag != "smoke" else tag
    R.write_outputs(out_dir, metrics, "", metrics_name=f"metrics_{stem}.json")
    with open(os.path.join(out_dir, f"summary_{stem}.md"), "w", encoding="utf-8") as fh:
        fh.write(R.render_summary(metrics, meta))
    if tag == "smoke":
        sizing = dict(cfg)
        sizing.update({"timestamp": meta["timestamp"], "counts": counts})
        with open(os.path.join(out_dir, "smoke_report.md"), "w", encoding="utf-8") as fh:
            fh.write(R.render_smoke(records, sizing, model))
    print(f"report rebuilt from {log_dir} ({counts})")
    return 0


def cmd_compare(args, cfg, root) -> int:
    log_dir = C.resolve(root, cfg["paths"]["logs"])
    out_dir = C.resolve(root, cfg["paths"]["results"])
    tag = args.tag or "full"
    models = [m.strip() for m in args.models.split(",")] if getattr(args, "models", None) else None
    payload = CMP.build(log_dir, tag=tag, n_boot=int(getattr(args, "n_boot", 2000) or 2000),
                        seed=int(cfg["seed"]), models=models)
    paths = CMP.write(payload, out_dir, tag=tag)
    print(f"compare[{tag}] models={list(payload['models'])} -> {paths['metrics']}, {paths['summary']}")
    return 0


def cmd_manifest(args, cfg, root) -> int:
    log_dir = C.resolve(root, cfg["paths"]["logs"])
    data_dir = C.resolve(root, cfg["paths"]["data"])
    tag = args.tag or "full"
    models = ([m.strip() for m in args.models.split(",")] if getattr(args, "models", None)
              else [cfg["model"]["name"]])
    written = []
    for model in models:
        p = MNF.build(log_dir, tag, cfg, model, data_dir)
        written.append(p["_path"])
        print(f"manifest[{tag}] {model} -> {p['_path']} "
              f"(ollama {p['runtime'].get('ollama_version')}, "
              f"quant {p['runtime'].get('quantization_level')}, "
              f"items {p['items_per_family']})")
    return 0


def cmd_selftest(args, cfg, root) -> int:
    from .selftest import main as selftest_main
    return selftest_main(root)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="knowbound", description="KnowBound benchmark (C9/Track 2)")
    p.add_argument("command", choices=["generate", "run", "smoke", "report", "compare",
                                       "manifest", "selftest"])
    p.add_argument("--config", default=None, help="path to a yaml/json config")
    p.add_argument("--project-root", default=None,
                   help="project root; defaults to the parent of the knowbound package")
    p.add_argument("--model", default=None)
    p.add_argument("--models", default=None, help="comma separated model list (compare/manifest)")
    p.add_argument("--n-boot", dest="n_boot", type=int, default=None,
                   help="bootstrap resamples for `compare` (default 2000)")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--families", default=None, help="comma separated, e.g. kb_a,kb_b")
    p.add_argument("--tag", default=None)
    p.add_argument("--version", action="version", version=f"knowbound {__version__}")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    root = _root(args)
    cfg_path = args.config or os.path.join(root, "configs", "default.yaml")
    cfg = C.load_config(cfg_path)
    table = {"generate": cmd_generate, "run": cmd_run, "smoke": cmd_smoke,
             "report": cmd_report, "compare": cmd_compare, "manifest": cmd_manifest,
             "selftest": cmd_selftest}
    return table[args.command](args, cfg, root)


if __name__ == "__main__":
    sys.exit(main())
