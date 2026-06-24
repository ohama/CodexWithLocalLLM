---
created: 2026-06-24
description: 유튜브 "Codex 무료 사용법" 영상 분석과, 그 아이디어를 mlx+litellm 시스템에 맞게 변형·적용한 전 과정
---

# Codex를 로컬 qwen-122b로 연결하기

유튜브 영상의 "Ollama로 Codex 무료 쓰기" 아이디어를 그대로 따라 하지 않고, 이미 운영 중인
**mlx_lm.server + LiteLLM** 스택에 맞게 변형해서 OpenAI Codex CLI를 로컬 **qwen-122b**에 붙인
기록. 핵심은 영상이 감춘 두 개의 호환성 벽(Responses API 전환, mlx의 `developer` role 거부)을
어떻게 넘었는가이다.

---

## Part 1. 유튜브 영상 분석

### 영상 기본 정보
- **제목:** "OpenAI Codex를 완전 무료로 사용하는 방법 | 무료 AI 코딩 에이전트 완성!"
- **채널:** 조피디 연구소 (JoPD LAB)
- **유형:** Windows 기준 셋업 튜토리얼 (자막 약 4,800자)

### 영상이 주장하는 것
> Codex 데스크톱 앱에 **Ollama + 로컬 오픈모델(Gemma)**을 연동하면, OpenAI에 토큰 비용을
> 내지 않고 로컬 모델로 Codex를 "무료로" 쓸 수 있다.

### 영상의 단계 요약
1. **Codex 설치** — 공식 사이트에서 OS별 설치, 구글 계정 로그인.
2. **Ollama 설치** — 로컬 LLM 실행 플랫폼. **0.24 버전부터 Codex 연동 지원** (구버전이면 업데이트 필수).
3. **로컬 모델 다운로드** — 추천: 구글 Gemma, 중국 Qwen 계열. 영상은 Gemma 선택.
4. **연동** — CMD에서 `ollama launch codex app` → 모델 선택 → Codex 재시작.
   연동되면 요금제/업그레이드 버튼이 사라지고 추론 단계가 4→7단계로 표시됨.
5. **설정** — 작업 모드(코딩용), 로컬 접근 권한 3개 활성화, 브라우저 제어 + 크롬 확장, 승인 모드(승인요청/대신승인/전체권한).
6. **테스트** — 계산기(HTML), 테트리스 웹게임 생성 + 자가 검증 시연.
7. **되돌리기** — `ollama launch codex app --restore`로 원복.

### 비판적 분석 (영상이 흐리는 지점)

| 쟁점 | 실제 내용 |
|------|-----------|
| **"무료 Codex"의 실체** | OpenAI의 GPT가 공짜가 되는 게 아니다. Codex는 **에이전트 UI(껍데기)**로만 쓰고, 실제 추론은 로컬 모델이 한다. 품질 = 로컬 모델 성능. |
| **비용 ≠ 0의 이면** | API 토큰비는 0이지만 GPU/RAM을 점유한다. 영상의 모델도 7~20GB. |
| **모델명 오인식** | "Gemma4", "잼마포", "Qwen3.6", "GPT 5.5/5.4 mini"는 음성 자막 오류로 보임. 실제로는 Gemma 3 / Qwen3 등. |
| **권한 설정 주의** | 영상은 편의상 "전체 권한"을 권하지만, 에이전트가 PC 파일·브라우저를 자율 조작하게 됨. "승인 요청"부터 점진 상향이 안전. |
| **영상 본인의 결론** | "작은 Gemma 모델은 생각보다 똑똑하지 않았다" → **결국 로컬 모델 선택이 전부**라는 자백. |

### 한 줄 평가
"로컬 LLM을 Codex 인터페이스에 붙여 API 비용 없이 코딩 에이전트를 굴린다"는 **개념 증명**으로는
유효. 단, 제목의 "무료 Codex"는 과장이고, 핵심 변수는 **로컬 모델의 품질**이다.

---

## Part 2. 내 시스템에 맞게 변형·적용한 과정

### The Insight

영상의 본질은 "Codex(에이전트 하네스) + OpenAI 호환 로컬 백엔드"다. **Ollama는 그 백엔드의
한 구현일 뿐**이다. 나는 이미 더 강한 백엔드(Qwen3.5-MoE 122B, mlx_lm.server)와 OpenAI 호환
게이트웨이(LiteLLM)를 운영 중이므로, 영상을 그대로 따라 Ollama를 새로 깔 이유가 없다.
**"Ollama 자리에 내 스택을 끼운다"**가 변형의 핵심이다.

