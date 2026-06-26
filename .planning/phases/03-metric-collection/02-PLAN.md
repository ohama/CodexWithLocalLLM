---
phase: 03-metric-collection
plan: 02
type: execute
wave: 2
depends_on: ["03-01"]
files_modified:
  - benchmark/score.py
  - benchmark/run.sh
autonomous: true

must_haves:
  truths:
    - "score.py extracts a step/tool-call count from the transcript using a TOOL-AWARE heuristic (codex exec-block style vs openhands agent-message style), and records the method used alongside the count."
    - "score.py records output size: number of files the agent produced and total lines of code, excluding transcript.log, meta.json, and __pycache__."
    - "All four metrics (passed, duration_seconds, steps, files+loc) land in ONE structured per-run record: the run dir's meta.json."
    - "run.sh automatically invokes the scorer after each run so a single run yields all four metrics with no manual step."
    - "Auto-scoring failure never aborts or fails the run; the run record is still written."
  artifacts:
    - path: "benchmark/score.py"
      provides: "MET-03 tool-aware step extraction + MET-04 file/LOC counting, merged into meta.json"
      contains: "step_method"
    - path: "benchmark/run.sh"
      provides: "Auto-invokes score.py on the run dir after meta.json is written"
      contains: "score.py"
  key_links:
    - from: "benchmark/score.py"
      to: "<run_dir>/transcript.log"
      via: "tool-aware parse: codex counts 'exec' blocks; openhands parses 'Number of agent messages' after stripping ANSI"
      pattern: "transcript\\.log"
    - from: "benchmark/run.sh"
      to: "benchmark/score.py"
      via: "python3 \"$HERE/score.py\" \"$RUN_DIR\" after section 10 (best-effort, set +e)"
      pattern: "score\\.py"
---

<objective>
Extend `benchmark/score.py` with the remaining two metrics and wire the scorer
into the runner so every run auto-produces a complete record:

- MET-03: step / tool-call count, extracted TOOL-AWARE from transcript.log. The
  two tools' transcripts differ (codex prints `exec` command blocks; openhands
  prints a `Number of agent messages: N` summary inside ANSI-colored output), so
  the extractor branches on `meta["tool"]`, records an approximate count, and
  also records the `step_method` it used so the heuristic is documented, not
  hidden.
- MET-04: output size — number of files the agent produced in the run dir and
  total lines of code, excluding the harness artifacts (transcript.log, meta.json)
  and __pycache__.
- Hook: `run.sh` invokes `score.py "$RUN_DIR"` after it writes meta.json, so a
  single `run.sh <tool> <level>` yields all four metrics. Scoring is best-effort
  and never aborts the run.

Purpose: Completes Phase 3 — every run now carries pass/fail, time, steps, and
size in one structured meta.json record.

Output: extended benchmark/score.py + benchmark/run.sh that auto-scores.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md

# Built in Plan 01 — extend this file:
@.planning/phases/03-metric-collection/03-01-SUMMARY.md
@benchmark/score.py

# The runner to hook into (add the scorer call after section 10):
@benchmark/run.sh

# REAL transcripts the step extractor MUST be designed against — formats differ:
#   codex: 'exec' on its own line, then the command, then ' succeeded in Nms:'
#   openhands: ANSI-colored; 'Number of agent messages: N' inside the summary block
@benchmark/.runs/codex-l1-fib-20260626-021103/transcript.log
@benchmark/.runs/openhands-l1-fib-20260626-021227/transcript.log
</context>

<tasks>

<task type="auto">
  <name>Task 1: MET-03 — tool-aware step/tool-call extraction</name>
  <files>benchmark/score.py</files>
  <action>
    Add step extraction to score_run, branching on `meta["tool"]`. Read
    `<run_dir>/transcript.log` (the filename is in `meta["transcript"]`; default
    "transcript.log"). Be tolerant if it is missing -> steps=0,
    step_method="transcript-missing".

    Design derived from the REAL sample transcripts (inspect them):

    - codex: each command execution is a line that is exactly `exec` followed by
      the command and a ` succeeded in `/` failed in ` line. Count tool calls as
      the number of `exec` markers: lines whose stripped value == "exec". In the
      L1 sample this yields 2 (the `cat > fib.py` heredoc and the `python3 fib.py`
      verification). Set step_method="codex:count of 'exec' blocks". (Optional,
      best-effort: you MAY also count ` failed in ` / `ERROR` lines as a
      self-correction sub-signal, but keep `steps` = the exec count.)

    - openhands: stdout is ANSI-colored. Strip escape codes first with
      `re.sub(r"\x1b\[[0-9;]*m", "", text)`, then find the line matching
      `Number of agent messages:\s*(\d+)` and use that integer as steps. In the
      L1 sample this yields 4. Set step_method="openhands:Number of agent
      messages". If the line is absent, steps=0,
      step_method="openhands:summary-not-found".

    Record `steps` (INT) and `step_method` (STR) into the meta dict. Keep the
    heuristic simple and documented — approximate is acceptable and expected per
    phase guidance; do NOT over-engineer a universal parser.
  </action>
  <verify>
    python3 benchmark/score.py benchmark/.runs/codex-l1-fib-20260626-021103 && python3 -c "import json;m=json.load(open('benchmark/.runs/codex-l1-fib-20260626-021103/meta.json'));assert m['steps']==2,m;assert 'exec' in m['step_method'];print('codex steps',m['steps'],m['step_method'])"
    python3 benchmark/score.py benchmark/.runs/openhands-l1-fib-20260626-021227 && python3 -c "import json;m=json.load(open('benchmark/.runs/openhands-l1-fib-20260626-021227/meta.json'));assert m['steps']==4,m;assert 'agent messages' in m['step_method'];print('openhands steps',m['steps'],m['step_method'])"
  </verify>
  <done>codex sample records steps=2 (exec blocks), openhands records steps=4 (agent messages), each with a documenting step_method; counts derived from the real transcripts.</done>
