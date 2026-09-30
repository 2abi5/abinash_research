#!/usr/bin/env python3
"""Inventory a research codebase so the paper can be grounded in real artifacts.

Finds configs, result files, logged metrics, seeds, datasets, loss terms,
optimizer settings, entry points, environment pins, and git provenance -- then
prints the reconciliation questions that must be answered before drafting.

The scan establishes what the artifacts support. It cannot tell you what the
contribution is; that comes from the author (references/01-intake.md). Where the
author's account and the artifacts disagree, report it -- never paper over it.

Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

CODE_EXT = {".py", ".ipynb", ".sh", ".yaml", ".yml", ".json", ".toml", ".cfg", ".ini",
            ".jl", ".R", ".m", ".cpp", ".cu", ".lua"}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "env", ".mypy_cache",
             ".pytest_cache", "build", "dist", ".ipynb_checkpoints", "wandb", ".idea",
             "site-packages", ".tox", ".cache"}
RESULT_EXT = {".json", ".csv", ".tsv", ".jsonl", ".npz", ".pkl", ".parquet"}
RESULT_DIRS = ("results", "result", "outputs", "output", "logs", "runs", "artifacts",
               "checkpoints", "eval", "metrics")
CONFIG_DIRS = ("configs", "config", "conf", "hparams", "experiments")
MAX_BYTES = 400_000
MAX_FILES = 4000

PAT = {
    "seed": re.compile(r"\b(?:seed|random_state)\s*[=:]\s*(\d+)|manual_seed\(\s*(\w+)|"
                       r"np\.random\.seed\(\s*(\w+)|set_seed\(\s*(\w+)"),
    "lr": re.compile(r"\b(?:lr|learning_rate)\s*[=:]\s*([0-9.eE\-]+)"),
    "batch": re.compile(r"\b(?:batch_size|bs|per_device_train_batch_size)\s*[=:]\s*(\d+)"),
    "epochs": re.compile(r"\b(?:epochs|num_epochs|max_epochs|num_train_epochs)\s*[=:]\s*(\d+)"),
    "steps": re.compile(r"\b(?:max_steps|total_steps|num_steps|train_steps)\s*[=:]\s*(\d+)"),
    "optim": re.compile(r"\b(?:optim\.|optimizer\s*[=:]\s*[\"']?)(Adam|AdamW|SGD|RMSprop|"
                        r"Adagrad|Adadelta|LAMB|Lion|Adafactor)\b", re.I),
    "wd": re.compile(r"\b(?:weight_decay|wd)\s*[=:]\s*([0-9.eE\-]+)"),
    "loss_weight": re.compile(r"\b(?:lambda|alpha|beta|gamma|w_|weight_)(\w*)\s*[=:]\s*"
                              r"([0-9.]+)"),
    "loss_term": re.compile(r"\b(\w*loss\w*)\s*=\s*([^\n#]{0,90})", re.I),
    "metric_log": re.compile(r"(?:log|log_metrics|add_scalar|wandb\.log|print)\s*\(\s*"
                             r"[\"']([A-Za-z_][A-Za-z0-9_/ ]{1,40})[\"']"),
    "metric_dict": re.compile(r"[\"'](acc|accuracy|top1|top-1|top5|f1|auc|auroc|mse|rmse|mae|"
                              r"bleu|rouge|psnr|ssim|lpips|fid|miou|iou|map|mAP|em|exact_match|"
                              r"perplexity|ppl|wer|cer|dice|precision|recall|ndcg|mrr)"
                              r"[\"']\s*[:=]", re.I),
    "dataset": re.compile(r"(?:torchvision\.datasets\.(\w+)|load_dataset\(\s*[\"']([\w/\-.]+)"
                          r"|datasets\.load_dataset\(\s*[\"']([\w/\-.]+)"
                          r"|ImageFolder|CIFAR10|CIFAR100|ImageNet|MNIST|COCO|ADE20K|"
                          r"SQuAD|GLUE|WikiText|Cityscapes|KITTI|LibriSpeech)"),
    "amp": re.compile(r"\b(?:amp|autocast|fp16|bf16|mixed_precision|torch\.compile)\b"),
}

ENV_FILES = ("requirements.txt", "environment.yml", "environment.yaml", "pyproject.toml",
             "Pipfile", "poetry.lock", "uv.lock", "conda.yaml", "setup.py", "renv.lock")
ENTRY_HINTS = ("train", "main", "run", "eval", "evaluate", "test", "experiment",
               "finetune", "pretrain", "reproduce", "benchmark")


def walk(root: str) -> list[str]:
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(p) > MAX_BYTES and os.path.splitext(fn)[1] in CODE_EXT:
                    continue
            except OSError:
                continue
            out.append(p)
            if len(out) >= MAX_FILES:
                return out
    return out


def read(p: str) -> str:
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            return fh.read(MAX_BYTES)
    except OSError:
        return ""


def git_info(root: str) -> dict:
    def run(*a):
        try:
            r = subprocess.run(["git", "-C", root, *a], capture_output=True,
                               text=True, timeout=20)
            return r.stdout.strip() if r.returncode == 0 else ""
        except Exception:
            return ""
    if not run("rev-parse", "--is-inside-work-tree"):
        return {}
    return {
        "head": run("rev-parse", "--short", "HEAD"),
        "branch": run("rev-parse", "--abbrev-ref", "HEAD"),
        "last_commit": run("log", "-1", "--format=%ci %s"),
        "commits": run("rev-list", "--count", "HEAD"),
        "tags": [t for t in run("tag", "--sort=-creatordate").split("\n") if t][:8],
        "dirty": bool(run("status", "--porcelain")),
        "first_commit": run("log", "--reverse", "--format=%ci", "--max-count=1"),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".", help="repository root")
    ap.add_argument("--out", help="write provenance JSON here")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    files = walk(root)
    rel = lambda p: os.path.relpath(p, root)

    configs, results, entries, envs, docs = [], [], [], [], []
    hp: dict[str, set] = {k: set() for k in
                          ("seed", "lr", "batch", "epochs", "steps", "optim", "wd")}
    metrics, datasets, loss_terms, loss_weights = set(), set(), set(), set()
    amp_hits = 0

    for p in files:
        r, ext = rel(p), os.path.splitext(p)[1].lower()
        low = r.lower()
        base = os.path.basename(low)

        if base in ENV_FILES:
            envs.append(r)
        if base in ("readme.md", "readme.rst", "readme.txt", "notes.md", "changelog.md"):
            docs.append(r)
        if ext in RESULT_EXT and any(f"{d}/" in low or low.startswith(f"{d}/")
                                     for d in RESULT_DIRS):
            try:
                results.append({"path": r, "bytes": os.path.getsize(p)})
            except OSError:
                pass
        if ext in (".yaml", ".yml", ".json", ".toml", ".ini", ".cfg") and (
                any(f"{d}/" in low or low.startswith(f"{d}/") for d in CONFIG_DIRS)
                or "config" in base or "hparam" in base):
            configs.append(r)
        if ext in (".py", ".sh") and any(h in base for h in ENTRY_HINTS):
            entries.append(r)

        if ext not in CODE_EXT:
            continue
        txt = read(p)
        if not txt:
            continue
        for key, pat in PAT.items():
            for m in pat.finditer(txt):
                groups = [g for g in m.groups() if g] or [m.group(0)]
                val = groups[0]
                if key in hp:
                    hp[key].add(str(val)[:24])
                elif key == "metric_log" or key == "metric_dict":
                    v = str(val).strip().lower()
                    if 2 <= len(v) <= 40 and not v.startswith(("epoch", "step", "time", "lr")):
                        metrics.add(v)
                elif key == "dataset":
                    datasets.add(str(val)[:40])
                elif key == "loss_term":
                    nm = str(val).lower()
                    if nm not in ("loss", "losses"):
                        loss_terms.add(nm[:40])
                elif key == "loss_weight":
                    loss_weights.add(f"{m.group(0).strip()[:40]}")
                elif key == "amp":
                    amp_hits += 1

    prov = {
        "root": root,
        "files_scanned": len(files),
        "git": git_info(root),
        "environment_files": envs,
        "entry_points": sorted(entries)[:25],
        "configs": sorted(configs)[:60],
        "result_files": sorted(results, key=lambda d: d["path"])[:60],
        "hyperparameters": {k: sorted(v)[:12] for k, v in hp.items() if v},
        "metrics_logged": sorted(metrics)[:30],
        "datasets_referenced": sorted(datasets)[:20],
        "loss_terms": sorted(loss_terms)[:20],
        "loss_weight_assignments": sorted(loss_weights)[:20],
        "mixed_precision_mentions": amp_hits,
        "docs": docs,
    }

    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(prov, fh, indent=2)
        print(f"provenance written to {args.out}\n")

    g = prov["git"]
    print(f"# Repository scan — {root}\n")
    print(f"  {len(files)} files scanned")
    if g.get("head"):
        print(f"  git: {g.get('branch','?')} @ {g.get('head','?')} "
              f"({g.get('commits','?')} commits{', DIRTY' if g.get('dirty') else ''})")
        print(f"  last commit: {g.get('last_commit','')}")
        if g.get("tags"):
            print(f"  tags: {', '.join(g['tags'])}")
    elif g:
        print("  git: repository present but no commits yet")
    else:
        print("  git: not a git repository — no provenance for any reported number")
    print()

    def section(title, items, empty_msg, fmt=str, limit=12):
        print(f"## {title}")
        if not items:
            print(f"  (none) — {empty_msg}")
        else:
            for it in list(items)[:limit]:
                print(f"  - {fmt(it)}")
            if len(items) > limit:
                print(f"  ... and {len(items) - limit} more")
        print()

    section("Entry points", prov["entry_points"],
            "no train/eval script found; reproduction commands cannot be documented")
    section("Configs", prov["configs"],
            "NO CONFIGS. Every hyperparameter in the paper will be unverifiable")
    section("Result files", prov["result_files"],
            "NO SAVED RESULTS. Every table cell would be hand-typed and untraceable",
            fmt=lambda d: f"{d['path']}  ({d['bytes']/1024:.0f} KB)")
    section("Metrics logged in code", prov["metrics_logged"],
            "no metric names found; check what the paper reports against what is computed",
            limit=20)
    section("Datasets referenced", prov["datasets_referenced"],
            "no dataset loader found")
    section("Loss terms", prov["loss_terms"], "no named loss terms found")
    section("Loss-weight assignments", prov["loss_weight_assignments"],
            "no loss weights found — these are the most commonly omitted detail in ML papers")
    print("## Hyperparameters found in code/configs")
    if prov["hyperparameters"]:
        for k, v in prov["hyperparameters"].items():
            print(f"  {k:8} {', '.join(v)}")
    else:
        print("  (none found)")
    print()
    section("Environment pins", prov["environment_files"],
            "no requirements/lockfile — the artifact will not be reproducible")

    print("## Reconcile before drafting\n")
    print("Answer each of these WITH the author. Report every mismatch; never paper over one.\n")
    qs = [
        "Does every number the paper will report come from a file in the result list above?",
        "Does every metric the paper reports appear in 'metrics logged'? If not, where did it come from?",
        "Does every config above correspond to a reported row — and every reported row to a config?",
        "Are there result files the paper does NOT report? Why not?",
        "Do the hyperparameters above match what the paper states, exactly?",
        "Is every loss term's weight stated in the paper?",
        "Is each baseline either implemented here, or cited with a published number?",
        "Does every ablation described in the paper have a config? If not, it was not run.",
        "Does the dataset loader apply preprocessing the paper does not mention?",
        "Are seeds set? If the paper reports variance, where does the variance come from?",
        "Which commit produced the reported numbers? Tag it.",
    ]
    for i, q in enumerate(qs, 1):
        print(f"  {i:>2}. {q}")

    if not prov["result_files"]:
        print("\n  BLOCKING: no saved results were found. Code that can run an experiment is")
        print("  not a result. The first deliverable is a script that regenerates the paper's")
        print("  numbers into results/ — without it, every number is unverifiable, including")
        print("  to the author.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
