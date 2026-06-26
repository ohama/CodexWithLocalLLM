# Benchmark Results — codex vs openhands (qwen-122b)

- **Source:** `benchmark/.runs/matrix-20260626-042701/results.json`
- **Matrix timestamp:** 20260626-042701
- **Model(s):** codex → `qwen-122b-codex`, openhands → `openai/qwen-122b`
  - Both are the same local **qwen-122b** family served at `http://localhost:4000/v1`; the two tools merely report the model string differently (codex: `qwen-122b-codex`, openhands: `openai/qwen-122b`).
- **Cells:** 6 (2 tools × 3 levels)

> This report is the **durable** record. `benchmark/.runs/` is gitignored, so the raw run directories are not committed — the metrics table and transcript excerpts below bake the evidence into version control (REP-02 + REP-03).

## Results matrix (REP-02)

| Tool | Level | Success | Time | Steps (step_method) | Size (files / loc) |
|------|-------|---------|------|---------------------|--------------------|
| codex | l1-fib | PASS | 26s | 2 (codex:count of 'exec' blocks) | 1f / 31loc |
| openhands | l1-fib | PASS | 49s | 4 (openhands:Number of agent messages) | 1f / 31loc |
| codex | l2-wordstat | PASS | 98s | 10 (codex:count of 'exec' blocks) | 4f / 148loc |
| openhands | l2-wordstat | PASS | 145s | 16 (openhands:Number of agent messages) | 4f / 222loc |
| codex | l3-kvstore | FAIL | 14s | 2 (codex:count of 'exec' blocks) | 0f / 0loc |
| openhands | l3-kvstore | PASS | 147s | 15 (openhands:Number of agent messages) | 9f / 362loc |

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

- **Time:** codex 26s vs openhands 49s (Δ +23s; **codex** faster).
- **Process (units differ — not directly comparable):** codex 2 (codex:count of 'exec' blocks) vs openhands 4 (openhands:Number of agent messages).
- **Output:** codex 1f/31loc vs openhands 1f/31loc (Δ +0f / +0loc).
- **Verdict:** codex **PASS**, openhands **PASS**.

### l2-wordstat

- **Time:** codex 98s vs openhands 145s (Δ +47s; **codex** faster).
- **Process (units differ — not directly comparable):** codex 10 (codex:count of 'exec' blocks) vs openhands 16 (openhands:Number of agent messages).
- **Output:** codex 4f/148loc vs openhands 4f/222loc (Δ +0f / +74loc).
- **Verdict:** codex **PASS**, openhands **PASS**.

### l3-kvstore

- **Time:** codex 14s vs openhands 147s (Δ +133s; **codex** faster).
- **Process (units differ — not directly comparable):** codex 2 (codex:count of 'exec' blocks) vs openhands 15 (openhands:Number of agent messages).
- **Output:** codex 0f/0loc vs openhands 9f/362loc (Δ +9f / +362loc).
- **Verdict:** codex **FAIL**, openhands **PASS**.

## Transcript references & evidence excerpts (REP-03)

Each run's transcript path and a short ANSI-stripped excerpt are embedded below so the evidence survives in the committed report even though `benchmark/.runs/` is gitignored.

### codex / l1-fib — PASS in 26s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/codex-l1-fib-20260626-042701/transcript.log`
- **Steps:** 2 (codex:count of 'exec' blocks) · **Size:** 1f / 31loc

```text
Reading additional input from stdin...
OpenAI Codex v0.142.0
--------
workdir: /Users/ohama/projs/codex/benchmark/.runs/codex-l1-fib-20260626-042701
model: qwen-122b-codex
provider: litellm
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: none
reasoning summaries: none
session id: 019f022e-60da-7550-afb5-6fb336d4a8f0
--------
user
# L1 — Fibonacci (single file)
    ... (excerpt trimmed) ...
tokens used
49,021
The `fib.py` file has been created successfully at the project root. It contains:
- A `fib(n: int) -> int` function using an iterative approach (standard library only)
- All required Fibonacci values verified via assertions
- The script runs cleanly with `python3 fib.py` and exits with code 0
All contract requirements are satisfied:
- `fib(0) == 0`, `fib(1) == 1`, `fib(2) == 1`, `fib(3) == 2`, `fib(5) == 5`, `fib(10) == 55`, `fib(20) == 6765`, `fib(30) == 832040`
- Returns `int` type
- No non-stdlib imports
```

### openhands / l1-fib — PASS in 49s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/openhands-l1-fib-20260626-042920/transcript.log`
- **Steps:** 4 (openhands:Number of agent messages) · **Size:** 1f / 31loc

```text
13:29:21 - LiteLLM:WARNING: common_utils.py:979 - litellm: could not pre-load bedrock-runtime response stream shape — Bedrock event-stream decoding will be unavailable. Error: No module named 'botocore'
13:29:21 - LiteLLM:WARNING: common_utils.py:24 - litellm: could not pre-load sagemaker-runtime response stream shape — SageMaker event-stream decoding will be unavailable. Error: No module named 'botocore'
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
│ Finish with message:                                                         │
│ Created fib.py with a working Fibonacci implementation. All 8 contract tests │
│ pass (fib(0)=0, fib(1)=1, fib(2)=1, fib(3)=2, fib(5)=5, fib(10)=55,          │
│ fib(20)=6765, fib(30)=832040). The script runs cleanly with exit code 0.     │
╰──────────────────────────────────────────────────────────────────────────────╯
────────────────────────────────────────────────────────────────────────────────
Goodbye! 👋
Conversation ID: caba0d5220fa4302a3cc4ad5fcaf61da
Hint: run openhands --resume caba0d52-20fa-4302-a3cc-4ad5fcaf61da to resume this
conversation.
```

