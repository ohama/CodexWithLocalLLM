# CodexWithLocalLLM

OpenAI **Codex CLI**를 클라우드 API 대신 **로컬 LLM**(Qwen3.5-MoE 122B, Apple Silicon/MLX)에
연결해서, 토큰 비용 0·데이터 외부 유출 0으로 코딩 에이전트를 쓰는 방법을 정리한 저장소.

유튜브 "Codex 무료 사용법(Ollama 연동)" 아이디어에서 출발하되, 이미 운영 중인
**`mlx_lm.server` + LiteLLM** 스택에 맞게 변형·적용한 실전 기록이다.

## 무엇을 푸는가

최신 Codex CLI를 로컬 OpenAI 호환 백엔드에 붙일 때 부딪히는 두 개의 호환성 벽을 해결한다.

1. **Codex가 chat API를 버리고 Responses API만 쓴다** → LiteLLM의 `openai/chat_completions/`
   prefix로 responses→chat **브릿지**.
2. **`mlx_lm.server`가 Codex의 `developer` role을 거부한다** → 사이에 **role-shim**
   (`developer`→`system`)을 끼움.

## 구성

```
Codex CLI ──Responses API──▶ LiteLLM :4000 (qwen-122b-codex)
            ──responses→chat 브릿지──▶ role-shim :8011 (developer→system)
            ──▶ mlx_lm.server :8001 (Qwen3.5-MoE 122B)
```

## 환경 (전제조건)

- Apple Silicon (통합 메모리 ≥ 약 80GB 권장 — 4bit MLX 양자화 65GB)
- `mlx_lm.server`, LiteLLM, OpenAI Codex CLI 0.142+
- 서비스는 launchd로 영구화(`com.ohama.litellm`, `com.ohama.role-shim`, `com.ohama.qwen122b`)

## 설치 (배선)

위 두 벽을 해결하는 배선 구축 전 과정(설치·shim·브릿지)은 한 문서에 정리돼 있다.

→ **[connect-codex-to-local-qwen122b](documentation/howto/connect-codex-to-local-qwen122b.md)**

## 사용법

배선이 끝났다면 작업할 디렉터리에서 바로 쓴다.

### PC에서

```bash
cd ~/my-project
codex                 # 대화형 (기본 모델: qwen-122b-codex)
codex exec "..."      # 비대화형 (자동화/CI)
# 백그라운드/CI는 stdin 닫기 필수 (안 하면 hang):
codex exec "..." < /dev/null > build.log 2>&1 &
```

권한은 **샌드박스 × 승인 모드**로 조절한다 (처음엔 좁게, 신뢰되면 넓게).

```bash
# 일반 코딩 (작업트리 안에서 쓰기/실행 허용)
codex exec --sandbox workspace-write "fix the failing test and run it"

# 읽기 전용 (코드 설명·리뷰)
codex exec --sandbox read-only "explain server.py"
```

- 샌드박스: `read-only` → `workspace-write` → `danger-full-access`
- 승인: `untrusted` / `on-failure` / `on-request` / `never`
- 빠른 자동 반복: `codex --full-auto` (결과는 검토)

자세한 모드·권한·운영·트러블슈팅 → **[use-codex-cli](documentation/howto/use-codex-cli.md)**

### 휴대폰에서

모델·Codex는 Mac에서 돌고, 폰은 **원격 터미널** 역할만 한다 (Tailscale + SSH + tmux).

```bash
# 폰 터미널 앱(Moshi 권장)에서
ssh ohama@100.118.140.2
tmux new -A -s codex      # 끊겨도 유지
codex
```

추천 앱(Moshi)·설정·끊김 방지 → **[use-codex-from-phone](documentation/howto/use-codex-from-phone.md)**

## 예제

레벨별로 Codex를 점검·시연하는 예제 (스모크 → 단일파일 → 멀티스텝 → 자가수정 → 멀티파일).
**실패→디버깅→통과**까지 실제 실행 기록으로 확인할 수 있다.

