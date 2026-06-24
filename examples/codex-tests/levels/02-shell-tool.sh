#!/usr/bin/env bash
# Level 2 — 도구/셸 사용: 명령을 실행하고 결과를 보고하나 (read-only)
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"
require_gateway

WORK="$(new_run 02-shell-tool)"; cd "$WORK"
banner "Level 2 — shell tool use (read-only)  | $WORK"

codex exec "${CODEX_FLAGS[@]}" --sandbox read-only \
  "Run the command 'python3 --version' and report the exact version string it prints."

# 통과 신호: 실제 python3 버전을 실행해서 보고 (예: Python 3.x.y)
