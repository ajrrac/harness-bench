#!/usr/bin/env bash
# Run the 10-task hard subset of Terminal-Bench 2.0 against one Harbor agent.
# Usage: ./run.sh -a <harbor-agent> -m <model> [-l label] [-k runs] [-n concurrent] [-I import.path:Class] [-H harness-commit] [--dry-run] [-- extra harbor args]
set -euo pipefail
cd "$(dirname "$0")"

AGENT="" MODEL="" LABEL="" RUNS=3 CONC=1 IMPORT="" HCOMMIT="" DRY=0 EXTRA=()
usage(){ sed -n 2,3p "$0"; exit 1; }
while [[ $# -gt 0 ]]; do
  case "$1" in
    -a) AGENT="$2"; shift 2;;
    -m) MODEL="$2"; shift 2;;
    -l) LABEL="$2"; shift 2;;
    -k) RUNS="$2"; shift 2;;
    -n) CONC="$2"; shift 2;;
    -H) HCOMMIT="$2"; shift 2;;
    -I) IMPORT="$2"; shift 2;;
    --dry-run) DRY=1; shift;;
    --) shift; EXTRA=("$@"); break;;
    -h|--help) usage;;
    *) echo "unknown arg: $1"; usage;;
  esac
done
[[ -n "$AGENT$IMPORT" && -n "$MODEL" ]] || usage
[[ "$RUNS" == 3 ]] || echo "WARNING: official comparisons use 3 runs per task (got $RUNS)." >&2

COMMIT=$(sed -n 's/^# dataset_commit=//p' tasks.txt)
REPO=$(sed -n 's/^# dataset_repo=//p' tasks.txt)
mapfile -t TASKS < <(grep -v '^#' tasks.txt | grep -v '^$')
LABEL="${LABEL:-${AGENT:-custom}-$(echo "$MODEL" | tr '/' '_')}"
JOB="${LABEL}-$(date +%Y%m%d-%H%M%S)"
DS=".cache/terminal-bench-2"

CMD=(harbor run -p "$DS" -o jobs -k "$RUNS" -n "$CONC" -m "$MODEL" --job-name "$JOB")
CMD+=(-a "${IMPORT:-$AGENT}")  # Harbor -a takes a built-in name or module.path:ClassName
for t in "${TASKS[@]}"; do CMD+=(-i "$t"); done
CMD+=("${EXTRA[@]}")

echo "dataset: $REPO @ $COMMIT"
echo "tasks:   ${#TASKS[@]}  runs/task: $RUNS  job: jobs/$JOB"
if [[ $DRY == 1 ]]; then printf '%q ' "${CMD[@]}"; echo; echo "(dry run: nothing executed)"; exit 0; fi

command -v harbor >/dev/null || { echo "harbor not found"; exit 1; }
docker info >/dev/null 2>&1 || { echo "docker not running"; exit 1; }
if [[ ! -d "$DS/.git" ]]; then git clone -q "$REPO" "$DS"; fi
git -C "$DS" fetch -q origin "$COMMIT" 2>/dev/null || true
git -C "$DS" checkout -q "$COMMIT"
[[ -z "$(git -C "$DS" status --porcelain)" ]] || { echo "dataset has local edits; refusing to run"; exit 1; }

"${CMD[@]}"
python3 summarize.py "jobs/$JOB" --label "$LABEL" --agent "${IMPORT:-$AGENT}" --model "$MODEL" --dataset-commit "$COMMIT" ${HCOMMIT:+--harness-commit "$HCOMMIT"}
