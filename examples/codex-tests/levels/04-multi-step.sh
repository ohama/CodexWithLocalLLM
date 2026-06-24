#!/usr/bin/env bash
# Level 4 — 멀티스텝 프로젝트: CLI 도구 + 샘플 + 테스트 + 실행 (workspace-write)
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"
require_gateway

WORK="$(new_run 04-multi-step)"; cd "$WORK"
banner "Level 4 — multi-step project (workspace-write)  | $WORK"

codex exec "${CODEX_FLAGS[@]}" --sandbox workspace-write \
  "Build a small Python CLI 'wordstat.py' using only the standard library. It reads a text \
file given as argv[1] and prints: total word count, unique word count, and the top 5 most \
frequent words (case-insensitive, ignore punctuation). Create sample.txt with a few \
sentences, write test_wordstat.py with assert-based tests for the counting logic, run the \
tests with python3, then run wordstat.py on sample.txt to show real output."

banner "결과 파일"
ls -1 "$WORK"