### codex / l2-wordstat — PASS in 98s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/codex-l2-wordstat-20260626-042728/transcript.log`
- **Steps:** 10 (codex:count of 'exec' blocks) · **Size:** 4f / 148loc

```text
Reading additional input from stdin...
OpenAI Codex v0.142.0
--------
workdir: /Users/ohama/projs/codex/benchmark/.runs/codex-l2-wordstat-20260626-042728
model: qwen-122b-codex
provider: litellm
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: none
reasoning summaries: none
session id: 019f022e-c82e-7462-9b21-f52474d5e018
--------
user
# L2 — Word statistics CLI (multi-file)
    ... (excerpt trimmed) ...
dog 2
fox 2
hello 2
testing 2
```
**Key implementation details:**
- Tokenization uses regex `[A-Za-z0-9]+` to extract maximal runs of ASCII alphanumerics, lowercased
- Tie-breaking for top words: count descending, then word ascending (alphabetically)
- All 14 tests pass
- Exit code 0 on success
```

### openhands / l2-wordstat — PASS in 145s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/openhands-l2-wordstat-20260626-044118/transcript.log`
- **Steps:** 16 (openhands:Number of agent messages) · **Size:** 4f / 222loc

```text
13:41:19 - LiteLLM:WARNING: common_utils.py:979 - litellm: could not pre-load bedrock-runtime response stream shape — Bedrock event-stream decoding will be unavailable. Error: No module named 'botocore'
13:41:19 - LiteLLM:WARNING: common_utils.py:24 - litellm: could not pre-load sagemaker-runtime response stream shape — SageMaker event-stream decoding will be unavailable. Error: No module named 'botocore'
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
│ test input, and test_wordstat.py with 16 passing unit tests. The CLI         │
│ correctly tokenizes words as ASCII alphanumerics (case-insensitive), outputs │
│ total/unique counts and top 5 words sorted by frequency descending then word │
│ ascending, and exits with code 0 on success.                                 │
╰──────────────────────────────────────────────────────────────────────────────╯
────────────────────────────────────────────────────────────────────────────────
Goodbye! 👋
Conversation ID: 857ef5c33680485f9f8bfd3385c1d9ea
Hint: run openhands --resume 857ef5c3-3680-485f-9f8b-fd3385c1d9ea to resume this
conversation.
```

### codex / l3-kvstore — FAIL in 14s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/codex-l3-kvstore-20260626-042906/transcript.log`
- **Steps:** 2 (codex:count of 'exec' blocks) · **Size:** 0f / 0loc

```text
Reading additional input from stdin...
OpenAI Codex v0.142.0
--------
workdir: /Users/ohama/projs/codex/benchmark/.runs/codex-l3-kvstore-20260626-042906
model: qwen-122b-codex
provider: litellm
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: none
reasoning summaries: none
session id: 019f0230-4965-7842-b9a7-bfd33c8d841d
--------
user
# L3 — Key-value store service (multi-module)
    ... (excerpt trimmed) ...
  • Verify CLI contract with manual testing
codex
Now I'll create the kvstore package with the storage module:
exec
/bin/zsh -lc 'mkdir -p kvstore' in /Users/ohama/projs/codex/benchmark/.runs/codex-l3-kvstore-20260626-042906
 succeeded in 0ms:
codex
tokens used
48,823
Now I'll create the kvstore package with the storage module:
```

### openhands / l3-kvstore — PASS in 147s

- **Transcript:** `/Users/ohama/projs/codex/benchmark/.runs/openhands-l3-kvstore-20260626-044445/transcript.log`
- **Steps:** 15 (openhands:Number of agent messages) · **Size:** 9f / 362loc

```text
13:44:45 - LiteLLM:WARNING: common_utils.py:979 - litellm: could not pre-load bedrock-runtime response stream shape — Bedrock event-stream decoding will be unavailable. Error: No module named 'botocore'
13:44:45 - LiteLLM:WARNING: common_utils.py:24 - litellm: could not pre-load sagemaker-runtime response stream shape — SageMaker event-stream decoding will be unavailable. Error: No module named 'botocore'
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
│ - CLI commands: `set`, `get`, `delete`, `list` with correct exit codes   │
│ - All 15 tests pass, verifying CLI contract and persistence behavior     │
│                                                                          │
│ The service satisfies all requirements from the task specification.      │
╰──────────────────────────────────────────────────────────────────────────╯
────────────────────────────────────────────────────────────────────────────────
Goodbye! 👋
Conversation ID: a7d934ac3052422d855d5a0995b63e3d
Hint: run openhands --resume a7d934ac-3052-422d-855d-5a0995b63e3d to resume this
conversation.
```

---

_Generated by `benchmark/report.py` from the aggregated matrix metrics. Re-runnable and idempotent: same `results.json` → identical `RESULTS.md` (no agents or judges are re-run)._
