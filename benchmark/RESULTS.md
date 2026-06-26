# Benchmark Results — codex vs openhands (qwen-122b)

- **Source:** `benchmark/.runs/results-14.json`
- **Matrix timestamp:** .runs
- **Model(s):** codex → `qwen-122b-codex`, openhands → `openai/qwen-122b`
  - Both are the same local **qwen-122b** family served at `http://localhost:4000/v1`; the two tools merely report the model string differently (codex: `qwen-122b-codex`, openhands: `openai/qwen-122b`).
- **Cells:** 14 (2 tools × 7 levels)

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
| codex | l4-calc | PASS | 88s | 13 (codex:count of 'exec' blocks) | 1f / 187loc |
| openhands | l4-calc | PASS | 120s | 13 (openhands:Number of agent messages) | 1f / 200loc |
| codex | l5-todo | PASS | 101s | 5 (codex:count of 'exec' blocks) | 8f / 341loc |
| openhands | l5-todo | PASS | 159s | 14 (openhands:Number of agent messages) | 3f / 341loc |
| codex | l6-csvstat | PASS | 142s | 12 (codex:count of 'exec' blocks) | 5f / 490loc |
| openhands | l6-csvstat | PASS | 173s | 18 (openhands:Number of agent messages) | 5f / 345loc |
| codex | l7-kvapi | FAIL | 33s | 2 (codex:count of 'exec' blocks) | 0f / 0loc |
| openhands | l7-kvapi | PASS | 190s | 0 (openhands:summary-not-found) | 9f / 516loc |

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

### l4-calc

- **Time:** codex 88s vs openhands 120s (Δ +32s; **codex** faster).
- **Process (units differ — not directly comparable):** codex 13 (codex:count of 'exec' blocks) vs openhands 13 (openhands:Number of agent messages).
- **Output:** codex 1f/187loc vs openhands 1f/200loc (Δ +0f / +13loc).
- **Verdict:** codex **PASS**, openhands **PASS**.

### l5-todo

- **Time:** codex 101s vs openhands 159s (Δ +58s; **codex** faster).
- **Process (units differ — not directly comparable):** codex 5 (codex:count of 'exec' blocks) vs openhands 14 (openhands:Number of agent messages).
- **Output:** codex 8f/341loc vs openhands 3f/341loc (Δ -5f / +0loc).
- **Verdict:** codex **PASS**, openhands **PASS**.

### l6-csvstat

- **Time:** codex 142s vs openhands 173s (Δ +31s; **codex** faster).
- **Process (units differ — not directly comparable):** codex 12 (codex:count of 'exec' blocks) vs openhands 18 (openhands:Number of agent messages).
- **Output:** codex 5f/490loc vs openhands 5f/345loc (Δ +0f / -145loc).
- **Verdict:** codex **PASS**, openhands **PASS**.

### l7-kvapi

- **Time:** codex 33s vs openhands 190s (Δ +157s; **codex** faster).
- **Process (units differ — not directly comparable):** codex 2 (codex:count of 'exec' blocks) vs openhands 0 (openhands:summary-not-found).
- **Output:** codex 0f/0loc vs openhands 9f/516loc (Δ +9f / +516loc).
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

### codex / l4-calc — PASS in 88s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/codex-l4-calc-20260626-074443/transcript.log`
- **Steps:** 13 (codex:count of 'exec' blocks) · **Size:** 1f / 187loc

```text
Reading additional input from stdin...
OpenAI Codex v0.142.0
--------
workdir: /Users/ohama/projs/codex/benchmark/.runs/codex-l4-calc-20260626-074443
model: qwen-122b-codex
provider: litellm
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: none
reasoning summaries: none
session id: 019f02e3-61c6-7f20-96e9-18b7fa7c5a03
--------
user
# L4 — Arithmetic expression evaluator CLI (single-file, algorithmic)
    ... (excerpt trimmed) ...
tokens used
225,704
All tests pass. The `calc.py` implementation is complete with:
- **Proper operator precedence**: `*` and `/` bind tighter than `+` and `-`
- **Left-associativity**: `7 - 2 - 1 = 4` (correctly evaluates as `(7 - 2) - 1`)
- **Parentheses support**: `(2 + 3) * 4 = 20`
- **Unary minus**: `-3 + 5 = 2`, `2 * -4 = -8`
- **Float division**: `10 / 4 = 2.5`
- **Output formatting**: Integral results show as integers (`6`), non-integral as floats (`3.333...`)
- **Error handling**: Invalid expressions and division by zero exit with nonzero status
```

