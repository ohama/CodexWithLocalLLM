#!/usr/bin/env bash
# Level 5 — 디버깅/자가수정: 버그가 심긴 코드를 실패 테스트만 보고 고치나 (workspace-write)
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"
require_gateway

WORK="$(new_run 05-self-repair)"; cd "$WORK"
cp "$FIXTURES_DIR"/self-repair/stats.py "$WORK"/
cp "$FIXTURES_DIR"/self-repair/test_stats.py "$WORK"/

banner "Level 5 — debugging / self-repair (workspace-write)  | $WORK"
echo "(baseline: 테스트는 현재 실패 상태로 심어져 있음)"

codex exec "${CODEX_FLAGS[@]}" --sandbox workspace-write \
  "The project has stats.py and test_stats.py. Run 'python3 test_stats.py' — it is FAILING. \
Investigate why, fix the bug(s) in stats.py only (do NOT modify the test file), and keep \
iterating until all tests pass. Then summarize what was broken and how you fixed it."

banner "독립 재검증"
( cd "$WORK" && python3 test_stats.py )
