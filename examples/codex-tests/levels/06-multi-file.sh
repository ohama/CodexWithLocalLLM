#!/usr/bin/env bash
# Level 6 — 멀티파일 패키지: 여러 파일에 걸친 구조 생성 + 테스트 (workspace-write)
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"
require_gateway

WORK="$(new_run 06-multi-file)"; cd "$WORK"
banner "Level 6 — multi-file package (workspace-write)  | $WORK"

codex exec "${CODEX_FLAGS[@]}" --sandbox workspace-write \
  "Create a small Python package 'mathpkg' with: mathpkg/__init__.py exporting add/sub/mul, \
mathpkg/ops.py implementing them, and tests/test_ops.py with unittest cases for each. \
Then run the tests with 'python3 -m unittest discover -s tests' and make sure they pass."

banner "결과 트리"
find "$WORK" -type f -not -path '*/__pycache__/*' | sed "s|$WORK/||" | sort
