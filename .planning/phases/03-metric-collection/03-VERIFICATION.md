---
phase: 03-metric-collection
verified: 2026-06-26T00:00:00Z
status: passed
score: 5/5 must-haves verified
re_verification: false
---

# Phase 3: Metric Collection Verification Report

**Phase Goal:** Every run automatically produces the four metrics, with success judged by an INDEPENDENT test re-run (not tool self-report), all four landing in one structured per-run record. Phase 3 only makes a single run yield the 4 metrics — NO full matrix, NO results table/report, NO reproducibility doc.
**Verified:** 2026-06-26
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| - | ----- | ------ | -------- |
| 1 | Pass/fail decided by re-running the task's independent judge, NOT tool self-report | ✓ VERIFIED | `score.py:124-137` builds `judge = tasks/<level>/test.py`, runs it via `subprocess.run([sys.executable, judge, run_dir])`, sets `passed = (returncode == 0)`. exit_code/transcript never consulted. Proven by injection test: corrupted fib.py with meta `exit_code=0` → `passed=False`, `judge_exit=1`. |
| 2 | Wall-clock duration measured + recorded | ✓ VERIFIED | `score.py:139-148` parses `started_at`/`finished_at` ISO timestamps → `duration_seconds`. codex=43s, openhands=49s in meta.json. |
| 3 | Step/tool-call count extracted, tool-aware | ✓ VERIFIED | `score.py:45-77` branches on `meta["tool"]`: codex counts standalone `exec` blocks, openhands reads "Number of agent messages". Records `step_method`. codex steps=2 (2 exec markers in transcript), openhands steps=4 (transcript line confirms). |
| 4 | Output size (file count + LOC) measured + recorded | ✓ VERIFIED | `score.py:80-106` walks run dir, excludes `transcript.log`, `meta.json`, `__pycache__/`, `.pyc`. Both samples: files=1, loc=31. Corrupted 2-line copy → loc=2 (counting works). |
| 5 | All four metrics land in a single structured record (one JSON per run) | ✓ VERIFIED | `score.py:156-158` writes all of passed/judge_exit/duration_seconds/steps/step_method/files/loc back into the run's `meta.json`. Both sample meta.json files contain all four. |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `benchmark/score.py` | Standalone scorer producing 4 metrics | ✓ VERIFIED | 178 lines, stdlib-only, no stubs. Functions extract_steps, measure_output, score_run all substantive. Runs cleanly on both samples; idempotent on re-run. |
| `benchmark/run.sh` | Auto-invokes scorer after meta write, guarded | ✓ VERIFIED | Section 10b (lines 201-212): `set +e; python3 score.py "$RUN_DIR"; SCORE_EXIT=$?; set -e` placed AFTER meta.json write (section 10). Scorer failure warns but never aborts. |
| `benchmark/tasks/l1-fib/test.py` | Independent judge accepting run_dir arg | ✓ VERIFIED | Accepts `solution_dir` argv, imports fib fresh (pops cache), asserts frozen values, exits 0/1. |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| run.sh | score.py | `python3 "$HERE/score.py" "$RUN_DIR"` after meta.json write, under `set +e` | ✓ WIRED | Lines 206-209; guarded so scorer never aborts the run. |
| score.py | tasks/<level>/test.py | `subprocess.run([sys.executable, judge, run_dir])`, returncode → passed | ✓ WIRED | Independence proven via injection test. |
| score.py | meta.json | `json.dump(meta, ...)` writes 4 metrics in place | ✓ WIRED | Verified in both sample meta.json. |

### Requirements Coverage

| Requirement | Status | Notes |
| ----------- | ------ | ----- |
| MET-01 (independent pass/fail) | ✓ SATISFIED | Judge subprocess returncode; exit_code/transcript ignored (injection-proven). |
| MET-02 (wall-clock duration) | ✓ SATISFIED | duration_seconds from timestamps. |
| MET-03 (step/tool-call count) | ✓ SATISFIED | Tool-aware with step_method label. |
| MET-04 (output size) | ✓ SATISFIED | files + loc, harness artifacts excluded. |

### Independent Re-run Results (no new agent runs)

```
codex-l1-fib:     passed=True  duration_seconds=43  steps=2 (codex:count of 'exec' blocks)  files=1  loc=31
openhands-l1-fib: passed=True  duration_seconds=49  steps=4 (openhands:Number of agent messages)  files=1  loc=31
```
Matches expected (codex steps=2, openhands steps=4, files=1, passed true).

### Independence Proof (MET-01)

Copied codex run dir, replaced fib.py with `return 999` (meta exit_code stayed 0), re-scored:
`exit_code=0  passed=False  judge_exit=1` — the judge re-run, not the tool's self-report, decides correctness.

### Scope Check (no Phase 4/5 work)

- No matrix loop: run.sh runs a single tool×level per invocation; the only `for`/`while` grep hits are comment text.
- No results table / comparison report: no such file or code (grep for matrix/results table/comparison/reproducib empty).
- No reproducibility doc: README.md (58 lines) carries usage only; no repro guide artifact.

### Anti-Patterns Found

None. No TODO/FIXME/placeholder/empty-return stubs in score.py or run.sh additions. Best-effort error handling is intentional and self-describing (e.g. `transcript-missing`, `judge not found`).

### Human Verification Required

None. All five success criteria are programmatically verifiable and were verified against the actual codebase and live re-runs of score.py.

### Gaps Summary

No gaps. All four metrics are produced automatically, pass/fail is judged by an independent test re-run (proven independent of tool self-report), and all four land in one structured per-run meta.json. Scope correctly limited to single-run scoring; no Phase 4/5 artifacts present.

---

_Verified: 2026-06-26_
_Verifier: Claude (gsd-verifier)_
