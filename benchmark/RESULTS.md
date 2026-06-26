# Benchmark Results — codex vs openhands (qwen-122b)

- **Source:** `benchmark/.runs/matrix-20260626-074243/results.json`
- **Matrix timestamp:** 20260626-074243
- **Model(s):** codex → `qwen-122b-codex`, openhands → `openai/qwen-122b`
  - Both are the same local **qwen-122b** family served at `http://localhost:4000/v1`; the two tools merely report the model string differently (codex: `qwen-122b-codex`, openhands: `openai/qwen-122b`).
- **Cells:** 12 (2 tools × 3 levels)

> This report is the **durable** record. `benchmark/.runs/` is gitignored, so the raw run directories are not committed — the metrics table and transcript excerpts below bake the evidence into version control (REP-02 + REP-03).

## Results matrix (REP-02)

| Tool | Level | Success | Time | Steps (step_method) | Size (files / loc) |
|------|-------|---------|------|---------------------|--------------------|
| codex | l1-fib | PASS | 23s | 2 (codex:count of 'exec' blocks) | 1f / 25loc |
| openhands | l1-fib | PASS | 47s | 4 (openhands:Number of agent messages) | 1f / 31loc |
| codex | l2-wordstat | PASS | 83s | 6 (codex:count of 'exec' blocks) | 4f / 191loc |
| openhands | l2-wordstat | PASS | 165s | 17 (openhands:Number of agent messages) | 4f / 305loc |
| codex | l3-kvstore | FAIL | 14s | 2 (codex:count of 'exec' blocks) | 0f / 0loc |
| openhands | l3-kvstore | PASS | 134s | 12 (openhands:Number of agent messages) | 9f / 360loc |

### Reading the numbers

- **Success** is decided ONLY by each level's independent black-box judge (`tasks/<level>/test.py`) re-run against the files the agent produced — the tool's own "all tests pass" claim is never trusted (MET-01).
- **Steps are NOT directly comparable across tools.** The two tools expose different units, so each count is shown with its `step_method`:
  - **codex** = count of `exec` tool-call blocks in the transcript.
  - **openhands** = the `Number of agent messages` reported in its conversation summary.
  A codex `10` and an openhands `16` are different kinds of events — compare the *shape* of the work, never the raw integers as if identical.
- **Size** = files produced in the run dir and total lines of code, excluding harness artifacts (`transcript.log`, `meta.json`, `__pycache__/`) (MET-04).

### Scoring honesty note (read this)

Two corrections were applied to the first raw matrix; both are disclosed here rather than silently baked into the numbers:

1. **openhands L2 / L3 were initially mis-scored FAIL** because of a harness isolation leak: an early `run.sh` invoked openhands with `--file` pointing at the prompt, which anchored the agent's working directory to the *canonical task dir* instead of the isolated run dir, so its output never landed where the judge looked. After switching to an inline `--task` (no workdir leak), L2 and L3 were **re-run** and both **PASS**. The numbers above are from those clean re-runs.
2. **codex L3 (`l3-kvstore`) is a GENUINE failure**, not a harness artifact. codex truncated at ~14s after only running `mkdir kvstore` — it produced an empty package (0 files, 0 loc) and the judge correctly fails it. This is reported as a real FAIL, not hidden or re-run away.

## Per-level codex vs openhands difference summary (REP-03)

### l1-fib

- **Time:** codex 23s vs openhands 47s (Δ +24s; **codex** faster).
- **Process (units differ — not directly comparable):** codex 2 (codex:count of 'exec' blocks) vs openhands 4 (openhands:Number of agent messages).
- **Output:** codex 1f/25loc vs openhands 1f/31loc (Δ +0f / +6loc).
- **Verdict:** codex **PASS**, openhands **PASS**.

### l2-wordstat

- **Time:** codex 83s vs openhands 165s (Δ +82s; **codex** faster).
- **Process (units differ — not directly comparable):** codex 6 (codex:count of 'exec' blocks) vs openhands 17 (openhands:Number of agent messages).
- **Output:** codex 4f/191loc vs openhands 4f/305loc (Δ +0f / +114loc).
- **Verdict:** codex **PASS**, openhands **PASS**.

### l3-kvstore

- **Time:** codex 14s vs openhands 134s (Δ +120s; **codex** faster).
- **Process (units differ — not directly comparable):** codex 2 (codex:count of 'exec' blocks) vs openhands 12 (openhands:Number of agent messages).
- **Output:** codex 0f/0loc vs openhands 9f/360loc (Δ +9f / +360loc).
- **Verdict:** codex **FAIL**, openhands **PASS**.

## Transcript references & evidence excerpts (REP-03)

