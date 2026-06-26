#!/usr/bin/env bash
# Equal-conditions benchmark runner.
#   benchmark/run.sh <tool> <level>
#
# <tool>  : codex | openhands
# <level> : l1 | l1-fib | 1   (fib)
#           l2 | l2-wordstat | 2  (wordstat)
#           l3 | l3-kvstore | 3   (kvstore)
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
  <level> l1|l1-fib|1  l2|l2-wordstat|2  l3|l3-kvstore|3
EOF
  exit 2
}

# ── 1. Argument validation ──────────────────────────────────────────────
[ "$#" -eq 2 ] || usage
TOOL="$1"
LEVEL_ARG="$2"

case "$TOOL" in
  codex|openhands) ;;
  *) echo "✗ unknown tool: '$TOOL' (expected codex|openhands)" >&2; usage ;;
esac

# ── 2. Level normalization ──────────────────────────────────────────────
# Map any accepted alias to a short key, then glob the real dir so a renamed
# suffix (e.g. l1-fib2) still resolves.
case "$LEVEL_ARG" in
  l1|l1-fib|1) SHORT="l1" ;;
  l2|l2-wordstat|2) SHORT="l2" ;;
  l3|l3-kvstore|3) SHORT="l3" ;;
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

# ── 6. Fresh isolated run dir ───────────────────────────────────────────
STAMP="$(date -u +%Y%m%d-%H%M%S)"
RUN_DIR="$HERE/.runs/$TOOL-$LEVEL-$STAMP"
# Guard against two runs landing in the same UTC second.
if [ -e "$RUN_DIR" ]; then
  RUN_DIR="$RUN_DIR-$RANDOM"
fi
mkdir -p "$RUN_DIR"

# ── 7. Tool invocation — STUBS (wired in Plan 02) ───────────────────────
run_codex() {
  # [stub] Plan 02 replaces this body with a real `codex exec` invocation.
  echo "[stub] would invoke codex in $RUN_DIR (wired in Plan 02)"
}

run_openhands() {
  # [stub] Plan 02 replaces this body with a real OpenHands invocation.
  echo "[stub] would invoke openhands in $RUN_DIR (wired in Plan 02)"
}

# ── 8. Start summary + dispatch ─────────────────────────────────────────
echo "tool        : $TOOL"
echo "level       : $LEVEL"
echo "run dir     : $RUN_DIR"
echo "prompt file : $PROMPT_FILE"

case "$TOOL" in
  codex)     run_codex ;;
  openhands) run_openhands ;;
esac
