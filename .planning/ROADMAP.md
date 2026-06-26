# Roadmap: Agent Benchmark — Codex vs OpenHands

## Overview

This milestone builds a reproducible benchmark harness that runs the same three coding tasks against both Codex CLI and OpenHands on one local backend (qwen-122b via LiteLLM :4000), measures ability and time under identical conditions, and records the comparison so anyone can reproduce it. The journey follows the data flow: first fix the tasks, then build an equal-conditions runner, then collect metrics automatically, then run the full matrix and record results, and finally write the reproducibility guide that ties every command to its effect.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Fixed Tasks** - Three fixed-complexity, tool-agnostic tasks with objective pass criteria
- [x] **Phase 2: Equal-Conditions Runner** - One command runs (tool, level) in isolation on the same model
- [x] **Phase 3: Metric Collection** - Four metrics captured automatically with independent pass/fail
- [ ] **Phase 4: Benchmark Run & Reporting** - Full matrix executed and recorded as comparison artifact
- [ ] **Phase 5: Reproducibility Guide** - A user can reproduce the whole benchmark from the docs

## Phase Details

### Phase 1: Fixed Tasks
**Goal**: Three fixed-complexity coding tasks exist (L1 single-file, L2 multi-file CLI, L3 multi-module service), tool-agnostic, each with an objective "tests pass" criterion.
**Depends on**: Nothing (first phase)
**Requirements**: TASK-01, TASK-02, TASK-03
**Success Criteria** (what must be TRUE):
  1. Three task specs exist at fixed locations — L1 (fib single-file), L2 (wordstat multi-file CLI), L3 (KV multi-module service).
  2. Each task ships an independent test using only Python stdlib; the test exits 0 on pass and nonzero on fail.
  3. Each task's prompt is stored as identical text in one canonical place, independent of which tool will run it.
  4. Running the test for each level against its reference/fixture solution passes for all three levels.
**Plans**: 2 plans

Plans:
- [x] 01-PLAN.md — Define and freeze L1/L2/L3 task specs + prompts + pass-criterion README (one canonical location)
- [x] 02-PLAN.md — Write stdlib-only independent judge per level + reference solutions, validated (exit 0 on reference, nonzero on broken)

### Phase 2: Equal-Conditions Runner
**Goal**: A single command runs a chosen (tool, level) under identical, isolated conditions against qwen-122b, non-interactively and serially.
**Depends on**: Phase 1
**Requirements**: RUN-01, RUN-02, RUN-03, RUN-04, RUN-05
**Success Criteria** (what must be TRUE):
  1. One command (e.g. `run.sh <tool> <level>`) launches a run for the chosen tool and level.
  2. Each run executes in a fresh isolated work directory with no leftover state from prior runs or the other tool.
  3. Both codex and openhands are invoked against qwen-122b (LiteLLM :4000); the same model is confirmable from the run log.
  4. codex runs with `< /dev/null` and openhands with `--headless`; neither hangs on stdin nor blocks on an interactive prompt.
  5. Runs are serialized so only one tool hits the single backend at a time (no concurrent contention).
**Plans**: 3 plans

Plans:
- [x] 01-PLAN.md — Runner scaffold: arg parse + level normalize + isolated run dir + serial lock + gateway preflight (stubbed invocation)
- [x] 02-PLAN.md — Wire non-interactive same-model invocation: codex `< /dev/null` + openhands `--headless`, transcript capture, model-confirming meta.json
- [x] 03-PLAN.md — Live smoke (L1) for both tools, serial, with human-verify of openhands output isolation

### Phase 3: Metric Collection
**Goal**: Every run automatically produces the four metrics, with success judged by an independent test re-run rather than tool self-report.
**Depends on**: Phase 2
**Requirements**: MET-01, MET-02, MET-03, MET-04
**Success Criteria** (what must be TRUE):
  1. After a run, pass/fail is decided by re-running the task's independent test (tool self-report is not trusted) and recorded.
  2. Wall-clock duration for each run is measured and recorded.
  3. Step / tool-call count (file edits, command executions, self-corrections) is extracted from the run and recorded.
  4. Output size (file count and lines of code) is measured and recorded.
  5. All four metrics for a run land in a single structured record (one row / JSON per run).
**Plans**: 2 plans

Plans:
- [x] 03-01-PLAN.md — Create score.py: independent judge re-run (MET-01) + wall-clock duration (MET-02), extend meta.json
- [x] 03-02-PLAN.md — Extend score.py: tool-aware step count (MET-03) + output size (MET-04); auto-hook scorer into run.sh

### Phase 4: Benchmark Run & Reporting
**Goal**: Execute the full 2-tools × 3-levels matrix and record results as a comparison artifact with preserved transcripts.
**Depends on**: Phase 3
**Requirements**: REP-01, REP-02, REP-03
**Success Criteria** (what must be TRUE):
  1. All six cells (2 tools × 3 levels) are executed and their metrics collected.
  2. Results are presented as a tool × level matrix table including success and time columns.
  3. Raw logs/transcripts for every run are preserved and referenced from the report.
  4. A per-level summary describes the codex-vs-openhands difference in time, process, and output.
**Plans**: TBD

Plans:
- [ ] 04-01: Run the full matrix and collect/store all metrics and transcripts
- [ ] 04-02: Generate the tool × level results table and per-level difference summaries

### Phase 5: Reproducibility Guide
**Goal**: A user can reproduce the entire benchmark from the documentation alone, with every command and its effect spelled out.
**Depends on**: Phase 4
**Requirements**: REPRO-01, REPRO-02, REPRO-03
**Success Criteria** (what must be TRUE):
  1. A step-by-step guide lists each command and its effect and runs top to bottom.
  2. Preconditions (LiteLLM/mlx up, model = qwen-122b, openhands settings) have documented verification commands.
  3. One place explains how to re-run the whole measurement from scratch.
  4. Following the guide on a clean checkout reproduces the matrix (or clearly states the expected outputs).
**Plans**: TBD

Plans:
- [ ] 05-01: Write the step-by-step run guide with precondition checks and effects per command
- [ ] 05-02: Add the from-scratch re-run section and validate by following it clean

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Fixed Tasks | 2/2 | ✓ Complete | 2026-06-26 |
| 2. Equal-Conditions Runner | 3/3 | ✓ Complete | 2026-06-26 |
| 3. Metric Collection | 2/2 | ✓ Complete | 2026-06-26 |
| 4. Benchmark Run & Reporting | 0/2 | Not started | - |
| 5. Reproducibility Guide | 0/2 | Not started | - |
