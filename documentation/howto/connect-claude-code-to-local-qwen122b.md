---
created: 2026-06-29
description: Claude Code(클로드 코드 CLI)를 로컬 qwen-122b(mlx+LiteLLM)에 붙이는 따라하기 가이드 — 명령·예상결과·검증 포인트 포함, 함께 채워나가는 문서
status: VERIFIED (2026-06-29) — claude-code-proxy 경로로 end-to-end 동작 확인 (Step P). LiteLLM 직결(Step 1~5)은 막다른 길로 확정. UPDATED (2026-06-30) — tier 분리 적용: Opus→122b, Sonnet/Haiku→35b (Step P-3 + P-1b).
---

# Claude Code를 로컬 qwen-122b로 연결하기 (따라하기)

> **이 문서의 사용법.** 각 단계에 **① 명령 / ② 예상 결과 / ③ 📋 결과 기록(네가 채워줘)** 이 있다.
> 네가 직접 명령을 실행하고 실제 출력을 ③에 알려주면, 내가 그걸로 다음 단계와 "예상"을 **보완**한다.
> "예상"이라고 표시된 곳은 아직 end-to-end로 검증 안 된 부분이다(솔직하게 표시함).

---

## 결론 먼저 (TL;DR)

- **가능하다 — 단, 직접은 아니다.** Claude Code는 **Anthropic Messages API(`POST /v1/messages`)만** 말한다.
  로컬 모델·OpenAI 호환 백엔드를 직접 못 붙인다. 공식 지원 백엔드는 Anthropic API / Amazon Bedrock /
  Google Vertex / Azure Foundry 뿐. 그 외에는 **anthropic↔백엔드 번역 게이트웨이**가 반드시 필요하다.
  ([근거: Claude Code LLM gateway 문서](https://code.claude.com/docs/en/llm-gateway))
- **주의 — 네 LiteLLM(1.86.1)의 `/v1/messages`는 그대로는 안 된다(측정으로 확정).** LiteLLM의 anthropic
  엔드포인트가 내부적으로 **Responses API로 번역**하는데, 네 mlx 백엔드엔 Responses API가 없어 404가 난다.
  (자세한 진단은 아래 "진단 결과" 절.) → **권장 경로: anthropic→chat 전용 프록시를 한 겹 끼운다**(Codex의
  role-shim과 같은 패턴). ([근거: LiteLLM "Use Claude Code with Non-Anthropic Models"](https://docs.litellm.ai/docs/tutorials/claude_non_anthropic_models),
  [LiteLLM anthropic_unified](https://docs.litellm.ai/docs/anthropic_unified/))
- **Codex 때와 번역 방향이 반대다.**
  - Codex: `Responses API → chat` 번역이 필요했다(`openai/chat_completions/` prefix + role-shim).
  - Claude Code: `Anthropic Messages → chat` 번역이 필요하다(LiteLLM의 `/v1/messages` 엔드포인트).
- **핵심 환경변수 4개**면 붙는다:
  `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_MODEL`, `ANTHROPIC_DEFAULT_HAIKU_MODEL`.
  ([근거: Claude Code 환경변수 문서](https://code.claude.com/docs/en/env-vars))

### Codex 연결 vs Claude Code 연결

| 항목 | Codex (기존, 완료) | Claude Code (이번) |
|------|--------------------|---------------------|
| 클라이언트가 쓰는 API | Responses API | **Anthropic Messages API** (`/v1/messages`) |
| 게이트웨이가 할 번역 | responses → chat | **anthropic → chat** |
| LiteLLM 모델 트릭 | `openai/chat_completions/` prefix | LiteLLM의 `/v1/messages` 엔드포인트가 자동 번역 |
| 백엔드 진입점 | role-shim :8011 (developer role 때문) | **(예상) 평범한 모델 → :8001 직결**, role 문제 나면 shim 경유로 전환 |
| 설정 위치 | `~/.codex/config.toml` | **환경변수** 또는 `~/.claude/settings.json`의 `env` 블록 |
| 모델 id(예) | `qwen-122b-codex` | `qwen-122b` (또는 새로 만들 `qwen-122b-claude`) |

---

## ⚠️ 시작 전 보안 경고 (먼저 읽기)

Anthropic이 경고: **LiteLLM PyPI 버전 `1.82.7` / `1.82.8` 에 자격증명 탈취 멀웨어**가 섞여 배포된 적이 있다.
이 두 버전이면 즉시 교체하고 키를 전부 회전(rotate)할 것. 깨끗한 다른 버전으로 핀(pin).
([근거: 검색 요약 — Anthropic warning re LiteLLM 1.82.7/1.82.8](https://docs.litellm.ai/docs/tutorials/claude_non_anthropic_models))

```bash
litellm --version    # 1.82.7 / 1.82.8 이면 안 됨
```
📋 **결과 기록:** `litellm --version` →  `__________`

---

## 진단 결과 (✅ 범인 확정 — 2026-06-29)

아래는 내가(클로드) 네 머신에서 **실제로 측정**해 확정한 내용이다.

**환경**
- `claude --version` → **2.1.195 (Claude Code)** ✅ (게이트웨이 디스커버리 v2.1.129+ 요건 충족)
- LiteLLM 버전 → **1.86.1** ✅ (멀웨어 1.82.7/1.82.8과 무관, 안전)
- `:4000` 노출 모델 → `qwen-35b`, `qwen-122b`, `qwen-local`, `qwen-122b-codex`

**격리 테스트 (어디까지 정상인가)**

| 테스트 | 결과 |
|--------|------|
| mlx `:8001` 직접 chat | **200** ✅ |
| LiteLLM `:4000` `/v1/chat/completions` (qwen-122b) | **200** ✅ |
| LiteLLM `:4000` `/v1/responses` (qwen-122b-codex, Codex 경로) | **200** ✅ |
| LiteLLM `:4000` **`/v1/messages`** (anthropic) — qwen-122b | **404** ❌ |
| LiteLLM `:4000` **`/v1/messages`** (anthropic) — qwen-122b-codex | **404** ❌ |

**범인: LiteLLM 1.86.1의 `/v1/messages` 구현이 백엔드에 "Responses API"를 요구한다.**
- 코드 경로: `litellm/llms/anthropic/experimental_pass_through/responses_adapters/handler.py` →
  `/v1/messages` 핸들러가 내부에서 **`litellm.aresponses()`** 를 호출한다.
  즉 번역 방향이 **anthropic messages → Responses API → 백엔드**다 (anthropic→chat 이 아님!).
- 네 mlx 백엔드는 **Responses API(`/v1/responses`)가 없다**(chat/completions만 구현) → 백엔드 404 →
  `OpenAIException - Not Found`로 표면화.
- 결정적으로 이 내부 `aresponses` 경로는 **Codex가 쓰는 프록시 `/v1/responses` 엔드포인트(= responses→chat
  브릿지가 작동, 200)와 다른 코드 경로**라, `qwen-122b-codex`를 넣어도 그 브릿지를 안 타고 404가 난다.
- 관측 에러: `litellm.NotFoundError: OpenAIException - Not Found. Received Model Group=qwen-122b`

> **결론:** LiteLLM 1.86.1의 `/v1/messages`는 chat-only(mlx) 백엔드와 **구조적으로 안 맞는다.**
> 입구는 열렸지만 안쪽이 Responses API를 고집한다. → **아래 "권장 경로"로 우회한다.**

---

## Step 0 — 전제 확인

```bash
claude --version
curl -s http://localhost:4000/v1/models -H "Authorization: Bearer dummy" | python3 -m json.tool | grep '"id"'
launchctl list | grep -E 'litellm|qwen122b|role-shim'
```

**예상 결과:** Claude Code 2.1.x, 모델 4개, launchd 서비스 3개가 떠 있음.

📋 **결과 기록:**
```
(여기에 실제 출력 붙여넣기)
```

---

## Step 1 — LiteLLM `/v1/messages` 직접 타진 (✅ 실행 완료 — 막다른 길로 확정)

> **이미 돌려봤다.** 결과: LiteLLM 1.86.1의 `/v1/messages`는 mlx에서 **404로 막힘**(위 "진단 결과" 참고).
> 백엔드·chat 라우팅은 정상인데 anthropic 경로만 Responses API를 요구해서 깨진다.
> → **이 LiteLLM-직결 경로(Step 2~5)는 mlx에선 안 된다. "권장 경로(아래 Step P)"로 간다.**
> 아래 curl은 재현/회귀 확인용으로 남겨둔다.

Claude Code를 붙이기 **전에**, 게이트웨이가 Anthropic 포맷을 받아서 qwen으로 번역하는지부터 확인한다.

```bash
curl -sS -X POST http://localhost:4000/v1/messages \
  -H "Authorization: Bearer dummy" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "qwen-122b",
    "max_tokens": 64,
    "messages": [{"role": "user", "content": "Reply with exactly: pong"}]
  }' | python3 -m json.tool
```

**예상(성공 시) 결과:** Anthropic 포맷 응답 —
```json
{
  "id": "msg_...",
  "type": "message",
  "role": "assistant",
  "content": [{"type": "text", "text": "pong"}],
  "model": "qwen-122b",
  "stop_reason": "end_turn",
  "usage": {"input_tokens": ..., "output_tokens": ...}
}
```

**현재 알려진 실패 상태(내가 본 것):** `OpenAIException - Not Found` (백엔드 404).
실패하면 아래 분기를 차례로 시도하고 **각 출력**을 알려줘:

1. **백엔드(mlx :8001)가 직접 chat을 받는지** — 번역 문제인지 백엔드 문제인지 가른다:
   ```bash
   curl -sS http://localhost:8001/v1/chat/completions \
     -H "content-type: application/json" \
     -d '{"model":"/Users/ohama/llm-system/models/qwen122b","max_tokens":16,
          "messages":[{"role":"user","content":"say pong"}]}' | head -c 400; echo
   ```
   - 200이면 → 백엔드는 정상, 문제는 LiteLLM의 anthropic→chat 번역 경로.
   - 404/400이면 → 모델 경로(`model` 값) 또는 mlx 쪽 문제.

2. **LiteLLM 버전이 `/v1/messages`(anthropic_unified)를 지원하는 버전인지**:
   ```bash
   litellm --version
   ```
   (너무 옛 버전이면 `/v1/messages` 번역이 미구현/불완전일 수 있음.)

3. **LiteLLM 로그**에서 404가 어디서 났는지:
   ```bash
   tail -n 40 ~/Library/Logs/litellm.log 2>/dev/null || launchctl print gui/$(id -u)/com.ohama.litellm 2>/dev/null | tail -40
   ```

📋 **결과 기록:**
- 메인 curl 응답: `__________`
- 분기 1 (mlx 직접): `__________`
- 분기 2 (litellm 버전): `__________`
- 분기 3 (로그 발췌): `__________`

> 💡 이 결과를 주면, 404 원인을 특정해서 Step 2를 "예상"이 아니라 "확정"으로 바꿔 줄게.

---

## Step P — 권장 경로: claude-code-proxy (✅ end-to-end 검증 완료 2026-06-29)

> **이게 동작하는 메인 경로다.** Codex의 role-shim과 같은 발상: **얇은 번역 한 겹**을 끼우고 나머지
> 스택(LiteLLM/mlx)은 그대로 둔다. 아래는 실제로 뚫어서 검증한 레시피.

**검증된 구조:**
```
Claude Code 2.1.195 ──anthropic /v1/messages──▶ claude-code-proxy :8082
   ──openai /v1/chat/completions──▶ LiteLLM :4000 (model: qwen-122b-claude)
   ──▶ role-shim :8011 (system-first 정규화)  ──▶ mlx_lm.server :8001 (qwen-122b)
```

> ⚠️ **두 번째 벽(실측으로 발견):** 프록시의 anthropic→chat 변환은 잘 되는데, 그대로 mlx에 보내면
> `OpenAIException ... 'System message must be at the beginning.'` 로 거부된다 — Codex 때 `developer`
> role을 거부했던 것과 **같은 mlx 제약**. 그래서 백엔드 모델을 `qwen-122b`(직결) 가 아니라
> **`qwen-122b-claude`(role-shim :8011 경유)** 로 잡아야 한다. shim이 "첫 메시지 외 system→user"로
> 정규화해서 이 제약을 해소한다.

### P-1. role-shim 경유 LiteLLM 모델 추가

`/Users/ohama/agent-stack/litellm/config.yaml` 에 **추가만**(기존 항목 불변):
```yaml
  # Claude Code 전용 — claude-code-proxy가 anthropic→chat 변환 후 여기로.
  # role-shim(:8011)을 거쳐 mlx의 "System message must be at the beginning." 제약 해소.
  - model_name: qwen-122b-claude
    litellm_params:
      model: openai//Users/ohama/llm-system/models/qwen122b
      api_base: http://localhost:8011/v1   # ← role-shim (mlx 직결 :8001 아님!)
      api_key: dummy
```
```bash
launchctl kickstart -k gui/$(id -u)/com.ohama.litellm   # ~3초, mlx는 안 건드림
# 확인: system이 중간에 낀 요청도 200 나와야 함 (직결 qwen-122b면 404)
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer dummy" -H "content-type: application/json" \
  -d '{"model":"qwen-122b-claude","max_tokens":16,"messages":[{"role":"user","content":"hi"},{"role":"system","content":"be terse"},{"role":"user","content":"say pong"}]}'
# → 200
```

### P-1b. (✅ 적용 완료 2026-06-30) 35b tier 분리 — 빠른 백그라운드/기본 작업용

세 tier를 전부 122b로 묶으면 가벼운 잡일(요약·제목)까지 큰 모델이 처리해 느리다. **Opus만 122b로
두고 Sonnet·Haiku는 35b로** 내리면 기본은 빠른 35b, 무거운 건 `--model opus`로 승격하는 구조가 된다.

> ⚠️ 35b도 122b와 **같은 "System message must be at the beginning." 제약**을 받는다. 그래서 직결
> `qwen-35b`(:8000) 엔트리는 claude 경로에서 못 쓰고(404), **35b 전용 role-shim을 따로** 둬야 한다.
> role-shim은 upstream이 인스턴스당 하나로 고정(`role_shim.py`가 모델로 분기 안 함)이라 **mlx 백엔드마다
> shim 하나** 원칙(:8011→122b, :8012→35b).

```bash
# 1) 35b용 2번째 role-shim (launchd) — :8012 → mlx 35b :8000
#    plist: ~/Library/LaunchAgents/com.ohama.role-shim-35b.plist
#    ProgramArguments = [venv/bin/python, role_shim.py, --listen, 8012, --upstream, http://localhost:8000]
#    KeepAlive=true, RunAtLoad=true, 로그 = role-shim-35b.log / .err.log
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.ohama.role-shim-35b.plist
curl -s http://localhost:8012/v1/models | python3 -m json.tool   # → qwen36-35b 보이면 OK

# 2) LiteLLM에 35b-claude 엔트리 추가 (config.yaml, 추가만)
#   - model_name: qwen-35b-claude
#     litellm_params:
#       model: openai//Users/ohama/llm-system/models/qwen36-35b
#       api_base: http://localhost:8012/v1   # ← 35b shim
#       api_key: dummy
launchctl kickstart -k gui/$(id -u)/com.ohama.litellm
curl -s localhost:4000/v1/models -H "Authorization: Bearer dummy" | grep qwen-35b-claude   # 노출 확인
```
그 다음 P-3에서 proxy.env의 Sonnet/Haiku를 `qwen-35b-claude`로 바꾸면 끝. **검증**(프록시 `[REQ]` 로그):
`qclaude --model opus`→`qwen-122b-claude`, `qclaude --model sonnet`→`qwen-35b-claude`.

### P-2. claude-code-proxy 빌드 (Go 바이너리)

```bash
git clone --depth 1 https://github.com/nielspeter/claude-code-proxy.git
cd claude-code-proxy
go build -o claude-code-proxy ./cmd/claude-code-proxy   # go 1.2x 필요, 결과 ~11MB 단일 바이너리
```

### P-3. 프록시 설정 — `~/.claude/proxy.env`

```bash
OPENAI_BASE_URL=http://localhost:4000/v1
OPENAI_API_KEY=dummy
# tier 분리 (2026-06-30): Opus=122b(무거운 추론/코딩, 명시적으로 고를 때만),
#                         Sonnet·Haiku=35b(기본 + 가벼운 백그라운드, 빠름).
# 모두 role-shim 경유 모델이어야 함 (직결 qwen-122b/qwen-35b는 system-first 404).
ANTHROPIC_DEFAULT_OPUS_MODEL=qwen-122b-claude
ANTHROPIC_DEFAULT_SONNET_MODEL=qwen-35b-claude
ANTHROPIC_DEFAULT_HAIKU_MODEL=qwen-35b-claude
PORT=8082
```
> 💡 35b-claude 모델/shim 만드는 법은 위 **P-1b** 참고. 전부 122b로 되돌리려면 세 줄 다
> `qwen-122b-claude`로 두면 된다.
> ⚠️ **동작 변화:** Claude Code 기본 tier는 Sonnet이라, 이제 그냥 `qclaude`로 켜면 **35b로 돈다**.
> 무거운 작업은 `qclaude --model opus`(또는 세션 안 `/model`)로 122b 승격.

### P-4. 프록시 기동 + Claude Code 연결

```bash
./claude-code-proxy -d        # 데몬 시작(:8082), -d는 디버그 로그. status/stop 서브커맨드 있음
# Claude Code를 이 프록시로 (이 셸에서만; 전역 설정 안 건드림)
export ANTHROPIC_BASE_URL=http://localhost:8082
export ANTHROPIC_AUTH_TOKEN=dummy
```

### P-5. 검증 (실측 결과)

```bash
claude -p "Reply with exactly: pong"
# → pong   ✅ (qwen-122b가 답함)

# 툴콜·파일쓰기 end-to-end:
mkdir -p /tmp/cc && cd /tmp/cc
claude -p "Create factorial.py with factorial(n) and 3 asserts, then run it." --permission-mode acceptEdits
# → factorial.py 생성됨(Write 툴 동작), 코드 정확(python3 실행 시 'All tests passed!')  ✅
# → 스트리밍 정상 종료(LiteLLM 스트리밍 tool 버그 미발생)  ✅
```

> 참고: `--permission-mode acceptEdits`는 파일편집만 자동승인이라 bash(python 실행)는 별도 승인이 필요하다.
> 완전 자율로 돌리려면 `--permission-mode bypassPermissions`(주의해서). 무해한 경고
> `claude.ai connectors are disabled ...`는 `ANTHROPIC_AUTH_TOKEN`을 설정해서 뜨는 정상 메시지.

### P-6. 영구화 (✅ 완료 2026-06-29)

바이너리를 scratchpad 밖으로 이전하고 launchd로 KeepAlive 등록 (role-shim과 같은 패턴):

```bash
# 1) 바이너리 이전
mkdir -p /Users/ohama/agent-stack/claude-code-proxy
cp <build>/claude-code-proxy /Users/ohama/agent-stack/claude-code-proxy/

# 2) launchd plist: ~/Library/LaunchAgents/com.ohama.claude-proxy.plist
#    ProgramArguments = [.../claude-code-proxy, -s], KeepAlive=true, RunAtLoad=true,
#    EnvironmentVariables HOME=/Users/ohama (proxy.env 탐색용), WorkingDirectory=그 폴더,
#    로그 = .../claude-code-proxy/proxy.log / proxy.err.log

# 3) 등록
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.ohama.claude-proxy.plist
launchctl list | grep claude-proxy            # PID 확인
curl -s -o/dev/null -w "%{http_code}\n" http://localhost:8082/health   # 200
```

검증됨: KeepAlive 자동복구 OK(프로세스 kill → 새 PID로 부활), 재부팅 후에도 RunAtLoad로 자동 기동.
재시작: `launchctl kickstart -k gui/$(id -u)/com.ohama.claude-proxy`.

> ⚠️ 주의: `daemon.go`의 `Start()`는 실제로 fork하지 않고 **포그라운드로** 서버를 돈다(이름만 "daemon").
> 그래서 launchd와 잘 맞는다. PID파일은 `/tmp/claude-code-proxy.pid`.

### P-7. 편하게 쓰기 (전역 오염 방지)

`ANTHROPIC_BASE_URL`을 셸 rc에 전역으로 박으면 **너의 모든 `claude`가 qwen으로** 간다(클라우드 Claude
못 씀). 분리하려면 **별도 alias**를 권장:

```bash
# ~/.zshrc — claude는 반드시 풀패스로! (그냥 `claude`면 zsh가 claude→myclaude(tmux 래퍼)
# alias로 재확장해서 엉뚱한 데로 샌다. which claude 가 myclaude를 가리키면 특히.)
alias qclaude='ANTHROPIC_BASE_URL=http://localhost:8082 ANTHROPIC_AUTH_TOKEN=dummy /opt/homebrew/bin/claude'
# 사용: qclaude          → 로컬 qwen-122b
#       claude           → 평소대로 클라우드(로그인 계정)
# 검증: zsh -ic 'qclaude --version' → "2.1.195 (Claude Code)" (open terminal failed 뜨면 아직 샘)
```

### P-8. 빠른 모드 — `--bare` 로 첫 턴 prefill 줄이기 (✅ 측정 2026-06-30)

로컬 qwen에서 qclaude가 codex보다 느린 **진짜 원인은 "캐싱 비활성"이 아니다** — codex도 같은
로컬 mlx라 Anthropic 캐싱이 없다. 원인은 **Claude Code가 보내는 거대한 프롬프트**(시스템 프롬프트
+ 툴 25종 스키마 + CLAUDE.md/메모리/스킬)를 mlx가 **턴마다 콜드 prefill** 하는 것. prefill은
선형(122b ≈ **1k 토큰당 1.75초**)이라 첫 토큰까지(ttft) 79~196초가 걸린다.

**해결: 프롬프트를 줄인다.** `--bare`(훅/LSP/플러그인 + CLAUDE.md/메모리/스킬 **자동주입** skip)
+ `--tools`(툴 스키마 최소화). 같은 122b·같은 L1 과제에서 측정:

| | 툴 스키마 | ttft | 총시간 |
|---|---|---|---|
| 풀 환경 (`qclaude`) | 25 | 98.6s | 158.2s |
| **`--bare` + 툴 최소** | 3~7 | **8.9s** | **28.5s** |

→ **ttft 11× / 총시간 5.5× 단축** (codex의 23s급). 정답은 그대로 PASS.

```bash
# ~/.zshrc — 빠른 모드 별칭 (qclaude는 풀기능용으로 그대로 둔다)
# --bare 라도 슬래시 명령/스킬은 /name 으로 그대로 쓸 수 있다.
alias qcf='ANTHROPIC_BASE_URL=http://localhost:8082 ANTHROPIC_AUTH_TOKEN=dummy /opt/homebrew/bin/claude --model opus --bare --tools Read Write Edit Bash Grep Glob WebFetch'
alias qcf35='ANTHROPIC_BASE_URL=http://localhost:8082 ANTHROPIC_AUTH_TOKEN=dummy /opt/homebrew/bin/claude --model sonnet --bare --tools Read Write Edit Bash Grep Glob WebFetch'
# 사용: qcf "..."   → 빠른 122b   /   qcf35 "..." → 최속 35b   /   qclaude → 풀기능(메모리·CLAUDE.md)
```

**트레이드오프 (`--bare`로 빠져나가는 것):** CLAUDE.md/자동 메모리 주입, 훅, MCP, 플러그인(LSP).
프로젝트 지침이 필요하면 `qcf --add-dir .`(그만큼 프롬프트↑), 툴 더 필요하면 `--tools`에 추가.

> 참고: **한 세션 안**에서는 첫 턴 이후 mlx가 prefix를 재사용(~0.1s)하므로 둘째 턴부터 빠르다.
> `--bare`의 이득은 그 **첫 턴/새 세션**의 콜드 prefill을 싸게 만드는 것. 무거운 작업은 `qcf`(122b),
> 가벼운 잡일/속도 우선은 `qcf35`(35b). `--prefill-step-size` 상향은 효과 없었다(연산 병목).
> (3자 벤치마크 근거: `benchmark/RESULTS-3way-qwen.md`.)

---

## Step 2 — (참고용·비권장) Claude 전용 LiteLLM 모델 추가

> ⚠️ Step 1 진단으로 **LiteLLM 직결 자체가 막힌 게 확정**됐다. 이 Step 2~5는 "원래 시도하려던 길"의
> 기록으로 남겨둔다(LiteLLM이 anthropic→chat 직접 번역하는 환경에선 유효). 너의 1.86.1+mlx에선 **건너뛴다.**

Step 1이 그냥 통과하면 **이 단계는 건너뛴다.** 만약 404가 백엔드 role/경로 문제로 판명되면(=Codex 때
mlx가 `developer` role을 거부했던 것과 유사한 류), Codex 때 만든 **role-shim(:8011)** 을 재활용해
Claude 전용 항목을 하나 추가한다. (기존 항목 불변 → 다른 클라이언트 무영향.)

`/Users/ohama/agent-stack/litellm/config.yaml` 에 추가 **(예상안 — Step 1 결과 보고 확정)**:

```yaml
  # Claude Code(Anthropic /v1/messages) 전용 — anthropic→chat 번역 + role-shim(:8011) → mlx(:8001)
  - model_name: qwen-122b-claude
    litellm_params:
      model: openai//Users/ohama/llm-system/models/qwen122b
      api_base: http://localhost:8011/v1   # role-shim 경유 (role 안전)
      api_key: dummy
```

> 포인트: Claude Code는 Responses가 아니라 Messages API라서 `openai/chat_completions/` prefix는 **필요 없다**.
> `/v1/messages` 엔드포인트가 anthropic→chat 번역을 담당하고, `model:`은 평범한 `openai/...`면 된다.
> api_base를 shim(:8011)으로 두는 건 mlx의 role 제약 회피용(예방).

재시작(모델 서버는 안 건드림):
```bash
launchctl kickstart -k gui/$(id -u)/com.ohama.litellm
curl -s localhost:4000/v1/models -H "Authorization: Bearer dummy" | grep qwen-122b-claude
```

📋 **결과 기록:** 새 모델 노출됨? `__________`

---

## Step 3 — 환경변수로 Claude Code를 게이트웨이에 연결

LiteLLM 공식 가이드 그대로. ([근거](https://docs.litellm.ai/docs/tutorials/claude_non_anthropic_models))

```bash
export ANTHROPIC_BASE_URL="http://localhost:4000"   # /v1/messages 는 Claude Code가 자동으로 붙임
export ANTHROPIC_AUTH_TOKEN="dummy"                 # 너의 LiteLLM은 아무 키나 허용
export ANTHROPIC_MODEL="qwen-122b"                  # Step 2를 했다면 "qwen-122b-claude"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="qwen-35b"     # 백그라운드/요약용 = 더 작은 모델(빠름)
# (옛 변수명 호환이 필요하면) export ANTHROPIC_SMALL_FAST_MODEL="qwen-35b"
```

> **왜 `ANTHROPIC_DEFAULT_HAIKU_MODEL`?** Claude Code는 제목 생성·요약 같은 잡일에 "작고 빠른
> haiku급" 모델을 따로 호출한다. 게이트웨이에선 그 이름을 백엔드가 아는 id로 매핑 안 하면 백그라운드
> 작업이 실패한다. 너는 `qwen-35b`(:8000)가 있으니 그걸 쓰면 빠르고 좋다.
> ([근거: env-vars 문서](https://code.claude.com/docs/en/env-vars))

연결 확인 (간단 대화 1턴):
```bash
claude -p "Reply with exactly: pong"
```
**예상 결과:** `pong` (qwen이 답함).

📋 **결과 기록:** `claude -p` 응답: `__________`

> ⚠️ `claude`가 너의 셸에선 tmux 래퍼(`myclaude`) alias일 수 있다. 위 비대화형 테스트는 실제
> 바이너리로 하는 게 깔끔하다: `/opt/homebrew/bin/claude -p "Reply with exactly: pong"`.

---

## Step 4 — (선택) `/model` 피커에 게이트웨이 모델 띄우기

```bash
export CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1   # v2.1.129+ 필요 (너는 2.1.195 ✅)
claude
# 세션 안에서:  /model   → "From gateway" 라벨로 qwen-* 들이 보여야 함
```
이걸 켜면 Claude Code가 시작 시 `GET /v1/models`를 게이트웨이에 호출해 모델 목록을 가져온다.
([근거: 검색 요약 — gateway model discovery](https://docs.litellm.ai/docs/tutorials/claude_non_anthropic_models))

📋 **결과 기록:** `/model`에 qwen 모델 보임? `__________`

---

## Step 5 — end-to-end 코딩 에이전트 테스트 (진짜 검증)

대화 1턴이 되는 것과, **툴콜·파일쓰기·멀티스텝**이 되는 건 다르다. Codex 때처럼 실전 작업으로 확인.

```bash
mkdir -p /tmp/cc-qwen-test && cd /tmp/cc-qwen-test
claude -p "Create factorial.py with a factorial(n) function and 3 asserts, then run it with python3 and report the result." \
  --permission-mode acceptEdits
ls -la; cat factorial.py 2>/dev/null
```

**예상 결과:** `factorial.py` 생성 → 실행 → "asserts passed" 류 보고.

📋 **결과 기록:**
```
(파일 생성됐는지 / 실행 보고 / 에러 메시지)
```

> 이 단계가 핵심 변별점이다. 여기서 **툴콜이 깨지면**(파일이 안 써지거나, tool_use 인자가 비면)
> 아래 "알려진 한계"의 LiteLLM 스트리밍 버그일 확률이 높다 → 보완책 같이 잡자.

---

## 알려진 한계 / 게이트웨이 번역의 함정

Claude Code를 비-Anthropic 모델에 붙이면 **포기해야 하는 것들**과 **버그**가 있다. 미리 알아야 디버깅이 쉽다.

| 한계/버그 | 내용 | 근거 |
|-----------|------|------|
| **프롬프트 캐싱 불가** | 캐싱은 Anthropic 네이티브 포맷에서만. OpenAI 번역 경로에선 동작 안 함 → 매 요청 풀 컨텍스트 재전송(느림·토큰↑) | [apiyi 가이드](https://help.apiyi.com/en/claude-prompt-caching-anthropic-native-format-guide-en.html) |
| **MCP tool search 기본 비활성** | `ANTHROPIC_BASE_URL` 설정 시 모델 디스커버리/ MCP 툴서치가 기본 꺼짐 → 툴은 미리 설정해야 | [env-vars 문서](https://code.claude.com/docs/en/env-vars) |
| **스트리밍 tool_use 인자 유실** | LiteLLM anthropic→openai 어댑터가 **스트리밍 모드에서 tool_use 인자를 떨어뜨리는 회귀** (비스트리밍은 OK) | [litellm#25321](https://github.com/BerriAI/litellm/issues/25321), [#30014](https://github.com/BerriAI/litellm/issues/30014) |
| **첫 토큰/델타 유실** | 스트리밍 시 응답 앞부분 글자가 잘리는 버그 | [litellm#30014](https://github.com/BerriAI/litellm/issues/30014) |
| **max_tokens 오염** | 같은 모델에 OpenAI 요청이 한 번 닿으면 max_tokens가 32000으로 기본값 오염되는 버그 | [litellm#22249](https://github.com/BerriAI/litellm/issues/22249) |
| **haiku급 모델 매핑 필수** | 백그라운드 잡일용 small/fast 모델을 매핑 안 하면 실패 → `ANTHROPIC_DEFAULT_HAIKU_MODEL` 지정 | [env-vars 문서](https://code.claude.com/docs/en/env-vars) |
| **extended thinking 등 미지원 가능** | Anthropic 전용 기능(thinking 등)은 백엔드가 지원해야 동작 | (미확인) |

**보완책 후보 (Step 5에서 툴콜 깨지면 시도):**
- LiteLLM 모델 파라미터에 `stream: false` 강제 / Claude Code 스트리밍 회피.
- LiteLLM 대신 **네이티브 Anthropic `/v1/messages`를 직접 구현한 게이트웨이** 사용 →
  - **vLLM 내장 Anthropic 어댑터** ([docs](https://docs.vllm.ai/en/stable/serving/integrations/claude_code/))
  - **claude-code-router** (musistudio) — 로컬/OpenAI호환/Ollama 라우팅, 기본 :3456
    ([repo](https://github.com/musistudio/claude-code-router))
  - **claude-code-proxy** (nielspeter) — 경량 HTTP 프록시, tool/streaming/thinking 지원 표방
    ([repo](https://github.com/nielspeter/claude-code-proxy))
  - **Ollama 네이티브** — 2026-01-16부터 Anthropic Messages API 호환 발표(프록시 불필요,
    `ANTHROPIC_BASE_URL=http://localhost:11434`) (검색 요약)

---

## 두 갈래 길 (의사결정 — 진단 후 갱신)

> 진단 결과 LiteLLM 1.86.1의 `/v1/messages`는 mlx(chat-only)에 막다른 길로 **확정**됐다. 따라서 순위가 바뀐다.

1. **anthropic→chat 전용 프록시 (✅ 권장 1순위).** Claude Code 앞에 얇은 프록시를 한 겹 두고, 그 프록시가
   **이미 200이 확인된** LiteLLM `:4000` `/v1/chat/completions`(qwen-122b)를 백엔드로 본다.
   - 구조: `Claude Code → [anthropic→chat 프록시] → LiteLLM :4000 (qwen-122b) → mlx :8001`
   - 후보: **claude-code-proxy**(nielspeter, 경량 anthropic→chat, tool/stream/thinking 지원 표방,
     [repo](https://github.com/nielspeter/claude-code-proxy)) 또는 **claude-code-router**(musistudio,
     [repo](https://github.com/musistudio/claude-code-router)).
   - 이건 Codex 때 role-shim을 끼운 것과 **완전히 같은 발상**(번역 한 겹 추가). 네 LiteLLM·mlx는 그대로 둔다.
2. **LiteLLM 버전 교체 (비권장).** anthropic→chat 직접 번역을 하던 버전으로 바꾸는 방법은 있으나, 회귀
   위험 + 1.82.x는 멀웨어라 지뢰밭. 굳이 가지 말 것.
3. **mlx에 Responses API 부여 (오버킬).** 백엔드를 고치는 건 과하다.

---

## 체크리스트

- [ ] `litellm --version`이 1.82.7/1.82.8 **아님** 확인 (보안)
- [ ] `claude --version` 2.1.129+ 확인 (게이트웨이 디스커버리용)
- [ ] **Step 1**: `curl POST /v1/messages`로 anthropic→qwen 번역 성공 확인 ← 최우선
- [ ] (404면) mlx 직접 chat 호출로 백엔드/번역 문제 분리
- [ ] (필요시) `qwen-122b-claude` 모델 추가 + 게이트웨이 재시작
- [ ] 4개 env 설정 (`BASE_URL`/`AUTH_TOKEN`/`MODEL`/`DEFAULT_HAIKU_MODEL`)
- [ ] `claude -p "...pong"` 1턴 대화 확인
- [ ] `claude -p` 코딩 작업으로 **툴콜·파일쓰기** end-to-end 확인
- [ ] 툴콜 깨지면 스트리밍/프록시 보완책 적용

---

## 출처 (근거 링크)

**Claude Code 공식**
- LLM gateway 개요: https://code.claude.com/docs/en/llm-gateway
- 환경변수: https://code.claude.com/docs/en/env-vars
- 모델 설정: https://code.claude.com/docs/en/model-config

**LiteLLM**
- Use Claude Code with Non-Anthropic Models: https://docs.litellm.ai/docs/tutorials/claude_non_anthropic_models
- anthropic_unified (`/v1/messages`): https://docs.litellm.ai/docs/anthropic_unified/
- anthropic passthrough: https://docs.litellm.ai/docs/pass_through/anthropic_completion
- 알려진 버그: [#25321](https://github.com/BerriAI/litellm/issues/25321) · [#30014](https://github.com/BerriAI/litellm/issues/30014) · [#22249](https://github.com/BerriAI/litellm/issues/22249) · [#22930](https://github.com/BerriAI/litellm/issues/22930)

**Anthropic Messages API (프로토콜)**
- Messages API: https://platform.claude.com/docs/en/api/messages
- working with messages: https://platform.claude.com/docs/en/build-with-claude/working-with-messages

**대안 프록시**
- claude-code-router: https://github.com/musistudio/claude-code-router
- claude-code-proxy: https://github.com/nielspeter/claude-code-proxy
- vLLM × Claude Code: https://docs.vllm.ai/en/stable/serving/integrations/claude_code/

**참고 블로그/가이드**
- Connecting Claude Code to Local LLMs (Medium): https://medium.com/@michael.hannecke/connecting-claude-code-to-local-llms-two-practical-approaches-faa07f474b0f
- Claude Code with Local LLMs and ANTHROPIC_BASE_URL: https://renezander.com/guides/claude-code-local-llm-anthropic-base-url/

---

## 관련 메모 / 파일

- 형제 문서: `connect-codex-to-local-qwen122b.md` (같은 스택, Responses API 쪽)
- 시스템 메모리: `codex-qwen122b-wiring.md`, `codex-qwen-degeneration-modes.md`
- 핵심 파일:
  - `/Users/ohama/agent-stack/litellm/config.yaml` (필요시 `qwen-122b-claude` 추가)
  - `/Users/ohama/llm-system/role_shim.py` (:8011, role 문제 시 재활용)
  - `~/.claude/settings.json` (`env` 블록으로 위 환경변수 영구화 가능)
