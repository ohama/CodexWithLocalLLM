### Findings & honesty (read this)

Headline pass counts: **codex 5/7 · qclaude(122b) 6/7 · qclaude35(35b) 6/7.** But the
*kinds* of failure are the story — each isolates a different variable.

1. **L3-kvstore — agent-loop, not model (codex FAIL, both Claude Code PASS).** codex's L3
   is a model-loop degeneration: first action `mkdir -p kvstore` (empty stdout), then
   qwen-122b re-emits its preamble with no tool call and `codex exec` exits clean with
   **0 files**. The *identical 122b weights* under Claude Code completed the package
   (9f/376loc), and even **35b** completed it (8f/230loc). So L3 is a Codex agent-loop
   failure, not a model-capability one.

2. **L4-calc — the one clean model-size signal (122b PASS, 35b FAIL).** Both 122b runs
   (codex and qclaude) pass. **35b fails**: its calculator accepts the invalid expression
   `2 3` (two numbers, no operator) and exits 0 instead of erroring
   (`FAIL l4-calc: invalid expr '2 3' exited 0 (want nonzero)`). This is a real
   error-handling gap the larger model catches — the place where 122b earns its cost.

3. **L7-kvapi — layout variance, disclosed (codex FAIL, qclaude FAIL, qclaude35 PASS).**
   - **codex**: same degeneration as L3 — built **0 files**.
   - **qclaude(122b)**: built a *working* service (its own pytest: **18/18 functional
     tests pass**) but nested everything under a `solution/` subdir; the frozen contract's
     judge wants `serve.py` at the run-dir **root**, so it scores FAIL on layout, not
     function.
   - **qclaude35(35b)**: built the same service with `serve.py` at the **root** → judge
     PASS. This cross-confirms that qclaude(122b)'s L7 FAIL was a layout-choice variance,
     not an inability to build the service.

4. **Speed — 35b is ~1.5–3.4× faster than 122b** under the same client (e.g. L3 103s vs
   351s, L5 121s vs 342s) — a real model-size effect (smaller model prefills and generates
   faster).
5. **Why both qclaude runs are slower than codex — measured, and it is NOT "caching".**
   codex also runs against the same local mlx, so it gets no Anthropic prompt caching
   either. The real cause is **prompt size × cold prefill**: Claude Code sends a very large
   prompt (system prompt + ~25 tool schemas + skills/agents), and mlx re-prefills it cold
   on **every task** — per-task time-to-first-token was **79–196s** (40–60% of each task's
   wall-clock), i.e. the giant prompt is processed before any output. Prefill is linear on
   this 122b (~1.75s per 1k prompt tokens; 16k tok → 28s, measured). mlx's prompt cache
   (on by default, size 10) reuses an *identical* prefix in ~0.1s (measured), but across
   the 7 separate tasks the static system-prompt prefix is not reused (per-task cwd/session
   content near the top breaks the common prefix), so each task pays the full cold prefill.
   codex's prompts are much smaller, so its prefill — and total time — is far lower.
   Levers to close the gap: shrink Claude Code's prompt (fewer tools/skills/plugins/MCP),
   prefer the 35b tier, and size `--prompt-cache-*` so the static prefix survives.
6. **Two levers measured.** (a) **Shrinking the prompt works, dramatically.** Re-running
   L1 on the same 122b with `--bare --tools Write Edit Read Bash --disable-slash-commands`
   (3 tool schemas instead of 25, no CLAUDE.md/memory/skills injection) cut
   **time-to-first-token 98.6s → 8.9s (11×)** and **total 158s → 28.5s (5.5×)**, still
   PASS — i.e. down to codex-class speed (~23s). This is the highest-leverage fix and
   confirms the prompt size, not the model, was the cost. (b) **`--prefill-step-size` does
   not help:** bumping the mlx server 2048 → 8192 left a fresh 20k-token cold prefill
   unchanged (37.7s → 39.4s, within noise) — the prefill bottleneck is compute, not batch
   step size. Reverted.

**Bottom line.** For these small, well-specified tasks the **35b (qclaude35) is a strong,
much faster default** — 6/7, failing only one corner error-case — while the **122b buys
that corner back** (calc error handling). codex's 5/7 is held down by agent-loop
degeneration (L3/L7), not by the model, which is the same 122b qclaude runs.
