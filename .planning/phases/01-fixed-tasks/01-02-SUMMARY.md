---
phase: 01-fixed-tasks
plan: 02
subsystem: benchmark
tags: [judge, test.py, reference-solution, python-stdlib, black-box, subprocess]

# Dependency graph
requires:
  - phase: 01-fixed-tasks
    plan: 01
    provides: "Frozen tool-agnostic PROMPT.md contracts (L1 fib, L2 wordstat, L3 kvstore) + README pass criterion"
provides:
  - "benchmark/tasks/l{1,2,3}-*/test.py — three independent, stdlib-only judges (exit 0 = PASS) reading solution_dir from argv[1]"
  - "benchmark/reference/l{1,2,3}-*/ — validated reference solutions proving each judge discriminates pass from fail"
affects: [phase-2-runner, phase-3-metrics]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Judge reads solution_dir from argv[1] (default cwd) so the Phase 2 runner can point it at any tool's output unchanged"
    - "L1 judge: importlib import + sys.modules.pop/invalidate_caches for clean re-runs across solution dirs"
    - "L2/L3 judges: black-box via subprocess so the judge is independent of internal module names (only entry-file names are fixed)"
    - "Hermetic fixtures: tempfile.TemporaryDirectory for crafted inputs (L2) and a fresh KVSTORE_PATH per run (L3)"

key-files:
  created:
    - benchmark/tasks/l1-fib/test.py
    - benchmark/tasks/l2-wordstat/test.py
    - benchmark/tasks/l3-kvstore/test.py
    - benchmark/reference/l1-fib/fib.py
    - benchmark/reference/l2-wordstat/wordstat.py
    - benchmark/reference/l2-wordstat/wordcount.py
    - benchmark/reference/l3-kvstore/cli.py
    - benchmark/reference/l3-kvstore/kvstore/__init__.py
    - benchmark/reference/l3-kvstore/kvstore/storage.py
  modified: []

key-decisions:
  - "L1 judge imports fib via importlib (path-injected) rather than subprocess: the contract is an in-process function API, so direct import is the faithful black-box check"
  - "L2 fixture uses strictly distinct counts down to the 5th slot (egg=2) with the only count-1 words below it, making the top-5 boundary unambiguous (honors plan-checker tie watch-item)"
  - "L3 get-miss detection uses an in-process sentinel (_MISSING) so an empty/false stored value is never confused with absence; cli maps sentinel -> exit 1"
  - "stdlib-only verified by a portable manual import scan (grep -RnE listing every import line), not a Perl negative-lookahead (unsupported by macOS ERE)"

patterns-established:
  - "Each judge prints a one-line PASS <level> on success or FAIL: <reason> lines on failure, then exits 0/1"
  - "Negative validation is part of the plan: every judge proven to exit nonzero on a deliberately broken solution"

# Metrics
duration: 9min
completed: 2026-06-26
---

# Phase 1 Plan 02: Independent Judges + Reference Solutions Summary

**Built three independent, stdlib-only judges (`tasks/l{1,2,3}-*/test.py`) that enforce the frozen Plan 01 contracts as the objective pass criterion, plus a validated reference solution per level — each judge exits 0 on its reference and nonzero on a deliberately broken solution, so it can score any tool's output unchanged in Phase 2.**

## Performance

- **Duration:** ~9 min
- **Started:** 2026-06-26
- **Completed:** 2026-06-26
- **Tasks:** 3
- **Files created:** 9

## Accomplishments

- **L1 (fib):** judge path-injects `solution_dir`, imports `fib` via `importlib` (with `sys.modules.pop` + `invalidate_caches` for clean re-runs), and asserts every pinned value `fib(0..30)` is exactly correct and `int`-typed.
- **L2 (wordstat):** multi-file reference (`wordstat.py` CLI + `wordcount.py` helper); judge runs the CLI as a subprocess on crafted inputs and parses the EXACT `total:`/`unique:`/`top:` stdout, validating a tie-free top-5, an alphabetical tie-break (`alpha`/`delta` both 2), and tokenization (`"The cat's"` -> `the,cat,s`).
- **L3 (kvstore):** multi-module reference (`cli.py` + `kvstore/{__init__,storage}.py`, JSON persistence keyed on `KVSTORE_PATH`); judge drives `set/get/delete/list` across separate subprocesses with a fresh temp `KVSTORE_PATH`, verifying multi-module files, cross-process persistence, and the pinned exit codes (get-miss=1, delete idempotent=0, list sorted asc).
- All three judges read `solution_dir` from `argv[1]` (default cwd) — Phase 2 runner can point them at any tool's output without modification.

