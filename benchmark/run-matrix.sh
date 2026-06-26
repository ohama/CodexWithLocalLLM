#!/usr/bin/env bash
# Full benchmark matrix driver (REP-01 / REP-03).
#   benchmark/run-matrix.sh
#
# Runs ALL six cells — (codex, openhands) x (l1, l2, l3) — strictly SERIALLY by
# calling the existing single-cell runner `benchmark/run.sh` once per cell, then
# aggregates the six per-run meta.json records into one results.json.
#
# CRITICAL (single mlx backend): this driver must NOT acquire `.runs/.lock`.
# run.sh acquires and releases that mkdir-mutex itself, per cell. If the driver
# held it, EVERY run.sh call would abort with exit 3 (lock held). The driver's
# only job is to invoke run.sh one cell at a time and wait for each to finish
# before starting the next — no `&`, no concurrency.
#
# A single cell failing (nonzero agent exit or a failed judge) is a VALID
# recorded result (passed=false); the sweep records it and continues — it never
# aborts the whole matrix.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

TOOLS=(codex openhands)
LEVELS=(l1 l2 l3 l4 l5 l6 l7)  # fib/wordstat/kvstore/calc/todo/csvstat/kvapi

# One timestamped collection dir per sweep so re-runs never clobber prior ones.
TS="$(date -u +%Y%m%d-%H%M%S)"
MATRIX_DIR="$HERE/.runs/matrix-$TS"
mkdir -p "$MATRIX_DIR"
MANIFEST="$MATRIX_DIR/manifest.txt"
: > "$MANIFEST"

echo "════════ benchmark matrix sweep ════════"
echo "matrix dir : $MATRIX_DIR"
echo "cells      : ${#TOOLS[@]} tools x ${#LEVELS[@]} levels = $(( ${#TOOLS[@]} * ${#LEVELS[@]} )) (serial)"
echo "────────────────────────────────────────"

N=0
TOTAL=$(( ${#TOOLS[@]} * ${#LEVELS[@]} ))
# tool-major: codex l1,l2,l3 then openhands l1,l2,l3 — one backend at a time.
for tool in "${TOOLS[@]}"; do
  for level in "${LEVELS[@]}"; do
    N=$(( N + 1 ))
    echo
    echo ">>> [$N/$TOTAL] $tool $level — starting ($(date -u +%H:%M:%SZ))"

    # Never abort the sweep on a single cell's failure: capture run.sh's REAL
    # exit via PIPESTATUS (tee would otherwise mask it), then keep going.
    set +e
    bash "$HERE/run.sh" "$tool" "$level" 2>&1 | tee "$MATRIX_DIR/$tool-$level.console.log"
    cell_exit="${PIPESTATUS[0]}"
    set -e

    # Resolve the run dir run.sh just created for this cell (newest by mtime).
    # Level alias "l1" matches the real "$tool-l1-fib-<stamp>" dir via the glob.
    RD="$(ls -dt "$HERE"/.runs/"$tool"-"$level"-* 2>/dev/null | head -1)"
    RD="${RD:-MISSING}"

    printf '%s %s %s %s\n' "$tool" "$level" "$cell_exit" "$RD" >> "$MANIFEST"
    echo ">>> [$N/$TOTAL] $tool $level -> exit=$cell_exit  run_dir=$RD"
  done
done

echo
echo "──────── aggregating $TOTAL cells -> results.json ────────"

# Aggregate every cell's meta.json into one JSON array. Read the manifest and
# matrix dir from argv (no fragile shell interpolation). A cell with a missing/
# unreadable meta.json gets a flagged placeholder so the report can surface it.
python3 - "$MANIFEST" "$MATRIX_DIR" <<'PY'
import json, sys, os

manifest_path, matrix_dir = sys.argv[1], sys.argv[2]
results = []
with open(manifest_path) as fh:
    for raw in fh:
        line = raw.strip()
        if not line:
            continue
        # "tool level cell_exit run_dir" — run_dir has no spaces (.runs path).
        tool, level, cell_exit, run_dir = line.split(None, 3)
        try:
            cell_exit = int(cell_exit)
        except ValueError:
            pass
        meta_path = os.path.join(run_dir, "meta.json")
        if run_dir != "MISSING" and os.path.isfile(meta_path):
            try:
                with open(meta_path) as mf:
                    rec = json.load(mf)
                rec.setdefault("cell_exit", cell_exit)
                results.append(rec)
                continue
            except (OSError, ValueError) as e:
                err = f"meta.json unreadable: {e}"
        else:
            err = "meta.json missing"
        results.append({
            "tool": tool,
            "level": level,
            "run_dir": run_dir,
            "cell_exit": cell_exit,
            "error": err,
        })

out = os.path.join(matrix_dir, "results.json")
with open(out, "w") as fh:
    json.dump(results, fh, indent=2)
    fh.write("\n")

scored = sum(1 for r in results if "error" not in r)
print(f"cells aggregated : {len(results)}")
print(f"with meta.json   : {scored}/{len(results)}")
print(f"results.json     : {out}")
PY

echo
echo "════════ matrix sweep complete ════════"
echo "matrix dir  : $MATRIX_DIR"
echo "results.json: $MATRIX_DIR/results.json"
echo "manifest    : $MANIFEST"
echo "console logs: $MATRIX_DIR/*.console.log"
