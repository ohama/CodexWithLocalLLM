# Agent Benchmark — Codex vs OpenHands

## What This Is

로컬 qwen-122b(LiteLLM :4000) 백엔드 위에서 **Codex CLI**와 **OpenHands**에게 동일한 코딩 과제를
복잡도 3단계로 시키고, 각 도구의 **능력(성공 여부)과 시간·과정**을 동일 조건으로 측정·기록해 비교하는
**재현 가능한 벤치마크 하니스 + 비교 문서**. 사용자가 문서를 보고 그대로 따라 해 직접 비교할 수 있는 것이 목표.

## Core Value

같은 과제를 두 도구에 동일 조건으로 돌려, **누구나 재현·검증 가능한 형태로 능력·시간을 비교 기록**한다.
(결과 수치보다 "재현 가능성"과 "공정한 동일 조건"이 핵심.)

## Requirements

### Validated

- ✓ Codex/OpenHands 모두 로컬 qwen-122b(LiteLLM :4000)로 동작 — existing
- ✓ 3단계 복잡도 과제 정의(L1 fib / L2 wordstat / L3 KV), 고정·도구무관·stdlib 독립 judge — v1.0
- ✓ 동일 조건 러너 `run.sh`(격리·순차·동일모델·비대화) — v1.0
- ✓ 지표 자동 수집 `score.py`(성공[독립judge]·시간·단계[step_method]·규모) — v1.0
- ✓ 도구×레벨 매트릭스 실행+리포트 `run-matrix.sh`/`report.py`/`RESULTS.md` — v1.0
- ✓ 재현 가이드 `REPRODUCE.md`(사전조건·명령별 효과·from-scratch) — v1.0

### Active

<!-- 다음 마일스톤 후보 (확정 전) -->

(없음 — 다음 마일스톤은 `/gsd:new-milestone`에서 정의)

### Out of Scope

- hermes 비교 — 이번 마일스톤은 codex+openhands만 (hermes는 기존 비교 문서에 별도 존재)
- 클라우드 모델 비교 — 로컬 qwen-122b 단일 백엔드로 고정(공정성·비용 0)
- 멀티 모델/백엔드 동시성 — 단일 mlx 백엔드라 직렬 측정이 기준
- 정밀 토큰/비용 회계 — 도구별 로그 형식이 달라 1차 범위에서 제외(필요 시 후속)

## Context

- 백엔드: LiteLLM `localhost:4000` → role-shim → mlx_lm.server(qwen-122b). 3개 도구 공유.
- 실행 제약(이번 세션에서 발견):
  - `codex exec` 는 백그라운드/파이프 실행 시 `< /dev/null` 필요(아니면 stdin hang).
  - 단일 mlx 백엔드라 두 도구 동시 실행은 경합 → **순차 측정**이 안정적.
  - OpenHands 는 `--task ... --headless` 비대화형, 모델은 `~/.openhands/agent_settings.json`(현재 qwen-122b).
- 기존 자산: `examples/codex-tests/`(레벨별 스크립트·RESULTS.md), `documentation/`의 비교 문서들.
- 과제 후보(이미 검증됨): fib(단일), wordstat(멀티파일 CLI), KV 스토어(다중모듈 서비스).

## Constraints

- **Tech stack**: 과제는 Python stdlib 한정 — 외부 의존 없이 어디서나 재현 가능하게.
- **Backend**: 로컬 qwen-122b 고정 — 두 도구 동일 모델로 공정 비교.
- **Reproducibility**: 모든 측정은 스크립트로 재실행 가능해야 하고, 결과 문서에 명령이 그대로 있어야 함.
- **Isolation**: 각 실행은 격리된 작업 디렉터리에서 — 도구 간/실행 간 오염 없음.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| codex+openhands만 비교(hermes 제외) | 사용자 지정, 범위 집중 | ✓ Good |
| 동일 모델 qwen-122b로 통일 | 도구 차이만 분리(모델 변수 제거) | ✓ Good |
| 3레벨 과제는 기존 검증본 재사용(fib/wordstat/KV) | 빠른 시작 + 이미 동작 확인됨 | ✓ Good |
| 순차 측정 | 단일 mlx 백엔드 경합 회피 | ✓ Good |
| 지표 4종(성공·시간·단계수·규모) | 사용자 선택 | ✓ Good |

---
*Last updated: 2026-06-26 after v1.0 milestone*