</task>

<task type="auto">
  <name>Task 2: MET-04 — output size (file count + LOC)</name>
  <files>benchmark/score.py</files>
  <action>
    Add output-size measurement to score_run. Walk the run dir and count only the
    files the AGENT produced — exclude the harness artifacts and caches:
    - exclude exact names: `transcript.log`, `meta.json`
    - exclude any path under a `__pycache__/` directory
    - exclude `.pyc` files

    Compute:
    - `files` (INT): number of produced files after exclusions (recurse with
      os.walk so multi-file L2/L3 solutions in subdirs like `kvstore/` are counted).
    - `loc` (INT): sum of line counts across those produced files. Count lines by
      reading each file as text (utf-8, errors="ignore") and counting newlines /
      splitlines(); skip unreadable/binary files gracefully (best-effort).

    Record `files` and `loc` into the meta dict. For the L1 samples this is
    files=1 (just fib.py) and loc≈30.
  </action>
  <verify>
    python3 benchmark/score.py benchmark/.runs/codex-l1-fib-20260626-021103 && python3 -c "import json;m=json.load(open('benchmark/.runs/codex-l1-fib-20260626-021103/meta.json'));assert m['files']==1,m;assert m['loc']>=20,m;print('codex files/loc',m['files'],m['loc'])"
    python3 benchmark/score.py benchmark/.runs/openhands-l1-fib-20260626-021227 && python3 -c "import json;m=json.load(open('benchmark/.runs/openhands-l1-fib-20260626-021227/meta.json'));assert m['files']==1,m;assert m['loc']>=20,m;print('openhands files/loc',m['files'],m['loc'])"
  </verify>
  <done>Both L1 samples record files=1 and loc>=20 (fib.py only); transcript.log, meta.json, and __pycache__ are excluded from the count.</done>
</task>

<task type="auto">
  <name>Task 3: Hook scorer into run.sh (auto-score every run, best-effort)</name>
  <files>benchmark/run.sh</files>
  <action>
    After section 10 (the heredoc that writes meta.json) and before the final
    summary (section 11), add a scoring step that extends that same meta.json with
    all four metrics so a single `run.sh` invocation yields the complete record:

    - Invoke `python3 "$HERE/score.py" "$RUN_DIR"`.
    - Wrap in `set +e` / capture exit / `set -e` (the script runs under
      `set -euo pipefail`). Scoring MUST be best-effort: a scorer error must NOT
      abort the run nor mask the run — print a warning and continue. The run
      record already exists; this only enriches it.
    - In the final summary (section 11), echo the four metrics by reading them
      back from meta.json (e.g. a small `python3 -c` that prints passed /
      duration_seconds / steps / files / loc), or print the scorer's stdout. Keep
      it informative but short.

    Do not change Phase 2 behavior: arg parsing, lock, isolation, tool invocation,
    and the meta.json fields from Phase 2 all stay intact. This is purely additive.
  </action>
  <verify>
    bash -n benchmark/run.sh   # syntax ok
    grep -q 'score.py' benchmark/run.sh && echo "scorer hooked"
    # Confirm the scorer call is positioned AFTER meta.json is written:
    python3 -c "s=open('benchmark/run.sh').read(); assert s.index('meta.json')<s.rindex('score.py'),'scorer must run after meta.json write'; print('order ok')"
  </verify>
  <done>run.sh syntax-checks clean and calls score.py "$RUN_DIR" after meta.json is written, guarded so scorer failure cannot abort the run.</done>
</task>

</tasks>

<verification>
Runnable on the EXISTING sample run dirs — no new agent/LLM run:

1. `python3 benchmark/score.py benchmark/.runs/codex-l1-fib-20260626-021103` and
   `...openhands-l1-fib-20260626-021227` both exit 0.
2. After scoring, EACH meta.json contains all four metrics in one record:
   - MET-01: passed (true), judge_exit (0)
   - MET-02: duration_seconds (43 / 49)
   - MET-03: steps (codex 2, openhands 4) + step_method documenting the heuristic
   - MET-04: files (1) + loc (>=20)
   - plus all original Phase 2 fields preserved.
3. Tool-awareness: codex steps come from `exec` blocks; openhands steps come from
   `Number of agent messages` (ANSI stripped) — verified by step_method values differing per tool.
4. Exclusion correctness: files==1 despite each run dir also containing
   transcript.log, meta.json, and a __pycache__/ dir.
5. `bash -n benchmark/run.sh` passes; `grep score.py benchmark/run.sh` matches;
   scorer call is positioned after the meta.json write and is failure-isolated.
6. Idempotency: re-running score.py yields identical metric values.
</verification>

<success_criteria>
- MET-03 + MET-04 implemented in score.py, tool-aware step heuristic documented via step_method.
- All four metrics land in one structured per-run record (meta.json).
- run.sh auto-invokes the scorer after writing meta.json; scorer failure cannot abort a run.
- Verified on both existing sample dirs with zero new LLM time.
- No Phase 4/5 scope (no matrix run, no report table, no repro doc).
</success_criteria>

<output>
After completion, create `.planning/phases/03-metric-collection/03-02-SUMMARY.md`.
</output>
