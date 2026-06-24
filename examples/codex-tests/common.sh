#!/usr/bin/env bash
# 공통 헬퍼 — codex 테스트 예제들이 source 해서 사용.
set -euo pipefail

export LITELLM_API_KEY="${LITELLM_API_KEY:-dummy}"

COMMON_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNS_DIR="$COMMON_DIR/.runs"
FIXTURES_DIR="$COMMON_DIR/fixtures"

# codex exec 공통 플래그 (예제는 git 리포 밖처럼 독립 실행)
CODEX_FLAGS=(--skip-git-repo-check)

# 게이트웨이가 살아있는지 확인 (없으면 친절히 종료)
require_gateway() {
  if ! curl -sf -m 5 http://localhost:4000/v1/models \
        -H "Authorization: Bearer dummy" >/dev/null 2>&1; then
    echo "✗ LiteLLM 게이트웨이(:4000)가 응답하지 않습니다."
    echo "  서비스 확인:  launchctl list | grep com.ohama"
    exit 1
  fi
}

# 격리된 작업 디렉터리 생성 후 경로 출력.  $1 = 레벨 이름
new_run() {
  local d="$RUNS_DIR/$1-$(date +%Y%m%d-%H%M%S)"
  mkdir -p "$d"
  echo "$d"
}

banner() { printf '\n\033[1m▶ %s\033[0m\n' "$*"; }
