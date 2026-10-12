#!/usr/bin/env python3
"""Turn a Harbor job dir into results/<label>-<date>.json, or compare result files.
  python3 summarize.py jobs/<job> --label X --model M --dataset-commit C
  python3 summarize.py --compare results/a.json results/b.json
"""
import argparse, json, glob, os, subprocess, datetime
from collections import defaultdict

BENCH_VERSION = "1.0"

def ts(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None

def collect(job):
    runs = []
    for f in sorted(glob.glob(os.path.join(job, "*", "result.json"))):
        d = json.load(open(f))
        if "task_name" not in d:
            continue
        a = d.get("agent_result") or {}
        v = (d.get("verifier_result") or {}).get("rewards") or {}
        s, e = ts(d.get("started_at")), ts(d.get("finished_at"))
        exc = d.get("exception_info")
        runs.append({
            "task_id": d["task_name"].split("/")[-1], "trial": d.get("trial_name"),
            "reward": v.get("reward", 0.0 if exc else None),
            "error": (exc or {}).get("exception_type") if exc else None,
            "input_tokens": a.get("n_input_tokens"), "cache_tokens": a.get("n_cache_tokens"),
            "output_tokens": a.get("n_output_tokens"), "cost_usd": a.get("cost_usd"),
            "wall_sec": (e - s).total_seconds() if s and e else None})
    return runs

def summarize(runs):
    per = defaultdict(list)
    for r in runs:
        per[r["task_id"]].append(1.0 if (r["reward"] or 0) >= 1.0 else 0.0)
    tot = lambda k: sum(r[k] or 0 for r in runs)
    return {"pass_rate": round(sum(sum(v) for v in per.values()) / max(1, len(runs)), 4),
            "per_task": {t: f"{int(sum(v))}/{len(v)}" for t, v in sorted(per.items())},
            "total_input_tokens": int(tot("input_tokens")), "total_output_tokens": int(tot("output_tokens")),
            "total_cost_usd": round(tot("cost_usd"), 4), "total_wall_sec": round(tot("wall_sec"), 1)}

def compare(files):
    res = [json.load(open(f)) for f in files]
    tasks = sorted({t for r in res for t in r["summary"]["per_task"]})
    w = max(len(t) for t in tasks + ["pass rate"]) + 2
    print("".ljust(w) + "".join(r["label"][:18].ljust(20) for r in res))
    for t in tasks:
        print(t.ljust(w) + "".join(r["summary"]["per_task"].get(t, "-").ljust(20) for r in res))
    for k in ["pass_rate", "total_cost_usd", "total_input_tokens", "total_output_tokens", "total_wall_sec"]:
        print(k.ljust(w) + "".join(str(r["summary"][k]).ljust(20) for r in res))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("job", nargs="?")
    p.add_argument("--label"); p.add_argument("--model"); p.add_argument("--dataset-commit")
    p.add_argument("--harness-commit"); p.add_argument("--compare", nargs="+")
    a = p.parse_args()
    if a.compare:
        return compare(a.compare)
    runs = collect(a.job)
    try:
        hv = subprocess.run(["harbor", "--version"], capture_output=True, text=True).stdout.strip()
    except FileNotFoundError:
        hv = "unknown"
    out = {"bench_version": BENCH_VERSION, "label": a.label, "model": a.model,
           "harness_commit": a.harness_commit, "dataset_commit": a.dataset_commit,
           "harbor_version": hv, "date": datetime.date.today().isoformat(),
           "runs": runs, "summary": summarize(runs)}
    os.makedirs("results", exist_ok=True)
    path = f"results/{a.label}-{out['date']}.json"
    json.dump(out, open(path, "w"), indent=2)
    print(json.dumps(out["summary"], indent=2)); print("wrote", path)

if __name__ == "__main__":
    main()
