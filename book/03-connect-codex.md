# 3. Codex 를 qwen-122b 에 연결

이미 `codex` 가 로컬 qwen 으로 동작하면 이 장은 건너뛴다.

## 연결됐는지 확인

```sh
grep -E '^[[:space:]]*model[[:space:]]*=' ~/.codex/config.toml
# → model = "qwen-122b-codex" 가 보이면 연결됨
```

## 연결 원리 (왜 이게 필요한가)

최신 Codex CLI를 로컬 백엔드에 붙일 때 **두 개의 호환성 벽**이 있다:

1. **Codex가 chat API를 버리고 Responses API만 쓴다.**
   → LiteLLM이 모델 id에 `openai/chat_completions/` prefix를 붙여 responses→chat 으로 **번역(브릿지)**.
2. **백엔드 `mlx_lm.server` 가 Codex의 `developer` role을 거부한다.**
   → 그 사이에 **role-shim**(`developer`→`system`)을 끼운다.

```
Codex ──Responses──▶ LiteLLM :4000 (qwen-122b-codex)
        ──브릿지──▶ role-shim :8011 ──▶ mlx_lm.server :8001 (qwen-122b)
```

## 설정 요지

`~/.codex/config.toml`:
```toml
model = "qwen-122b-codex"
model_provider = "litellm"

[model_providers.litellm]
name = "LiteLLM (local Qwen)"
base_url = "http://localhost:4000/v1"
env_key = "LITELLM_API_KEY"
wire_api = "responses"
```

> 전체 설치 과정(브릿지 모델 등록 + role-shim launchd 서비스 + Codex CLI 설치)은
> `documentation/howto/connect-codex-to-local-qwen122b.md` 에 단계별로 있다. 이 장은 그 요지다.

## 동작 확인 (선택)

```sh
LITELLM_API_KEY=dummy codex exec --skip-git-repo-check --sandbox read-only \
  "Reply with exactly: OK" < /dev/null
```
- `OK` 가 나오면 codex→qwen-122b 경로가 살아 있다.

> ⚠️ 백그라운드/파이프에서 `codex exec` 를 돌릴 땐 항상 `< /dev/null` 을 붙인다. 안 그러면
> stdin 입력을 기다리며 멈춘다(hang). 벤치마크 러너는 이걸 자동으로 처리한다.

## 다음

codex가 연결됐으면 [4. OpenHands 연결](04-connect-openhands.md)로.
