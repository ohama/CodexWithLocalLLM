# Hermes Agent — 이 시스템에서의 동작 / 연결 구조

이 머신에 설치된 **Hermes Agent**(NousResearch, v0.16.0)가 어떻게 구성되고, CLI·웹서버·로컬
LLM이 어떻게 연결되는지 정리한 문서. (프레임워크 일반론이 아니라 *이 시스템의 실제 배선* 기준)

---

## 한눈에

```
[터미널] hermes (CLI) ─┐
                       ├─▶ hermes-agent (~/.hermes/hermes-agent, config: ~/.hermes/config.yaml)
[브라우저/폰] Web UI ──┘            │
                                   ▼  provider = custom:litellm
                         LiteLLM 게이트웨이  http://localhost:4000/v1   (model: qwen-122b)
                                   ▼
                         role-shim :8011 → mlx_lm.server :8001 (Qwen3.5-MoE 122B)
```

- **CLI와 웹 UI가 같은 agent + 같은 config** 를 쓰고, LLM은 **Codex와 동일한 LiteLLM :4000** 으로 간다.
- 로컬 모델이라 토큰 비용 0, 데이터 로컬.

---

## 구성 요소

### 1) CLI — `hermes`
- 진입점: `~/.local/bin/hermes` → (PYTHONPATH/HOME 정리 후) `~/.hermes/hermes-agent/venv/bin/hermes` 실행.
- 버전: **Hermes Agent v0.16.0** (2026.6.5), Python 3.11, 프로젝트 `~/.hermes/hermes-agent`.
- 본체: `hermes_cli/`(거대 모듈군 — config, gateway, models, kanban, skills, service_manager 등).

### 2) Agent 본체 / 상태
- 코드: `~/.hermes/hermes-agent/` (git 저장소, upstream NousResearch).
- 설정: `~/.hermes/config.yaml` (모델·툴셋·세션 등). 비밀값: `~/.hermes/.env`.
- 상태/데이터: `~/.hermes/` 아래
  - `state.db`(~15MB), `sessions/`, `kanban.db`, `skills/`, `agents/`, `memories/`, `logs/`, `cron/`.

### 3) 웹 서버 2종 (launchd, 상시 실행)
| 서비스(launchd) | 포트 | 실행 | 역할 |
|---|---|---|---|
| `com.ohama.hermes-webui` | **8787** | `~/hermes-webui/bootstrap.py` | NousResearch 공식 **Hermes Web UI** |
| `com.ohama.hermes-for-web` | **8788** | `~/hermes-for-web/server.py` | 커스텀 **Hermes for Web**(브라우저 조종석, reallygood83). `HERMES_WEBUI_AGENT_DIR=~/.hermes/hermes-agent` 로 같은 agent 사용 |

둘 다 `~/.hermes/hermes-agent/venv` 파이썬으로 돌고, 같은 agent/config를 통해 **동일한 qwen-122b** 를 구동한다.

---

## 로컬 LLM 연결 (핵심)

`~/.hermes/config.yaml` 상단:
```yaml
model:
  default: qwen-122b
  provider: custom:litellm
  context_length: 65536
  base_url: http://localhost:4000/v1
providers: {}
```

- **provider `custom:litellm` + base_url :4000** → Hermes의 모든 LLM 호출이 LiteLLM 게이트웨이로 간다.
- LiteLLM이 `qwen-122b` 를 role-shim(:8011) 거쳐 `mlx_lm.server`(:8001)로 라우팅 → 로컬 Qwen3.5-MoE 122B.
- 즉 **Codex와 동일한 로컬 LLM 백엔드를 공유**한다. (별도 API 키 불필요 — litellm은 dummy 키)
- `config.yaml.bak.20260528_pre_litellm` 백업이 있어, 2026-05-28경 litellm 연동으로 전환됐음을 알 수 있다.
- 대안 경로(설정에 흔적): DeepSeek 클라우드 키(webui 서비스 env), Qwen OAuth(`~/.qwen/oauth_creds.json`) — 현재 기본은 로컬 litellm.

---

## 서버 & 원격 접속 (Tailscale)

두 웹 UI 모두 Tailscale 로 **tailnet 내부에만** 노출(외부 공개 아님):

```
https://ohama-2.tail318f12.ts.net          → 127.0.0.1:8787  (hermes-webui)
https://ohama-2.tail318f12.ts.net:10000    → 127.0.0.1:8788  (hermes-for-web)
```

→ 폰/다른 기기에서 Tailscale 로 붙으면 브라우저로 Hermes를 조작할 수 있다(로컬 qwen-122b 사용).

---

## 실행 / 관리

```sh
# 상태 확인
launchctl list | grep com.ohama.hermes
lsof -nP -iTCP:8787 -sTCP:LISTEN ; lsof -nP -iTCP:8788 -sTCP:LISTEN

# 재시작
launchctl kickstart -k gui/$(id -u)/com.ohama.hermes-webui
launchctl kickstart -k gui/$(id -u)/com.ohama.hermes-for-web

# CLI
hermes --version
hermes            # 대화형 (필요 시 tmux-cli-session 패턴으로 디렉터리별 세션 운용 가능)
```

로그:
- webui: `~/.hermes/webui/launchd.out.log`
- for-web: `~/.local/state/launchd-logs/com.ohama.hermes-for-web.{out,err}.log`

---

## 비밀값 위치 (값은 기록 안 함)

- `~/.hermes/.env` — 프로바이더 키/토큰 다수.
- `com.ohama.hermes-webui` plist 의 `EnvironmentVariables` — `DEEPSEEK_API_KEY` 등.
- `~/.hermes/auth.json` — 인증 상태.
- LiteLLM(:4000) 경유 로컬 모델은 키가 필요 없다(dummy).

---

## 의존 관계 요약

- Hermes(CLI+웹) → **LiteLLM :4000**(launchd `com.ohama.litellm`) → **role-shim :8011** → **mlx_lm.server :8001**(launchd `com.ohama.qwen122b`).
- 이 LiteLLM 게이트웨이는 Codex 등 다른 도구와 **공유**된다(같은 :4000). 게이트웨이/모델 서버를
  내리면 Hermes의 로컬 LLM 응답도 멈춘다.