Each run's transcript path and a short ANSI-stripped excerpt are embedded below so the evidence survives in the committed report even though `benchmark/.runs/` is gitignored.

### codex / l1-fib — PASS in 23s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/codex-l1-fib-20260626-074243/transcript.log`
- **Steps:** 2 (codex:count of 'exec' blocks) · **Size:** 1f / 25loc

```text
Reading additional input from stdin...
OpenAI Codex v0.142.0
--------
workdir: /Users/ohama/projs/codex/benchmark/.runs/codex-l1-fib-20260626-074243
model: qwen-122b-codex
provider: litellm
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: none
reasoning summaries: none
session id: 019f02e1-8ca3-7140-9ecd-6653478d4717
--------
user
# L1 — Fibonacci (single file)
    ... (excerpt trimmed) ...
- All required test cases (`fib(0)` through `fib(30)`)
- Runs cleanly with `python3 fib.py` and exits with code 0
All contract requirements are satisfied using only the Python standard library.
tokens used
48,604
The `fib.py` file has been created successfully at the project root. It contains:
- An iterative `fib(n: int) -> int` function that computes Fibonacci numbers efficiently
- All required test cases (`fib(0)` through `fib(30)`)
- Runs cleanly with `python3 fib.py` and exits with code 0
All contract requirements are satisfied using only the Python standard library.
```

### openhands / l1-fib — PASS in 47s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/openhands-l1-fib-20260626-075016/transcript.log`
- **Steps:** 4 (openhands:Number of agent messages) · **Size:** 1f / 31loc

```text
16:50:17 - LiteLLM:WARNING: common_utils.py:979 - litellm: could not pre-load bedrock-runtime response stream shape — Bedrock event-stream decoding will be unavailable. Error: No module named 'botocore'
16:50:17 - LiteLLM:WARNING: common_utils.py:24 - litellm: could not pre-load sagemaker-runtime response stream shape — SageMaker event-stream decoding will be unavailable. Error: No module named 'botocore'
/Users/ohama/.local/share/uv/tools/openhands/lib/python3.12/site-packages/openhands/sdk/llm/auth/openai.py:25: AuthlibDeprecationWarning: authlib.jose module is deprecated, please use joserfc instead.
It will be compatible before version 2.0.0.
  from authlib.jose import JsonWebKey, jwt
+----------------------------------------------------------------------+
|  OpenHands SDK v1.21.0                                               |
|                                                                      |
|  Report a bug: github.com/OpenHands/software-agent-sdk/issues        |
|  Get help: openhands.dev/joinslack                                   |
|  Scale up: openhands.dev/product/sdk                                 |
|                                                                      |
|  Set OPENHANDS_SUPPRESS_BANNER=1 to hide this message                |
+----------------------------------------------------------------------+
    ... (excerpt trimmed) ...
│                                                                              │
│ Finish with message:                                                         │
│ Created fib.py with fib(n) function satisfying all contract requirements.    │
│ All 8 assertions pass and the script exits cleanly with code 0.              │
╰──────────────────────────────────────────────────────────────────────────────╯
────────────────────────────────────────────────────────────────────────────────
Goodbye! 👋
Conversation ID: 8f4b1dfdc1834991bb4074f90e0e0fe6
Hint: run openhands --resume 8f4b1dfd-c183-4991-bb40-74f90e0e0fe6 to resume this
conversation.
```

### codex / l2-wordstat — PASS in 83s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/codex-l2-wordstat-20260626-074306/transcript.log`
- **Steps:** 6 (codex:count of 'exec' blocks) · **Size:** 4f / 191loc

```text
Reading additional input from stdin...
OpenAI Codex v0.142.0
--------
workdir: /Users/ohama/projs/codex/benchmark/.runs/codex-l2-wordstat-20260626-074306
model: qwen-122b-codex
provider: litellm
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: none
reasoning summaries: none
session id: 019f02e1-e426-7af3-ac11-a8ee4ca28c66
--------
user
# L2 — Word statistics CLI (multi-file)
    ... (excerpt trimmed) ...
```
total: 28
unique: 18
top:
the 4
dog 3
fox 3
a 2
brown 2
```
```

### openhands / l2-wordstat — PASS in 165s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/openhands-l2-wordstat-20260626-075103/transcript.log`
- **Steps:** 17 (openhands:Number of agent messages) · **Size:** 4f / 305loc

