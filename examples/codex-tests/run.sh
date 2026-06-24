#!/usr/bin/env bash
# codex 테스트 예제 러너.
#   ./run.sh           # 전 레벨 순서대로 실행
#   ./run.sh 03        # 03 으로 시작하는 레벨만 실행
#   ./run.sh 01 05     # 여러 개 지정
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

run_one() {
  local prefix="$1" matches
  matches=( "$HERE"/levels/"$prefix"*.sh )
  if [ ! -e "${matches[0]}" ]; then
    echo "✗ '$prefix' 에 해당하는 레벨 스크립트가 없습니다." >&2
    return 1
  fi
  bash "${matches[0]}"
}

if [ "$#" -ge 1 ]; then
  for p in "$@"; do run_one "$p"; done
else
  for s in "$HERE"/levels/*.sh; do bash "$s"; done
fi
