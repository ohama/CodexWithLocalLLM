# Project Milestones: Agent Benchmark — Codex vs OpenHands

## v1.0 Agent Benchmark (Shipped: 2026-06-26)

**Delivered:** A reproducible harness that runs the same 3-complexity-level coding tasks against
Codex CLI and OpenHands on one local backend (qwen-122b via LiteLLM :4000), measures ability/time
under identical conditions, and records the comparison so anyone can reproduce it.

**Phases completed:** 1-5 (10 plans total)

**Key accomplishments:**
- 3 fixed, tool-agnostic tasks (L1 fib / L2 wordstat / L3 KV store) with stdlib-only independent
  judges — success decided by judge re-run, never tool self-report.
- `run.sh` equal-conditions runner: one command per (tool, level), isolated dir, serial mkdir-lock,
  same model (qwen-122b), non-interactive (codex `< /dev/null`, openhands inline `--task`).
- `score.py` auto-collects 4 metrics per run into meta.json: pass/fail (independent judge),
  wall-clock, tool-aware steps (+step_method), output size.
- `run-matrix.sh` + `report.py` → full 2×3 matrix executed and committed as `benchmark/RESULTS.md`
  (durable, since `.runs/` is gitignored), with transcript excerpts + per-level diffs + honesty notes.
- `benchmark/REPRODUCE.md` reproducibility guide: preconditions (live-verified commands), per-command
  effects, from-scratch re-run sequence.
- Found & fixed a real OpenHands isolation leak (`--file` anchored workdir to canonical task dir →
  false FAILs); re-ran openhands L2/L3 → both PASS.

**Final result (qwen-122b):**
- codex: L1 PASS 26s / L2 PASS 98s / L3 FAIL 14s (genuine truncation)
- openhands: L1 PASS 49s / L2 PASS 145s / L3 PASS 147s

**Stats:**
- 5 phases, 10 plans, 18 requirements (18/18 shipped)
- benchmark harness ~1,200 LOC (Python + bash, excl. reference solutions)
- 70 commits, 2026-06-24 → 2026-06-26
- Git range: `632072a` → `c88111a`

**What's next:** TBD (candidates: add hermes for a 3-way matrix; token/cost accounting; repeat-run
averaging; an L4 larger/ambiguous task).

---