영상 대비 차이:

| 항목 | 영상 (입문용) | 내 시스템 |
|------|---------------|-----------|
| 추론 백엔드 | Ollama + Gemma(소형) | **Qwen3.5-MoE 122B** (4bit MLX, 65GB), mlx_lm.server |
| 게이트웨이 | Ollama 직접 연동 | **LiteLLM** OpenAI 호환 `:4000` (멀티모델 라우팅, launchd 관리) |
| 컨텍스트 | 모델별 소형 | **256K** 네이티브 |
| 모델 검증 | 계산기/테트리스 생성까지 | 병렬 툴콜·멀티턴·멀티스텝·self-repair까지 실측 |

### 사전 검증: 이 백엔드가 에이전트로 쓸 만한가

연결 전에 LiteLLM 게이트웨이(`localhost:4000`)로 qwen-122b의 에이전트 능력을 실측해 전부 통과.

- **병렬 툴콜** — 한 응답에 도구 2개 동시 호출, 인자 JSON 정확.
- **멀티턴 tool 루프** — tool 결과를 되돌려주면 최종 자연어 종합 (프롬프트 캐시 작동).
- **멀티스텝 코딩** — 파일 작성→실행→검증→종료. 시키지 않은 입력검증·추가 테스트까지.
- **self-repair** — 버그 위치를 안 알려줘도 실패 재현→소스 읽기→수정→재검증, 테스트 조작 안 함.

결론: qwen-122b는 로컬 코딩 에이전트로 1군. 연결할 가치가 충분.

### Recognition Pattern (이 변형이 필요한 신호)

다음을 만나면 "영상대로 Ollama"가 아니라 "내 스택에 브릿지"를 떠올려야 한다.

1. 이미 OpenAI 호환 로컬 서버(vLLM/mlx_lm/TGI 등)를 LiteLLM 등으로 노출하고 있다.
2. Codex 최신 버전이 **chat API를 거부**한다(`wire_api = "chat"` is no longer supported).
3. 백엔드가 **`developer` role을 거부**한다(`Unexpected message role.`).

### The Approach — 두 개의 벽

영상은 "그냥 연동된다"고 하지만, 최신 Codex + mlx 조합에는 두 개의 호환성 벽이 있다.
**LiteLLM 재시작만으로는 안 풀린다.** 각각을 한 계층씩 추가해 해결한다.

```
Codex 0.142 ──Responses API──▶ LiteLLM :4000 (qwen-122b-codex)
              ──responses→chat 브릿지──▶ role-shim :8011 (developer→system)
              ──▶ mlx_lm.server :8001 (qwen122b)
```

#### 벽 ①: Codex가 chat API를 버리고 Responses API만 쓴다
- 증상: `Error loading config.toml: wire_api = "chat" is no longer supported.`
- 원인: Codex 0.142가 `chat` wire_api 제거. 그런데 mlx 백엔드는 `/chat/completions`만 구현.
- 해결: LiteLLM이 들어온 Responses 요청을 chat/completions로 **번역(bridge)**하게 한다.
  모델 id를 `openai/chat_completions/...` prefix로 주면 LiteLLM이 responses→chat 브릿지를 켠다.

#### 벽 ②: mlx_lm.server가 Codex의 `developer` role을 거부한다
- 증상: 백엔드가 `{"error": "Unexpected message role."}` / `System message must be at the beginning.`
- 원인: Codex(Responses API)는 instructions를 **`developer` role**로 내보내는데,
  `mlx_lm.server`는 system/user/assistant/tool만 받고 system은 맨 앞만 허용.
- 해결: LiteLLM과 mlx 사이에 **role 변환 shim**을 끼워
  - 첫 메시지의 developer/system → `system`
  - 이후의 developer/system → `user` (순서 제약 보존)

### Step 1: Codex CLI 설치

```bash
npm install -g @openai/codex@0.142.0
codex --version   # codex-cli 0.142.0
```

> 영상의 "데스크톱 앱"이 아니라 **CLI**를 쓴다. 터미널/LiteLLM 워크플로우에 맞고,
> 커스텀 OpenAI 호환 엔드포인트를 config로 지정할 수 있기 때문.

### Step 2: role 변환 shim 작성

`/Users/ohama/llm-system/role_shim.py` — chat/completions 요청의 메시지 role만 고쳐
mlx로 그대로 흘려보내는 경량 프록시(스트리밍/SSE 패스스루 포함). 핵심 로직:

