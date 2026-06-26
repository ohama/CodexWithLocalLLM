---
phase: 05-reproducibility-guide
verified: 2026-06-26
status: passed
score: 7/7 must-haves verified
gaps: []
---

# Phase 5: Reproducibility Guide — Verification

**Status:** passed (7/7). REPRO-01/02/03 all satisfied.

- benchmark/REPRODUCE.md (202 lines, committed, not gitignored): Overview → Preconditions
  (live verification commands, all confirmed working) → Run guide (command+effect per step) →
  From-scratch re-run sequence → Caveats.
- Preconditions ran live: gateway curl :4000 OK (qwen-122b, qwen-122b-codex), codex model
  qwen-122b-codex, openhands model openai/qwen-122b, ports :8011/:8001 LISTEN, tool versions present.
- Routes all runs via run.sh / run-matrix.sh → report.py → RESULTS.md. No `openhands --file`
  anti-pattern (negative grep clean; warning split across lines).
- Caveats cover LLM nondeterminism, step-unit incomparability, gitignored .runs/, codex L3
  truncation, serial-only.
- Scope clean: only REPRODUCE.md + README.md pointer; no harness behavior changes.
