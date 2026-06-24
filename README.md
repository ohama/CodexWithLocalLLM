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

## 문서

| 문서 | 내용 |
|------|------|
| [connect-codex-to-local-qwen122b](documentation/howto/connect-codex-to-local-qwen122b.md) | 유튜브 영상 분석 + 시스템에 맞춘 배선 구축 전 과정 (설치·shim·브릿지) |
| [use-codex-cli](documentation/howto/use-codex-cli.md) | 일상 사용법 — 실행 모드, 샌드박스/승인 권한, 운영·트러블슈팅 |
| [use-codex-from-phone](documentation/howto/use-codex-from-phone.md) | 휴대폰에서 사용 — Tailscale + SSH + tmux 원격 터미널 |
| [howto 목록](documentation/howto/README.md) | 전체 howto 인덱스 |

## 사용법

배선이 끝났다면(위 connect 문서 참고) 작업할 디렉터리에서 바로 쓴다.

### PC에서

```bash
cd ~/my-project
codex                 # 대화형 (기본 모델: qwen-122b-codex)
codex exec "..."      # 비대화형 (자동화/CI)
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

## 검증된 능력

로컬 qwen-122b를 에이전트로 실측한 결과 — 병렬 툴콜, 멀티턴 tool 루프, 멀티스텝 코딩
(작성→실행→검증→종료), 그리고 실패 진단 후 self-repair까지 모두 통과. 실제 CLI 도구 작성·테스트도
end-to-end로 동작 확인.

## 환경

- Apple Silicon (통합 메모리 ≥ 약 80GB 권장 — 4bit MLX 양자화 65GB)
- `mlx_lm.server`, LiteLLM, OpenAI Codex CLI 0.142+
- 서비스는 launchd로 영구화(`com.ohama.litellm`, `com.ohama.role-shim`, `com.ohama.qwen122b`)