```text
16:51:04 - LiteLLM:WARNING: common_utils.py:979 - litellm: could not pre-load bedrock-runtime response stream shape — Bedrock event-stream decoding will be unavailable. Error: No module named 'botocore'
16:51:04 - LiteLLM:WARNING: common_utils.py:24 - litellm: could not pre-load sagemaker-runtime response stream shape — SageMaker event-stream decoding will be unavailable. Error: No module named 'botocore'
/Users/ohama/.local/share/uv/tools/openhands/lib/python3.12/site-packages/openhands/sdk/llm/auth/openai.py:25: AuthlibDeprecationWarning: authlib.jose module is deprecated, please use joserfc instead.
It will be compatible before version 2.0.0.
  from authlib.jose import JsonWebKey, jwt
+----------------------------------------------------------------------+
|  OpenHands SDK v1.21.0                                               |
|                                                                      |
|  Report a bug: github.com/OpenHands/software-agent-sdk/issues        |
|  Get help: openhands.dev/joinslack                                   |
|  Scale up: openhands.dev/product/sdk                                 |
|                                                                      |
|  Set OPENHANDS_SUPPRESS_BANNER=1 to hide this message                |
+----------------------------------------------------------------------+
    ... (excerpt trimmed) ...
│ - Top 5 entries with single space between word and count                     │
│ - Exit code 0 on success                                                     │
│                                                                              │
│ All 21 tests pass and CLI output matches the required format exactly.        │
╰──────────────────────────────────────────────────────────────────────────────╯
────────────────────────────────────────────────────────────────────────────────
Goodbye! 👋
Conversation ID: 961be9ab8d28430192cfa93d7ab3de08
Hint: run openhands --resume 961be9ab-8d28-4301-92cf-a93d7ab3de08 to resume this
conversation.
```

### codex / l3-kvstore — FAIL in 14s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/codex-l3-kvstore-20260626-074429/transcript.log`
- **Steps:** 2 (codex:count of 'exec' blocks) · **Size:** 0f / 0loc

```text
Reading additional input from stdin...
OpenAI Codex v0.142.0
--------
workdir: /Users/ohama/projs/codex/benchmark/.runs/codex-l3-kvstore-20260626-074429
model: qwen-122b-codex
provider: litellm
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: none
reasoning summaries: none
session id: 019f02e3-2b21-72c0-9e4a-4440849d8fd8
--------
user
# L3 — Key-value store service (multi-module)
    ... (excerpt trimmed) ...
  • Test the CLI contract
codex
Now I'll create the kvstore package with the storage module:
exec
/bin/zsh -lc 'mkdir -p kvstore' in /Users/ohama/projs/codex/benchmark/.runs/codex-l3-kvstore-20260626-074429
 succeeded in 0ms:
codex
tokens used
48,822
Now I'll create the kvstore package with the storage module:
```

### openhands / l3-kvstore — PASS in 134s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/openhands-l3-kvstore-20260626-075348/transcript.log`
- **Steps:** 12 (openhands:Number of agent messages) · **Size:** 9f / 360loc

```text
16:53:48 - LiteLLM:WARNING: common_utils.py:979 - litellm: could not pre-load bedrock-runtime response stream shape — Bedrock event-stream decoding will be unavailable. Error: No module named 'botocore'
16:53:49 - LiteLLM:WARNING: common_utils.py:24 - litellm: could not pre-load sagemaker-runtime response stream shape — SageMaker event-stream decoding will be unavailable. Error: No module named 'botocore'
/Users/ohama/.local/share/uv/tools/openhands/lib/python3.12/site-packages/openhands/sdk/llm/auth/openai.py:25: AuthlibDeprecationWarning: authlib.jose module is deprecated, please use joserfc instead.
It will be compatible before version 2.0.0.
  from authlib.jose import JsonWebKey, jwt
+----------------------------------------------------------------------+
|  OpenHands SDK v1.21.0                                               |
|                                                                      |
|  Report a bug: github.com/OpenHands/software-agent-sdk/issues        |
|  Get help: openhands.dev/joinslack                                   |
|  Scale up: openhands.dev/product/sdk                                 |
|                                                                      |
|  Set OPENHANDS_SUPPRESS_BANNER=1 to hide this message                |
+----------------------------------------------------------------------+
    ... (excerpt trimmed) ...
│ Key-value store service implemented successfully. Created multi-module       │
│ package with kvstore/storage.py for persistence and cli.py for CLI commands. │
│ All 15 tests pass, verifying set, get, delete, list commands and persistence │
│ across process invocations.                                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
────────────────────────────────────────────────────────────────────────────────
Goodbye! 👋
Conversation ID: 8ed36bec9b45472e8de6febda1e4c1d5
Hint: run openhands --resume 8ed36bec-9b45-472e-8de6-febda1e4c1d5 to resume this
conversation.
```

---

_Generated by `benchmark/report.py` from the aggregated matrix metrics. Re-runnable and idempotent: same `results.json` → identical `RESULTS.md` (no agents or judges are re-run)._