## Judge Invocation (per level)

```
python3 benchmark/tasks/l1-fib/test.py      benchmark/reference/l1-fib       # PASS l1-fib,      exit 0
python3 benchmark/tasks/l2-wordstat/test.py benchmark/reference/l2-wordstat  # PASS l2-wordstat, exit 0
python3 benchmark/tasks/l3-kvstore/test.py  benchmark/reference/l3-kvstore   # PASS l3-kvstore,  exit 0
```

## Validation (both directions, all confirmed)

| Level | Judge vs reference | Judge vs broken solution |
|-------|--------------------|--------------------------|
| L1 | exit 0 (PASS l1-fib) | `fib(n)->n` stub -> exit 1 (FAIL on fib(2),(3),(10),(20),(30)) |
| L2 | exit 0 (PASS l2-wordstat) | `print("total: 0")` stub -> exit 1 (FAIL: bad stdout) |
| L3 | exit 0 (PASS l3-kvstore) | always-`exit 0`, no-persistence cli -> exit 1 (FAIL: get/persistence/exit-codes) |

stdlib-only confirmed via a portable manual import scan: only `os, sys, subprocess, tempfile, importlib, json, re` plus intra-solution imports (`from kvstore import Store`, `from .storage import ...`, `import wordcount`). No third-party imports.

## Task Commits

Each task committed atomically (files staged individually):

1. **Task 1: L1 judge + reference** - `eba7a1e` (test)
2. **Task 2: L2 judge + multi-file reference** - `d22ea5f` (test)
3. **Task 3: L3 judge + multi-module reference** - `667e094` (test)

**Plan metadata:** see final `docs(01-02)` commit.

## Files Created

- `benchmark/tasks/l1-fib/test.py` - L1 judge (importlib-based contract check).
- `benchmark/tasks/l2-wordstat/test.py` - L2 judge (subprocess; total/unique/top + tie + tokenization).
- `benchmark/tasks/l3-kvstore/test.py` - L3 judge (subprocess; files, persistence, exit codes, list).
- `benchmark/reference/l1-fib/fib.py` - iterative stdlib reference.
- `benchmark/reference/l2-wordstat/{wordstat.py,wordcount.py}` - multi-file CLI reference.
- `benchmark/reference/l3-kvstore/{cli.py,kvstore/__init__.py,kvstore/storage.py}` - multi-module service reference.

## Decisions Made

- L1 uses in-process `importlib` import (the contract is a function API); L2/L3 use subprocess black-box (only entry-file names are fixed by the contract, internal module names are free).
- L2 fixture deliberately avoids count-1 ambiguity at the 5th slot (egg=2, with fig/grape=1 below it) to keep the top-5 boundary deterministic.
- L3 get-miss uses an in-process sentinel so an empty/falsey value is never mistaken for absence.
- stdlib-only verified with a portable import-line scan, not a Perl negative-lookahead grep (unsupported on macOS ERE — plan-checker watch-item #1).

## Deviations from Plan

None - plan executed exactly as written. All three `<verify>` blocks and the `<verification>` suite passed on first run.

## Issues Encountered

None.

## User Setup Required

None - stdlib-only; no external services or pip installs.

## Next Phase Readiness

- The objective pass criterion (MET-01) is now executable: `python3 benchmark/tasks/<level>/test.py <solution_dir>` returns exit 0/nonzero for any solution directory.
- Phase 2 runner can invoke these judges unchanged against each tool's output dir. Carry-forward reminders from STATE.md still apply: `codex exec` needs `< /dev/null` to avoid stdin hang; tools must run serially against the single mlx backend.

---
*Phase: 01-fixed-tasks*
*Completed: 2026-06-26*
