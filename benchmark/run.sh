#!/usr/bin/env bash
# Equal-conditions benchmark runner.
#   benchmark/run.sh <tool> <level>
#
# <tool>  : codex | openhands
# <level> : l1 | l1-fib | 1        (fib)
#           l2 | l2-wordstat | 2   (wordstat)
#           l3 | l3-kvstore | 3    (kvstore)
#           l4 | l4-calc | 4       (calc)
#           l5 | l5-todo | 5       (todo)
#           l6 | l6-csvstat | 6    (csvstat)
#           l7 | l7-kvapi | 7      (kvapi — HTTP service)
#
# Drives one tool over one frozen task PROMPT.md under identical conditions,
# in a fresh isolated work dir. Tool invocation is stubbed in this plan (Plan 01)
# and wired for real in Plan 02.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
export LITELLM_API_KEY="${LITELLM_API_KEY:-dummy}"

usage() {
  cat >&2 <<EOF
usage: run.sh <tool> <level>
  <tool>  codex | openhands
  <level> l1|1 .. l7|7  (fib/wordstat/kvstore/calc/todo/csvstat/kvapi)
EOF
  exit 2
}

# ── 1. Argument validation ──────────────────────────────────────────────
[ "$#" -eq 2 ] || usage
TOOL="$1"
LEVEL_ARG="$2"

case "$TOOL" in
  codex|openhands|qclaude|qclaude35) ;;
  *) echo "✗ unknown tool: '$TOOL' (expected codex|openhands|qclaude|qclaude35)" >&2; usage ;;
esac

# ── 2. Level normalization ──────────────────────────────────────────────
# Map any accepted alias to a short key, then glob the real dir so a renamed
# suffix (e.g. l1-fib2) still resolves.
case "$LEVEL_ARG" in
  l1|l1-fib|1) SHORT="l1" ;;
  l2|l2-wordstat|2) SHORT="l2" ;;
  l3|l3-kvstore|3) SHORT="l3" ;;
  l4|l4-calc|4) SHORT="l4" ;;
  l5|l5-todo|5) SHORT="l5" ;;
  l6|l6-csvstat|6) SHORT="l6" ;;
  l7|l7-kvapi|7) SHORT="l7" ;;
  *) echo "✗ unknown level: '$LEVEL_ARG'" >&2; usage ;;
esac

LEVEL_DIRS=( "$HERE"/tasks/"$SHORT"-* )
if [ ! -d "${LEVEL_DIRS[0]}" ]; then
  echo "✗ no task dir matching tasks/$SHORT-* under $HERE" >&2
  exit 1
fi
LEVEL_DIR="${LEVEL_DIRS[0]}"
LEVEL="$(basename "$LEVEL_DIR")"

# ── 3. Resolve & read the canonical PROMPT.md verbatim ──────────────────
PROMPT_FILE="$LEVEL_DIR/PROMPT.md"
if [ ! -f "$PROMPT_FILE" ]; then
  echo "✗ missing prompt: $PROMPT_FILE" >&2
  exit 1
fi
# Read verbatim so Plan 02 can feed it to the tool unchanged.
PROMPT="$(cat "$PROMPT_FILE")"

# ── 4. Serial run-lock (RUN-05) ─────────────────────────────────────────
# Single mlx backend must never be hit by two runs at once. macOS base has no
# flock, so use a mkdir-based atomic mutex: mkdir succeeds for exactly one proc.
mkdir -p "$HERE/.runs"
LOCK="$HERE/.runs/.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "✗ another run holds the lock (single backend, serial only)" >&2
  exit 3
fi
# CRITICAL: install the cleanup trap ONLY AFTER acquiring the lock. If set
# earlier, a losing invocation (lock already held) would delete the holder's
# lock on exit and break the serial guarantee.
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

# ── 5. LiteLLM gateway preflight (supports RUN-03) ──────────────────────
# Abort early — before creating a run dir or invoking a tool — if backend down.
if ! curl -sf -m 5 http://localhost:4000/v1/models \
      -H "Authorization: Bearer $LITELLM_API_KEY" >/dev/null 2>&1; then
  echo "✗ LiteLLM gateway (:4000) not responding — check the LiteLLM/mlx service" >&2
  exit 1
fi
# qclaude* additionally goes through claude-code-proxy (:8082); fail early if down.
if [ "$TOOL" = "qclaude" ] || [ "$TOOL" = "qclaude35" ]; then
  if ! curl -sf -m 5 http://localhost:8082/ >/dev/null 2>&1; then
    echo "✗ claude-code-proxy (:8082) not responding — check com.ohama.claude-proxy" >&2
    exit 1
  fi
fi

