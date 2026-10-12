#!/usr/bin/env python3
"""Validate results/*.json against results/schema.json, plus basic consistency checks."""
import json, glob, sys
from jsonschema import Draft202012Validator

schema = json.load(open("results/schema.json"))
v = Draft202012Validator(schema)
tasks = {l.strip() for l in open("tasks.txt") if l.strip() and not l.startswith("#")}
commit = next(l.split("=", 1)[1].strip() for l in open("tasks.txt") if l.startswith("# dataset_commit="))
files = sys.argv[1:] or sorted(f for f in glob.glob("results/*.json") if not f.endswith("schema.json"))
bad = 0
for f in files:
    try:
        d = json.load(open(f))
    except Exception as e:
        print(f"FAIL {f}: not valid JSON ({e})"); bad += 1; continue
    errs = [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in v.iter_errors(d)]
    if not errs:
        if d["dataset_commit"] != commit:
            errs.append(f"dataset_commit {d['dataset_commit']} != pinned {commit}")
        extra = {r["task_id"] for r in d["runs"]} - tasks
        if extra:
            errs.append(f"unknown tasks: {sorted(extra)}")
        if d.get("example") and "EXAMPLE" not in f:
            errs.append("example data must have EXAMPLE in the file name")
        if not d.get("example") and "EXAMPLE" in f:
            errs.append("file named EXAMPLE but example is not true")
    for e in errs:
        print(f"FAIL {f}: {e}")
    bad += bool(errs)
    if not errs:
        print(f"ok   {f}")
sys.exit(1 if bad else 0)
