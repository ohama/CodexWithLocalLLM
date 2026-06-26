# 04-01 SUMMARY — Run the full 6-cell matrix

**Plan:** 04-01 (phase 04-benchmark-run-and-reporting)
**Status:** Complete
**Date:** 2026-06-26

## What was built

`benchmark/run-matrix.sh` — drives all 6 cells (codex,openhands × l1-fib,l2-wordstat,l3-kvstore)
**serially** by calling `benchmark/run.sh <tool> <level>` once per cell (single mlx backend; the driver
never grabs `.runs/.lock` — run.sh owns the per-cell mutex), then aggregates the 6 per-run `meta.json`
into one `results.json` under a timestamped `benchmark/.runs/matrix-<ts>/` dir. Console logs preserved per cell.

## Execution (real LLM time, serial)

Full matrix executed: `benchmark/.runs/matrix-20260626-042701/` (6/6 cells, each with transcript.log +
meta.json carrying all 4 metrics from score.py).

## Results (corrected — see RESULTS.md for full report)

| tool | level | passed | time | files/loc |
|------|-------|--------|------|-----------|
| codex | l1-fib | PASS | 26s | 1/31 |
| codex | l2-wordstat | PASS | 98s | 4/148 |
| codex | l3-kvstore | **FAIL** | 14s | 0/0 (genuine — truncated after `mkdir kvstore`) |
| openhands | l1-fib | PASS | 49s | 1/31 |
| openhands | l2-wordstat | PASS | 145s | 4/222 |
| openhands | l3-kvstore | PASS | 147s | 9/362 |

## Deviations (auto-handled, Rule 3)

1. **Orphaned first sweep.** The initial sweep was backgrounded inside a subagent that exited, orphaning
   the process mid-cell-2. Re-launched as a harness-tracked background job from the orchestrator; the full
   sweep then completed (matrix-20260626-042701).
2. **OpenHands isolation leak (RUN-02) on L2/L3.** `run.sh` fed openhands `--file <canonical PROMPT.md>`,
   which anchored its workdir to the canonical `tasks/<level>/` dir → solution leaked there, run dir empty,
   judge scored 0 files → false FAIL. Fixed `run.sh` to feed the prompt inline via `--task` (commit
   `1435e87`); re-ran openhands L2 + L3 → both PASS with output in RUN_DIR, no leak. Leaked files quarantined
   out of the canonical task dirs; `results.json` re-aggregated to the corrected per-cell latest runs.
3. **codex L3 genuine FAIL** kept as-is (not re-run) — real truncation, correctly judged.

## Artifacts

- `benchmark/run-matrix.sh` (committed)
- `benchmark/.runs/matrix-20260626-042701/results.json` (gitignored — baked into committed RESULTS.md by 04-02)
- `benchmark/run.sh` isolation fix (commit `1435e87`)

## Requirements

REP-01 (all 6 cells executed + metrics collected) — satisfied.