### openhands / l4-calc — PASS in 120s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/openhands-l4-calc-20260626-075602/transcript.log`
- **Steps:** 13 (openhands:Number of agent messages) · **Size:** 1f / 200loc

```text
16:56:03 - LiteLLM:WARNING: common_utils.py:979 - litellm: could not pre-load bedrock-runtime response stream shape — Bedrock event-stream decoding will be unavailable. Error: No module named 'botocore'
16:56:03 - LiteLLM:WARNING: common_utils.py:24 - litellm: could not pre-load sagemaker-runtime response stream shape — SageMaker event-stream decoding will be unavailable. Error: No module named 'botocore'
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
│ correct output formatting. All test cases pass: basic precedence (2+3*4=14), │
│ parentheses ((2+3)*4=20), division (10/4=2.5), unary minus (-3+5=2),         │
│ left-associativity (7-2-1=4), and error handling for malformed expressions   │
│ and division by zero.                                                        │
╰──────────────────────────────────────────────────────────────────────────────╯
────────────────────────────────────────────────────────────────────────────────
Goodbye! 👋
Conversation ID: 1682c0105e6449d1aff75d6030b5a9bc
Hint: run openhands --resume 1682c010-5e64-49d1-aff7-5d6030b5a9bc to resume this
conversation.
```

### codex / l5-todo — PASS in 101s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/codex-l5-todo-20260626-074612/transcript.log`
- **Steps:** 5 (codex:count of 'exec' blocks) · **Size:** 8f / 341loc

```text
Reading additional input from stdin...
OpenAI Codex v0.142.0
--------
workdir: /Users/ohama/projs/codex/benchmark/.runs/codex-l5-todo-20260626-074612
model: qwen-122b-codex
provider: litellm
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: none
reasoning summaries: none
session id: 019f02e4-ba92-7151-990e-35dd9fb68aca
--------
user
# L5 — Todo manager CLI (multi-file, subcommands + persistence)
    ... (excerpt trimmed) ...
$ python3 todo.py list
1 [x] buy milk
2 [ ] write report
$ python3 todo.py rm 1
$ python3 todo.py list
2 [ ] write report
$ python3 todo.py done 99
$ echo $?
1
```
```

### openhands / l5-todo — PASS in 159s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/openhands-l5-todo-20260626-075802/transcript.log`
- **Steps:** 14 (openhands:Number of agent messages) · **Size:** 3f / 341loc

```text
16:58:03 - LiteLLM:WARNING: common_utils.py:979 - litellm: could not pre-load bedrock-runtime response stream shape — Bedrock event-stream decoding will be unavailable. Error: No module named 'botocore'
16:58:03 - LiteLLM:WARNING: common_utils.py:24 - litellm: could not pre-load sagemaker-runtime response stream shape — SageMaker event-stream decoding will be unavailable. Error: No module named 'botocore'
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
│ - Proper exit codes (0 for success, nonzero for failures)                    │
│ - Correct output format: `<id> [ ]/<x] <text>`                               │
│ - Persistence via TODO_PATH env var or ./todos.json                          │
│ - Standard library only (json, os, argparse, subprocess)                     │
╰──────────────────────────────────────────────────────────────────────────────╯
────────────────────────────────────────────────────────────────────────────────
Goodbye! 👋
Conversation ID: 6a635549143d421297fcc469aaf653dd
Hint: run openhands --resume 6a635549-143d-4212-97fc-c469aaf653dd to resume this
conversation.
```

### codex / l6-csvstat — PASS in 142s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/codex-l6-csvstat-20260626-074754/transcript.log`
- **Steps:** 12 (codex:count of 'exec' blocks) · **Size:** 5f / 490loc

