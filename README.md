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
| [howto 목록](documentation/howto/README.md) | 전체 howto 인덱스 |

## 빠른 시작

배선이 끝났다면(위 connect 문서 참고):

```bash
cd ~/my-project
codex                 # 대화형 (기본 모델: qwen-122b-codex)
codex exec "..."      # 비대화형 (자동화/CI)
```

## 검증된 능력

로컬 qwen-122b를 에이전트로 실측한 결과 — 병렬 툴콜, 멀티턴 tool 루프, 멀티스텝 코딩
(작성→실행→검증→종료), 그리고 실패 진단 후 self-repair까지 모두 통과. 실제 CLI 도구 작성·테스트도
end-to-end로 동작 확인.

## 환경

- Apple Silicon (통합 메모리 ≥ 약 80GB 권장 — 4bit MLX 양자화 65GB)
- `mlx_lm.server`, LiteLLM, OpenAI Codex CLI 0.142+
- 서비스는 launchd로 영구화(`com.ohama.litellm`, `com.ohama.role-shim`, `com.ohama.qwen122b`)
