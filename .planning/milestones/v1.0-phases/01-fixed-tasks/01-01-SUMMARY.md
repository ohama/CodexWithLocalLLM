---
phase: 01-fixed-tasks
plan: 01
subsystem: benchmark
tags: [prompts, fixed-tasks, python-stdlib, contract, black-box-judge]

# Dependency graph
requires:
  - phase: 00-roadmap
    provides: PROJECT/ROADMAP/REQUIREMENTS defining the Codex-vs-OpenHands comparison and L1/L2/L3 task reuse
provides:
  - "benchmark/README.md — objective pass criterion (judge exits 0) + four shared conventions"
  - "Three frozen, tool-agnostic PROMPT.md files (L1 fib, L2 wordstat, L3 kvstore) with precise black-box contracts"
  - "Canonical task layout benchmark/tasks/l{1,2,3}-*/ that Plan 02 judges and references will populate"
affects: [02-judges-and-runner, fixed-tasks, phase-2-runner, phase-3-metrics]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Black-box contract prompts: each PROMPT.md pins exact file names, signatures, stdout format, and exit codes so one tool-agnostic test can judge any tool's output"
    - "Single canonical prompt location per level; identical text fed verbatim to every tool"

key-files:
  created:
    - benchmark/README.md
    - benchmark/tasks/l1-fib/PROMPT.md
    - benchmark/tasks/l2-wordstat/PROMPT.md
    - benchmark/tasks/l3-kvstore/PROMPT.md
  modified: []

key-decisions:
  - "Prompts never reference the hidden judge/test.py; trust is decided only by our independent test (Plan 02)"
  - "L3 persistence is keyed on env var KVSTORE_PATH (default ./kvstore.db) to make each run hermetic"
  - "Exit-code semantics pinned per command (get-miss=1, delete idempotent=0) so a black-box judge can key on them"

patterns-established:
  - "Each PROMPT.md = natural task text + explicit Contract section + stdlib-only note"
  - "Judge invocation convention: python3 tasks/<level>/test.py <solution_dir> (default cwd), exit 0 = PASS"

# Metrics
duration: 7min
completed: 2026-06-26
---

# Phase 1 Plan 01: Fixed Tasks (prompts + README) Summary

**Froze three tool-agnostic benchmark prompts (L1 fib single-file, L2 wordstat multi-file CLI, L3 kvstore multi-module service) with exact black-box contracts, plus a README defining the exit-0 pass criterion and shared conventions.**

## Performance

- **Duration:** ~7 min
- **Started:** 2026-06-26
- **Completed:** 2026-06-26
- **Tasks:** 3
- **Files modified:** 4 (created)

## Accomplishments
- Established the canonical `benchmark/` layout (`tasks/l1-fib`, `tasks/l2-wordstat`, `tasks/l3-kvstore`) as the single source of truth for prompts fed identically to both tools.
- Defined the objective, reproducible pass criterion in `benchmark/README.md`: a solution passes level X iff `python3 benchmark/tasks/<level>/test.py <solution_dir>` exits 0 — tool self-report is never trusted.
- Wrote three self-contained, stdlib-only prompts whose explicit Contract sections are precise enough for a single black-box judge per level (built in Plan 02).

## Task Commits

Each task was committed atomically:

1. **Task 1: benchmark/ structure + README** - `3e9a6f3` (feat)
2. **Task 2: L1 fib + L2 wordstat prompts** - `818310d` (feat)
3. **Task 3: L3 KV store prompt** - `3d3da81` (feat)

**Plan metadata:** see final `docs(01-01)` commit.

## Files Created/Modified
- `benchmark/README.md` - Pass criterion + 4 shared conventions (judge invocation, exit-code contract, stdlib-only, identical-prompt) + L1/L2/L3 summary table.
- `benchmark/tasks/l1-fib/PROMPT.md` - L1 single-file fib task + contract.
- `benchmark/tasks/l2-wordstat/PROMPT.md` - L2 multi-file CLI wordstat task + exact stdout contract.
- `benchmark/tasks/l3-kvstore/PROMPT.md` - L3 multi-module KV service task + CLI/persistence contract.

## Frozen Contracts (Plan 02 must mirror these)

### L1 — fib (single file)
- **File:** `fib.py` at solution root.
- **API:** `fib(n: int) -> int`.
- **Required values:** `fib(0)=0, fib(1)=1, fib(2)=1, fib(3)=2, fib(5)=5, fib(10)=55, fib(20)=6765, fib(30)=832040`.
- Returns `int`; no non-stdlib import.

### L2 — wordstat (multi-file CLI)
- **Entry:** `wordstat.py` at solution root, run as `python3 wordstat.py <textfile>`.
- **Token:** maximal run of ASCII alphanumerics `[A-Za-z0-9]`, lowercased; all else is a separator (`"The cat's"` -> `the, cat, s`).
- **Stdout (exact, in order):**
  ```
  total: <int>
  unique: <int>
  top:
  <word> <count>
  ...
  ```
  `top:` lists up to 5 entries, count descending then word ascending for ties, one space between word and count.
- **Exit 0** on success.

### L3 — kvstore (multi-module service)
- **Files required:** `cli.py` at root + `kvstore/` package with `__init__.py` and `storage.py`.
- **Persistence path:** env `KVSTORE_PATH` if set, else `./kvstore.db` in cwd.
- **CLI** (`python3 cli.py <cmd> ...`):
  - `set <key> <value>` -> exit 0.
  - `get <key>` -> print value + newline, exit 0; if missing -> no stdout, exit 1.
  - `delete <key>` -> idempotent, exit 0 whether or not key existed.
  - `list` -> all keys one-per-line sorted ascending, exit 0 (empty -> no output).
- Cross-process persistence guaranteed (same `KVSTORE_PATH`). Keys/values non-empty, no newlines.

## Decisions Made
- Prompts deliberately omit any reference to the hidden judge/`test.py` (design_notes): the agent satisfies the contract; trust is decided by our independent test in Plan 02 (forward ref MET-01).
- `KVSTORE_PATH` (default `./kvstore.db`) chosen so each judge run is hermetic and cross-process persistence is testable.
- Per-command exit-code semantics pinned (get-miss=1, delete idempotent=0) because the black-box judge keys on them.

## Deviations from Plan
None - plan executed exactly as written.

## Issues Encountered
None. Note: git does not track empty directories, so the three `tasks/l{1,2,3}-*/` dirs first appear in version control via their PROMPT.md commits (Tasks 2-3) rather than the Task 1 README commit; all four files are present and committed.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Contracts are frozen and precise; Plan 02 can now build one tool-agnostic `tasks/<level>/test.py` judge per level and validate each against `reference/<level>/` solutions.
- Reminders carried for Phase 2 runner (from STATE.md): `codex exec` must use `< /dev/null` to avoid stdin hang; tools must run serially against the single mlx backend.

---
*Phase: 01-fixed-tasks*
*Completed: 2026-06-26*
