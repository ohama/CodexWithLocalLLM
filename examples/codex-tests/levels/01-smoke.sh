#!/usr/bin/env bash
# Level 1 — 스모크: 배선이 살아있고 모델이 응답하나 (read-only)
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"
require_gateway

WORK="$(new_run 01-smoke)"; cd "$WORK"
banner "Level 1 — smoke (read-only)  | $WORK"

codex exec "${CODEX_FLAGS[@]}" --sandbox read-only \
  "Reply with exactly: CODEX_OK and nothing else."

# 통과 신호: 출력에 CODEX_OK 가 보이면 OK
