#!/usr/bin/env bash
# Level 3 — 단일 파일 코딩: 함수 작성 + 테스트 + 실행 (workspace-write)
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"
require_gateway

WORK="$(new_run 03-single-file)"; cd "$WORK"
banner "Level 3 — single-file coding (workspace-write)  | $WORK"

codex exec "${CODEX_FLAGS[@]}" --sandbox workspace-write \
  "Create fib.py with a function fib(n) (fib(0)=0, fib(1)=1) plus a few assert tests \
covering fib(0), fib(1), and fib(10)==55. Then run it with 'python3 fib.py' and show \
the output. Make sure it passes."

banner "결과 파일"
ls -1 "$WORK"