# ── 6. Fresh isolated run dir ───────────────────────────────────────────
STAMP="$(date -u +%Y%m%d-%H%M%S)"
RUN_DIR="$HERE/.runs/$TOOL-$LEVEL-$STAMP"
# Guard against two runs landing in the same UTC second.
if [ -e "$RUN_DIR" ]; then
  RUN_DIR="$RUN_DIR-$RANDOM"
fi
mkdir -p "$RUN_DIR"

# ── 7. Tool invocation (wired in Plan 02) ───────────────────────────────
# Both runners: cd into the isolated RUN_DIR, feed the verbatim PROMPT, tee
# combined stdout+stderr to transcript.log, and record the REAL tool exit code
# via ${PIPESTATUS[0]} (tee would otherwise mask it under `set -o pipefail`).
# A nonzero agent exit is still a valid recorded run (pass/fail judging is
# Phase 3), so we never abort the script on it — we record the code and finalize.
TOOL_EXIT=0

run_codex() {
  cd "$RUN_DIR"
  # `< /dev/null` is MANDATORY: without it `codex exec` hangs on stdin in a
  # non-tty/background context. --sandbox workspace-write lets codex write its
  # solution into the cwd (== RUN_DIR, the isolated dir).
  set +e
  LITELLM_API_KEY=dummy codex exec --skip-git-repo-check --sandbox workspace-write "$PROMPT" < /dev/null 2>&1 | tee "$RUN_DIR/transcript.log"
  TOOL_EXIT="${PIPESTATUS[0]}"   # codex's real exit, not tee's
  set -e
}

run_qclaude() {
  cd "$RUN_DIR"
  # Claude Code (local qwen via claude-code-proxy :8082). The tier flag picks the
  # backend via the proxy's tier mapping (proxy.env):
  #   qclaude   → --model opus   → qwen-122b-claude (122b, == the weights codex ran)
  #   qclaude35 → --model sonnet → qwen-35b-claude  (35b, the fast tier)
  # CLAUDE_TIER is set by the dispatcher below.
  # --dangerously-skip-permissions: headless tool use (Write/Bash) with no prompts,
  # matching codex --sandbox workspace-write / openhands --always-approve.
  # --output-format stream-json --verbose: emit per-event JSONL so score.py can
  # count tool_use events (the codex/openhands transcripts don't apply here).
  # `< /dev/null` for the same non-tty safety as the others. The FULL path to
  # claude is MANDATORY (a bare `claude` re-expands via the user's tmux wrapper).
  set +e
  ANTHROPIC_BASE_URL=http://localhost:8082 ANTHROPIC_AUTH_TOKEN=dummy \
    /opt/homebrew/bin/claude -p "$PROMPT" --model "$CLAUDE_TIER" \
    --dangerously-skip-permissions \
    --output-format stream-json --verbose \
    < /dev/null 2>&1 | tee "$RUN_DIR/transcript.log"
  TOOL_EXIT="${PIPESTATUS[0]}"   # claude's real exit, not tee's
  set -e
}

run_openhands() {
  cd "$RUN_DIR"
  # Workspace pin (PROACTIVE, by default): this OpenHands (CLI 1.16.0 / SDK
  # 1.21.0) resolves its agent workspace via get_work_dir() =
  # os.environ.get("OPENHANDS_WORK_DIR", os.getcwd()) — NOT from SANDBOX_VOLUMES/
  # WORKSPACE_BASE (those belong to the older docker app). So we pin the
  # workspace to the isolated RUN_DIR via OPENHANDS_WORK_DIR on EVERY run; the
  # solution always lands here, never in a shared/global workspace (RUN-02).
  export OPENHANDS_WORK_DIR="$RUN_DIR"
  # Same-model pin (RUN-03): --override-with-envs makes OpenHands take the LLM
  # from these env vars (it also REQUIRES LLM_API_KEY + LLM_MODEL when enabled),
  # so the model is enforced from the runner, independent of config drift.
  # MODEL is resolved (from agent_settings.json) before dispatch in section 8.
  export LLM_API_KEY=dummy
  export LLM_BASE_URL="http://localhost:4000/v1"
  export LLM_MODEL="$MODEL"
  # Feed the prompt verbatim via --task (inline text), NOT --file. With --file
  # pointing at the canonical tasks/<level>/PROMPT.md, OpenHands anchored its
  # working directory to that file's dir and wrote the solution into the canonical
  # task folder (RUN-02 leak observed on L2/L3 in the Phase 4 matrix), leaving the
  # isolated RUN_DIR empty. Inline --task removes the file-path anchor, so writes
  # land in OPENHANDS_WORK_DIR=RUN_DIR (same inline approach codex uses).
  # --headless runs non-interactively and auto-approves actions; --always-approve
  # / --exit-without-confirmation never block for human confirmation.
  # `< /dev/null` for the same non-tty safety as codex.
  set +e
  LITELLM_API_KEY=dummy openhands --task "$PROMPT" --headless \
    --always-approve --exit-without-confirmation --override-with-envs \
    < /dev/null 2>&1 | tee "$RUN_DIR/transcript.log"
  TOOL_EXIT="${PIPESTATUS[0]}"   # openhands's real exit, not tee's
  set -e
}