```python
def fix_messages(msgs):
    out = []
    for i, m in enumerate(msgs):
        if m.get("role") in ("developer", "system"):
            m = {**m, "role": "system" if i == 0 else "user"}
        out.append(m)
    return out
```

### Step 3: shim을 launchd 서비스로 등록

기존 서비스(`com.ohama.litellm`, `com.ohama.qwen122b`)와 동일한 패턴으로 영구화.

```bash
# ~/Library/LaunchAgents/com.ohama.role-shim.plist 작성 후
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.ohama.role-shim.plist
launchctl list | grep role-shim
```

plist 핵심: `role_shim.py --listen 8011 --upstream http://localhost:8001`, `KeepAlive=true`.

### Step 4: LiteLLM 공유 config에 브릿지 모델 추가

`/Users/ohama/agent-stack/litellm/config.yaml`에 **새 항목만 추가**(기존 항목 불변 → 기존 클라이언트 무영향).

```yaml
  # Codex(Responses API) 전용 — responses→chat 브릿지 + role-shim(:8011) → mlx(:8001)
  - model_name: qwen-122b-codex
    litellm_params:
      model: openai/chat_completions//Users/ohama/llm-system/models/qwen122b
      api_base: http://localhost:8011/v1   # ← role-shim을 가리킴
      api_key: dummy
```

포인트:
- `openai/chat_completions/` prefix = responses→chat 브릿지 스위치.
- `api_base`를 mlx(:8001)가 아니라 **shim(:8011)**으로 보낸다.

### Step 5: 게이트웨이 재시작 (1회, 무중단에 가깝게)

```bash
launchctl kickstart -k gui/$(id -u)/com.ohama.litellm   # ~3초 복구
curl -s localhost:4000/v1/models -H "Authorization: Bearer dummy"
# → qwen-35b, qwen-122b, qwen-local, qwen-122b-codex  (기존 + 신규)
```

> mlx_lm.server는 **재시작하지 않는다**(65GB 모델 재로딩 회피). shim은 그 앞단에만 끼우므로
> 모델 서버 무중단.

### Step 6: Codex를 게이트웨이에 연결

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

```bash
echo 'export LITELLM_API_KEY=dummy' >> ~/.zshrc   # LiteLLM은 아무 키나 허용
```

### Example — 동작 확인

```bash
codex exec --skip-git-repo-check --sandbox workspace-write \
  "Create factorial.py with factorial(n) and asserts, run it with python3."
```

결과: Codex가 `factorial.py` 작성 → 실행 → "All tests passed" 보고. (음수 입력 방어 코드까지 자동 추가)

검증 매트릭스:

| 항목 | 결과 |
|------|------|
| 기존 chat 클라이언트(`qwen-122b` 직결) | ✅ 그대로 동작 |
| `:4000` responses 브릿지 | ✅ |
| shim의 developer→system 변환 | ✅ |
| Codex 실전 코딩(작성·실행·보고) | ✅ |

### 사용법

```bash
codex                 # 대화형 (qwen-122b-codex 기본)
codex exec "..."      # 비대화형
```

---

## 체크리스트

- [ ] `npm install -g @openai/codex` 후 `codex --version` 확인
- [ ] 백엔드가 `developer` role을 받는지 확인 (`curl ... '{"role":"developer",...}'`) → 거부하면 shim 필요
- [ ] role-shim launchd 등록 + `launchctl list | grep role-shim`로 PID 확인
- [ ] LiteLLM config에 `openai/chat_completions/` 브릿지 항목 추가 (기존 항목 불변)
- [ ] `api_base`가 shim(:8011)을 가리키는지 확인
- [ ] 게이트웨이 재시작 후 기존 모델 + 신규 모델 모두 노출되는지 확인
- [ ] Codex config `wire_api = "responses"` + `env_key` 설정
- [ ] `codex exec`로 파일 생성/실행 end-to-end 검증

## 관련 메모

- 시스템 메모리: `codex-qwen122b-wiring.md` — 동일 배선의 요약 + 운영 명령
- 핵심 파일:
  - `~/.codex/config.toml`
  - `/Users/ohama/agent-stack/litellm/config.yaml` (`qwen-122b-codex` 항목)
  - `/Users/ohama/llm-system/role_shim.py`
  - `~/Library/LaunchAgents/com.ohama.role-shim.plist`
