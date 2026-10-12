#!/usr/bin/env python3
"""Combine results/*.json into _site/data.json and _site/index.html (data inlined)."""
import json, glob, os
os.makedirs("_site", exist_ok=True)
tasks = [l.strip() for l in open("tasks.txt") if l.strip() and not l.startswith("#")]
commit = next(l.split("=", 1)[1].strip() for l in open("tasks.txt") if l.startswith("# dataset_commit="))
entries = []
for f in sorted(glob.glob("results/*.json")):
    if f.endswith("schema.json"):
        continue
    d = json.load(open(f)); s = d["summary"]
    entries.append({"file": os.path.basename(f), "example": bool(d.get("example")), "label": d["label"],
        "agent": d.get("agent"), "model": d["model"], "harness_commit": d.get("harness_commit"),
        "date": d.get("date"), "harbor_version": d.get("harbor_version"), "pass_rate": s["pass_rate"],
        "per_task": s["per_task"], "cost": s.get("total_cost_usd"), "tokens_in": s.get("total_input_tokens"),
        "tokens_out": s.get("total_output_tokens"), "wall_sec": s.get("total_wall_sec")})
entries.sort(key=lambda e: (-e["pass_rate"], e["cost"] or 0))
data = {"tasks": tasks, "dataset_commit": commit, "entries": entries}
json.dump(data, open("_site/data.json", "w"), indent=1)
html = open("site/index.html").read().replace("/*__DATA__*/null", json.dumps(data).replace("</", "<\\/"))
open("_site/index.html", "w").write(html)
print(f"built _site with {len(entries)} entries")