# ── 8. Resolve model from the tool's own config (single source of truth) ─
# meta.json is the authoritative same-model record (RUN-03): it must name the
# qwen-122b-family model WITHOUT rerunning anything. Resolve per tool:
#   codex     -> `model = "..."` line in ~/.codex/config.toml
#   openhands -> .llm.model in ~/.openhands/agent_settings.json
# stdlib only (grep/sed for toml, python3 json for json) — no new deps.
resolve_model() {
  case "$TOOL" in
    codex)
      MODEL="$(grep -E '^[[:space:]]*model[[:space:]]*=' "$HOME/.codex/config.toml" \
                 | head -1 | sed -E 's/.*=[[:space:]]*"([^"]+)".*/\1/')"
      ;;
    openhands)
      MODEL="$(python3 -c "import json;print(json.load(open('$HOME/.openhands/agent_settings.json'))['llm']['model'])")"
      ;;
    qclaude)
      # claude-code-proxy maps the opus tier to qwen-122b-claude (proxy.env), the
      # same 122b weights codex used. No per-run config to read — it's the fixed
      # proxy routing for --model opus.
      CLAUDE_TIER="opus"
      MODEL="qwen-122b-claude"
      ;;
    qclaude35)
      # The sonnet tier maps to qwen-35b-claude (proxy.env) — the fast 35b model.
      CLAUDE_TIER="sonnet"
      MODEL="qwen-35b-claude"
      ;;
  esac
  [ -n "${MODEL:-}" ] || MODEL="unknown"
  # Same-model assertion (RUN-03): both tools must run the qwen-122b backend.
  case "$MODEL" in
    *qwen-122b*) ;;
    *) echo "⚠ resolved model '$MODEL' is not in the qwen-122b family (same-model criterion)" >&2 ;;
  esac
}
resolve_model

# ── 9. Start summary + dispatch ─────────────────────────────────────────
echo "tool        : $TOOL"
echo "level       : $LEVEL"
echo "model       : $MODEL"
echo "run dir     : $RUN_DIR"
echo "prompt file : $PROMPT_FILE"

# Record-only provenance timestamps (UTC ISO). NOT metrics — wall-clock
# measurement/aggregation is Phase 3. These only stamp when the run happened.
STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
case "$TOOL" in
  codex)               run_codex ;;
  openhands)           run_openhands ;;
  qclaude|qclaude35)   run_qclaude ;;
esac
FINISHED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# ── 10. Self-describing run record (meta.json) ──────────────────────────
# Written even on a nonzero agent exit (recording a failed run is valid).
cat > "$RUN_DIR/meta.json" <<EOF
{
  "tool": "$TOOL",
  "level": "$LEVEL",
  "model": "$MODEL",
  "base_url": "http://localhost:4000/v1",
  "prompt_file": "$PROMPT_FILE",
  "run_dir": "$RUN_DIR",
  "started_at": "$STARTED_AT",
  "finished_at": "$FINISHED_AT",
  "exit_code": $TOOL_EXIT,
  "transcript": "transcript.log"
}
EOF

# ── 10b. Auto-score (Phase 3) — enrich meta.json with all four metrics ───
# Runs AFTER meta.json is written; extends that same record in place with
# passed/duration_seconds/steps/files/loc. BEST-EFFORT: the script runs under
# `set -euo pipefail`, so guard with `set +e` — a scorer hiccup must NEVER abort
# or mask the run. The run record already exists; this only enriches it.
set +e
python3 "$HERE/score.py" "$RUN_DIR"
SCORE_EXIT=$?
set -e
if [ "$SCORE_EXIT" -ne 0 ]; then
  echo "⚠ scorer failed (exit $SCORE_EXIT) — run record kept, metrics may be incomplete" >&2
fi

# ── 11. Final summary ───────────────────────────────────────────────────
echo "──────── run complete ────────"
echo "run dir    : $RUN_DIR"
echo "transcript : $RUN_DIR/transcript.log"
echo "meta       : $RUN_DIR/meta.json"
echo "model      : $MODEL"
echo "exit code  : $TOOL_EXIT"
# Echo the four metrics back from meta.json (best-effort; never fails the run).
set +e
python3 -c "
import json,sys
m=json.load(open('$RUN_DIR/meta.json'))
print('passed     :', m.get('passed'))
print('duration   :', m.get('duration_seconds'), 's')
print('steps      :', m.get('steps'), '(', m.get('step_method'), ')')
print('output     :', m.get('files'), 'files /', m.get('loc'), 'loc')
" 2>/dev/null
set -e