```text
Reading additional input from stdin...
OpenAI Codex v0.142.0
--------
workdir: /Users/ohama/projs/codex/benchmark/.runs/codex-l6-csvstat-20260626-074754
model: qwen-122b-codex
provider: litellm
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: none
reasoning summaries: none
session id: 019f02e6-4922-7042-9f60-0434241f5c85
--------
user
# L6 — CSV column statistics CLI (multi-module, data processing)
    ... (excerpt trimmed) ...
- `csvstat.py` - CLI entry point at project root
- `csvstat/__init__.py` - Package initialization with exports
- `csvstat/stats.py` - Core numeric column statistics logic
- `test_csvstat.py` - Comprehensive test suite (17 tests)
**Features:**
- `--cols` - Lists all column names in header order
- `--col <name>` - Computes count, min, max, sum, mean for a numeric column
- Proper error handling for missing files, missing columns, and non-numeric data
- Number formatting that omits decimal points for integral values
**All tests pass** (17/17), including CLI integration tests and unit tests for the stats module.
```

### openhands / l6-csvstat — PASS in 173s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/openhands-l6-csvstat-20260626-080041/transcript.log`
- **Steps:** 18 (openhands:Number of agent messages) · **Size:** 5f / 345loc

```text
17:00:42 - LiteLLM:WARNING: common_utils.py:979 - litellm: could not pre-load bedrock-runtime response stream shape — Bedrock event-stream decoding will be unavailable. Error: No module named 'botocore'
17:00:42 - LiteLLM:WARNING: common_utils.py:24 - litellm: could not pre-load sagemaker-runtime response stream shape — SageMaker event-stream decoding will be unavailable. Error: No module named 'botocore'
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
│ CSV Statistics CLI completed successfully. Created multi-module project with │
│ csvstat.py entry point, csvstat/ package (stats.py for numeric logic), and   │
│ comprehensive test suite. All 13 tests pass and CLI matches the contract     │
│ specification.                                                               │
╰──────────────────────────────────────────────────────────────────────────────╯
────────────────────────────────────────────────────────────────────────────────
Goodbye! 👋
Conversation ID: a299387578c74d49aa4efd8d5212f7fe
Hint: run openhands --resume a2993875-78c7-4d49-aa4e-fd8d5212f7fe to resume this
conversation.
```

### codex / l7-kvapi — FAIL in 33s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/codex-l7-kvapi-20260626-084425/transcript.log`
- **Steps:** 2 (codex:count of 'exec' blocks) · **Size:** 0f / 0loc

```text
Reading additional input from stdin...
OpenAI Codex v0.142.0
--------
workdir: /Users/ohama/projs/codex/benchmark/.runs/codex-l7-kvapi-20260626-084425
model: qwen-122b-codex
provider: litellm
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: none
reasoning summaries: none
session id: 019f031a-0a0f-7ac1-ab00-bf11778823b3
--------
user
# L7 — HTTP key-value API service (multi-module, server + persistence + restart)
    ... (excerpt trimmed) ...
  • Write tests for the service
  • Verify implementation works correctly
codex
exec
/bin/zsh -lc 'mkdir -p kvapi' in /Users/ohama/projs/codex/benchmark/.runs/codex-l7-kvapi-20260626-084425
 succeeded in 0ms:
codex
tokens used
49,517
I'll build an HTTP key-value REST service in Python with persistence. Let me start by exploring the current directory structure and then create the implementation.
```

### openhands / l7-kvapi — PASS in 190s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/openhands-l7-kvapi-20260626-084458/transcript.log`
- **Steps:** 0 (openhands:summary-not-found) · **Size:** 9f / 516loc

```text
17:44:58 - LiteLLM:WARNING: common_utils.py:979 - litellm: could not pre-load bedrock-runtime response stream shape — Bedrock event-stream decoding will be unavailable. Error: No module named 'botocore'
17:44:58 - LiteLLM:WARNING: common_utils.py:24 - litellm: could not pre-load sagemaker-runtime response stream shape — SageMaker event-stream decoding will be unavailable. Error: No module named 'botocore'
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
```

---

_Generated by `benchmark/report.py` from the aggregated matrix metrics. Re-runnable and idempotent: same `results.json` → identical `RESULTS.md` (no agents or judges are re-run)._
