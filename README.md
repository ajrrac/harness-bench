# harness-bench

A small, fixed benchmark for comparing coding-agent harnesses. It runs the 10 hardest tasks from
[Terminal-Bench 2.0](https://github.com/harbor-framework/terminal-bench-2), 3 times each, with
[Harbor](https://github.com/harbor-framework/harbor). Everyone runs the same tasks at the same pinned
commit, so results are comparable.

No tasks are written or changed here. All tasks belong to the Terminal-Bench authors and are fetched at run time.

## The tasks
All 10 are marked `hard` by the Terminal-Bench authors. They are the hard tasks with the longest
expert time estimates in `task.toml`. `gpt2-codegolf` was left out because it needs 8 GB of RAM.
The list and pinned commit are in [`tasks.txt`](tasks.txt).

| Task | Expert estimate | RAM |
|---|---|---|
| fix-ocaml-gc | 24 h | 2 GB |
| regex-chess | 24 h | 2 GB |
| write-compressor | 24 h | 2 GB |
| circuit-fibsqrt | 16 h | 2 GB |
| feal-linear-cryptanalysis | 16 h | 2 GB |
| sparql-university | ~13 h | 2 GB |
| sam-cell-seg | 10 h | 4 GB |
| make-doom-for-mips | 8 h | 2 GB |
| make-mips-interpreter | 8 h | 2 GB |
| feal-differential-cryptanalysis | 8 h | 2 GB |

## Prerequisites
- Docker, running (at least 4 CPUs and 6 GB RAM free).
- Harbor 0.24.0: `uv tool install harbor==0.24.0` (or `pip install harbor==0.24.0`).
- Python 3.10+, git, bash.
- API keys or a CLI login for whatever model your harness uses, set in your shell. Never in this repo.

## Run it
```bash
git clone https://github.com/ajrrac/harness-bench && cd harness-bench
bash run.sh -a claude-code -m anthropic/claude-opus-4-1 --dry-run   # print the command, run nothing
bash run.sh -a claude-code -m anthropic/claude-opus-4-1 -l my-label
```
Options: `-a` Harbor agent name, `-I module.path:Class` a custom agent, `-m` model, `-l` label for results,
`-k` runs per task (keep 3), `-n` concurrency (default 1), `--` extra args passed to `harbor run`.

The first run clones Terminal-Bench 2.0 into `.cache/` and checks out the pinned commit. It refuses to run if those files were edited.
A full run is 30 trials and can take many hours and cost real money.

## Add your own harness
Write a Harbor agent: a Python class that extends Harbor's `BaseInstalledAgent` (or `BaseAgent`). Harbor's
built-in agents (`claude-code`, `codex`, and others) are good examples. Make it importable (`pip install -e .`
or put it on `PYTHONPATH`), then:
```bash
bash run.sh -I my_harness.agent:MyHarnessAgent -m <model> -l my-harness --dry-run
bash run.sh -I my_harness.agent:MyHarnessAgent -m <model> -l my-harness -H $(git -C ../my-harness rev-parse --short HEAD)
```
(`-H` records your harness commit in the results.)

## Compare results
Each run writes `results/<label>-<date>.json` (schema: [`results/schema.json`](results/schema.json)):
pass rate, per-task passes out of 3, tokens, cost, and wall time. To compare:
```bash
python3 summarize.py --compare results/harness-a-*.json results/harness-b-*.json
```
Open a PR with your result JSON to share it. Only commit the JSON, never `jobs/` (logs can contain secrets).

## Caveats
- **Contamination.** These tasks are public and can end up in model training data. Scores lose meaning over time.
  Always report the date, model, and dataset commit, and compare runs from around the same time.
- **Variance.** Hard tasks pass or fail somewhat at random. That is why each task runs 3 times.
- Same model + different harness is the fair comparison. Different models measure the model too.

## Credit and license
All tasks are from Terminal-Bench 2.0 by the Terminal-Bench authors and contributors
(harbor-framework/terminal-bench-2, Apache 2.0). Please cite their work. This repo is Apache 2.0; see `LICENSE`
and `NOTICE`. Some tasks fetch third-party code with its own license (for example, make-doom-for-mips builds Doom).