- **실제 실행 기록(입력+출력 전체):** [examples/codex-tests/RESULTS.md](examples/codex-tests/RESULTS.md)
- 입력 → 출력 요약: [examples/codex-tests/EXAMPLES.md](examples/codex-tests/EXAMPLES.md)
- 실행: `cd examples/codex-tests && ./run.sh` (전체) 또는 `./run.sh 05` (특정 레벨)
- 구조·응용: [examples/codex-tests/README.md](examples/codex-tests/README.md)

**데모** — Codex × 로컬 qwen-122b로 만든 실제 프로그램:
- 🎮 [테트리스](examples/demos/tetris/) (단일 `index.html`) · 생성 시 모델 왕복 전체 기록 → [SESSION.md](examples/demos/tetris/SESSION.md)

## 벤치마크 — Codex vs OpenHands (재현 가능)

같은 코딩 과제를 복잡도 3단계(L1 단일파일 → L2 멀티파일 CLI → L3 다중모듈 서비스)로 **codex**와
**openhands**에 동일 조건(로컬 qwen-122b, 격리·순차)으로 시키고, 능력·시간·과정을 측정·기록하는
재현 가능한 하니스. → **[benchmark/](benchmark/)**

- **결과 리포트:** [benchmark/RESULTS.md](benchmark/RESULTS.md) — 도구×레벨 표(성공·시간·단계·규모) + transcript 발췌 + 레벨별 차이 + 정직성 노트
- **재현 가이드:** [benchmark/REPRODUCE.md](benchmark/REPRODUCE.md) — 사전조건 확인 + 명령별 효과 + 처음부터 재실행
- 실행: `bash benchmark/run.sh <tool> <level>` (1셀) · `bash benchmark/run-matrix.sh` → `python3 benchmark/report.py` (전체)

| | L1 | L2 | L3 |
|---|---|---|---|
| **codex** | ✅ 26s | ✅ 98s | ❌ 14s (truncate) |
| **openhands** | ✅ 49s | ✅ 145s | ✅ 147s |

> codex는 빠르나 L3에서 잘려 실패, openhands는 2~3배 느리지만 전 레벨 성공. (steps 단위는 도구별로 달라 직접 비교 불가 — `step_method` 병기.) 결과는 LLM 비결정성으로 실행마다 달라질 수 있음.

## 문서

| 문서 | 내용 |
|------|------|
| [connect-codex-to-local-qwen122b](documentation/howto/connect-codex-to-local-qwen122b.md) | 유튜브 영상 분석 + 시스템에 맞춘 배선 구축 전 과정 (설치·shim·브릿지) |
| [use-codex-cli](documentation/howto/use-codex-cli.md) | 일상 사용법 — 실행 모드, 샌드박스/승인 권한, 운영·트러블슈팅 |
| [use-codex-from-phone](documentation/howto/use-codex-from-phone.md) | 휴대폰에서 사용 — Tailscale + SSH + tmux 원격 터미널 |
| [codex-vs-hermes-workflow](documentation/codex-vs-hermes-workflow.md) | Codex vs Hermes 비교 — research→planning→execute. 실측: 단발은 동급, Hermes는 kanban 분해→워커 실행→통합(20테스트 통과)까지 실증 (병렬 caveat 포함) |
| [hermes-swarm-tutorial](documentation/hermes-swarm-tutorial.md) | Hermes swarm 실행 따라하기(초보자용) — 매 명령과 효과 명시, 분해→워커 실행→검증 |
| [codex-hermes-openhands-comparison](documentation/codex-hermes-openhands-comparison.md) | Codex vs Hermes vs OpenHands 3자 비교 — 동일 과제·동일 모델(qwen-122b) 실측, 동작방식 차이 |
| [howto 목록](documentation/howto/README.md) | 전체 howto 인덱스 |

## 검증된 능력

로컬 qwen-122b를 에이전트로 실측해 — 병렬 툴콜, 멀티턴 tool 루프, 멀티스텝 코딩, 실패 진단 후
self-repair까지 모두 통과했다. 레벨별 실제 입출력은 → **[RESULTS.md](examples/codex-tests/RESULTS.md)**.
