---
phase: 04-benchmark-run-and-reporting
verified: 2026-06-26T00:00:00Z
status: passed
score: 4/4 truths verified
re_verification: false
---

# Phase 4: Benchmark Run & Reporting Verification Report

**Phase Goal:** Execute the full 2-tools × 3-levels matrix and record results as a comparison artifact with preserved transcripts.
**Verified:** 2026-06-26
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | All six cells (2 tools × 3 levels) executed and metrics collected (REP-01) | ✓ VERIFIED | `matrix-20260626-042701/results.json` holds 6 cell records; each carries passed, duration_seconds, steps, step_method, files, loc |
| 2 | Results presented as tool×level matrix table with success + time columns (REP-02) | ✓ VERIFIED | `RESULTS.md` lines 13-20: 6-row table with Success, Time, Steps(step_method), Size columns |
| 3 | Raw transcripts preserved and referenced from report; per-level codex-vs-openhands diff (REP-03) | ✓ VERIFIED | All 6 `transcript.log` files exist in referenced run dirs; RESULTS.md lines 38-59 per-level diffs, lines 61-261 transcript refs + baked excerpts |
| 4 | Report is committed, self-contained, idempotently regenerable, and honest about corrections | ✓ VERIFIED | RESULTS.md + report.py both git-tracked (commits f6670f4, 4a090ae); `python3 report.py` produces byte-identical output (git diff empty); honesty note present lines 31-36 |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `benchmark/run-matrix.sh` | Serial 6-cell driver via run.sh, no driver-held lock | ✓ VERIFIED | 122 lines, executable, committed (95bc63f). Loops tools×levels serially calling `run.sh` (line 49); explicitly does NOT acquire `.runs/.lock` (run.sh owns per-cell mutex, lines 9-13); failed cell recorded not aborted (set +e / PIPESTATUS) |
| `benchmark/.runs/matrix-20260626-042701/results.json` | 6 cells × 4 metrics | ✓ VERIFIED | Present locally (.runs gitignored). 6 records, each with passed, duration_seconds, steps+step_method, files, loc. codex L3 passed=false/0f/0loc |
| `benchmark/RESULTS.md` | Committed, self-contained comparison report | ✓ VERIFIED | 266 lines, git-tracked (f6670f4). Matrix table + reading note + honesty note + per-level diffs + transcript excerpts |
| `benchmark/report.py` | stdlib-only results.json → RESULTS.md generator | ✓ VERIFIED | 13.5KB, git-tracked (4a090ae). Imports only glob/json/os/re/sys. Ran successfully (exit 0), regeneration idempotent |
| 6× `transcript.log` | Preserved per-run transcripts | ✓ VERIFIED | All 6 referenced run dirs contain non-empty transcript.log (3.6KB-17KB) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| run-matrix.sh | run.sh | `bash "$HERE/run.sh" "$tool" "$level"` per cell | ✓ WIRED | Line 49; serial, no `&`; driver does not hold lock |
| run-matrix.sh | results.json | aggregates per-cell meta.json via inline python3 | ✓ WIRED | Lines 69-114; reads manifest, merges meta.json into JSON array |
| report.py | results.json | argv path / latest-matrix glob | ✓ WIRED | Read 6 cells, rendered report |
| report.py | RESULTS.md | writes OUT_PATH | ✓ WIRED | Idempotent: git diff empty after regen |
| RESULTS.md | transcripts | path refs + baked ANSI-stripped excerpts | ✓ WIRED | Each of 6 cells references its transcript.log path + excerpt |

### Requirements Coverage

| Requirement | Status | Notes |
|-------------|--------|-------|
| REP-01 (all 6 cells executed + metrics) | ✓ SATISFIED | 6/6 cells in results.json with all 4 metrics |
| REP-02 (tool×level matrix, success+time) | ✓ SATISFIED | RESULTS.md table with Success + Time (+Steps[step_method] + Size) |
| REP-03 (transcripts preserved + referenced; per-level diff) | ✓ SATISFIED | Transcripts exist + referenced/excerpted; per-level codex-vs-openhands diffs present |

### Honesty / Disclosure Check

- ✓ openhands L2/L3 isolation-leak re-run after `--file`→`--task` fix (commit 1435e87) disclosed — RESULTS.md honesty note item 1 (line 35).
- ✓ codex L3 reported as a GENUINE FAIL (truncated after `mkdir kvstore`, 0f/0loc) — honesty note item 2 (line 36), table line 19, transcript excerpt lines 197-228. Not hidden or re-run away.
- ✓ step_method surfaced in table cells, reading note, and each per-level process line, with explicit "units differ — not directly comparable" caveat (lines 25-28, 43/50/57).

### Anti-Patterns Found

None. No TODO/FIXME/placeholder/stub patterns in run-matrix.sh, report.py, or RESULTS.md. The single FAIL cell is a genuine, disclosed measurement, not a stub.

### Scope Check (no Phase 5 leakage)

- ✓ No Phase 5 reproducibility tutorial added. No `05-*` phase dir exists; no reproduction/step-by-step-guide/tutorial content found in `benchmark/`. README.md contains no "reproduc" content.

### Human Verification Required

None required for goal achievement. (Optional: a human may eyeball RESULTS.md rendering in a markdown viewer, but all structural, metric, wiring, and honesty checks passed programmatically.)

### Gaps Summary

No gaps. All four observable truths verified, all five required artifacts pass existence/substantive/wired checks, all five key links wired, all three requirements (REP-01/02/03) satisfied, honesty disclosures present, and no Phase 5 scope leakage. report.py regenerates RESULTS.md idempotently (git diff empty after re-run).

---

_Verified: 2026-06-26_
_Verifier: Claude (gsd-verifier)_
