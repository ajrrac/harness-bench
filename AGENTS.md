# AGENTS.md

Instructions for coding agents working in this repo.

## Leaderboard
- URL: https://ajrrac.github.io/harness-bench/
- Built from `results/*.json` on `main` by `.github/workflows/pages.yml` (it runs on every push to `main`).
- To submit: run `python3 scripts/validate_results.py` first (needs `pip install jsonschema`), then open a PR
  that adds only your `results/<label>-<date>.json`. No `jobs/`, logs, or other files.
- After the PR merges, check that the Deploy leaderboard workflow passed and your row appears on the page.
- One-time owner step: GitHub Pages must be enabled in repo Settings → Pages → Source = **GitHub Actions**.
  Agents cannot do this; if deploys fail with "Create Pages site failed", ask the repo owner.

## What this is
A runner for 10 fixed Terminal-Bench 2.0 tasks (`tasks.txt`), pinned to dataset commit
`2fd12b88aafdd04a52c298e3940bcb189f9766d6`, run with Harbor 0.24.0.

## Commands
```bash
bash -n run.sh                                            # syntax check
bash run.sh -a <agent> -m <provider/model> -l <label> --dry-run   # always do this first
bash run.sh -a <agent> -m <provider/model> -l <label>             # real run: 10 tasks x 3 runs
bash run.sh -I <module.path:Class> -m <model> -l <label>          # custom Harbor agent
python3 summarize.py jobs/<job> --label <label> --model <model> --dataset-commit <commit>
python3 summarize.py --compare results/a.json results/b.json
```

## Guardrails
- Do not add, remove, or edit tasks, and do not edit files under `.cache/`. Do not copy task files into this repo.
- Do not change `tasks.txt` or the pinned commit without the maintainer's approval.
- Keep 3 runs per task (`-k 3`) for any result that will be shared.
- Never commit secrets, `.env` files, API keys, `jobs/`, or logs. Only commit `results/*.json`.
- A real run spends model tokens and money. Ask the user before you start one. A dry run is free.
- Do not put anything from a private harness in this repo.

## Results format
`results/<label>-<YYYY-MM-DD>.json`, following `results/schema.json`: metadata (label, model, harness_commit,
dataset_commit, harbor_version, date), one entry per trial (task_id, reward, tokens, cost_usd, wall_sec, error),
and a summary (pass_rate, per_task "k/3", totals).
