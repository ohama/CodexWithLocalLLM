# Codex vs Hermes vs OpenHands — 같은 과제 3자 비교

세 로컬 코딩 에이전트(**Codex CLI**, **Hermes Agent**, **OpenHands**)에게 **완전히 동일한 과제**를
주고 실제로 빌드시켜 비교한 문서. 모두 이 시스템의 **로컬 qwen-122b**(LiteLLM :4000) 백엔드로 통일해
모델 변수를 제거하고 **도구/워크플로우 차이**만 비교했다.

> 과제(동일): 다중 모듈 **KV 스토어 서비스** — `kvstore/`(storage·server·client) + `cli.py` +
> 단위/통합 테스트, stdlib만, `python3 -m unittest discover` 로 전부 통과시킬 것.
> Codex/Hermes 비교의 심화는 → `codex-vs-hermes-workflow.md`.

---

## 공정성 — 같은 모델로 맞춤

세 도구 모두 같은 LiteLLM 게이트웨이(`localhost:4000`)를 쓴다. OpenHands도
**`qwen-122b`로 설정**(`~/.openhands/agent_settings.json`의 `llm.model`/`condenser.llm.model`)되어,
세 도구 모두 **qwen-122b** 기준으로 비교했다.

---

## 결과 (실측, 2026-06-26)

| | **Codex** (`codex exec`) | **Hermes** (`hermes -z`) | **OpenHands** (`--headless`) |
|---|---|---|---|
| 파일 | 7 | 8 | 7 |
| 코드 규모 | 530줄 | 565줄 | 625줄 |
| 테스트 | **통과** (독립검증 OK) | **통과** | **18 tests OK** (독립검증) |
| 결과물 정돈 | 깔끔 | `:memory:` 잔여 | `:memory:` 잔여 |
| 모델 | qwen-122b | qwen-122b | qwen-122b |

**→ 세 도구 모두 동일 과제를 완성**(테스트 통과하는 멀티모듈 KV 서비스). qwen-122b로 통일하니
**산출물 품질은 사실상 대등**하다.

---

## 동작 방식의 차이 (핵심)

겉보기 결과는 비슷하지만, **어떻게 일하는가**가 다르다.

### Codex CLI — 단일 에이전트 + inline 플랜
- `codex exec "<task>"` 한 번. 세션 안에서 **명시적 단계 플랜**(todo)을 세우고 `→/✓` 로 진행.
- shell/apply_patch 도구 반복, **자가검증**(테스트 직접 실행) + 실패 시 자가수정.
- 계획은 **세션 휘발성**. 샌드박스/승인 모드로 권한 제어. 가볍고 예측가능.

### Hermes Agent — 단발은 단일, 진짜 힘은 분해 모드
- `hermes -z "<task>"`(oneshot)는 Codex처럼 단일 에이전트로 빌드(동급).
- **차별점은 명시 호출하는 kanban 경로**: `kanban decompose`(task 그래프 분해) →
  `kanban swarm`(병렬 워커+verifier+synthesizer) → 워커들이 각 모듈 실행 → 통합.
- 계획이 **영속 Kanban(SQLite) task 그래프**로 남고 의존성·상태 추적. (실측: 분해→워커 직렬 실행으로
  20테스트 통과 앱 완성 — `codex-vs-hermes-workflow.md` 참고.)

### OpenHands — 단일 에이전트 + action/observation 루프
- `openhands --task "<task>" --headless` 로 자동승인 실행.
- **에이전트 런타임**(파일 편집·bash 실행을 action으로 내고 observation을 받는 루프)이 핵심.
  내장 **condenser**(컨텍스트 압축 LLM)로 긴 작업의 컨텍스트를 관리 — 세 도구 중 유일.
- 단일 컨텍스트에서 끝까지 빌드(Codex와 유사한 모놀리식), 다만 **TUI/웹/ACP** 등 surface가 다양하고
  대화 영속(`--resume <id>`)을 강조.

---

## 세 도구 한눈 표

| 축 | Codex | Hermes | OpenHands |
|----|-------|--------|-----------|
| 기본 형태 | 단일 에이전트 | 프레임워크(Kanban) | 에이전트 런타임 |
| 계획 | inline(휘발) | Kanban 그래프(영속) | 루프(휘발) + condenser |
| 분해/병렬 | 수동(fork) | **decompose/swarm** | 수동 |
| 컨텍스트 관리 | /clear·세션 | 세션·task | **condenser(자동 압축)** |
| 연속성 | resume/fork | kanban·sessions | resume |
| surface | CLI(+desktop) | CLI/웹/텔레그램/MCP | **CLI/TUI/웹/ACP** |
| 권한 | 샌드박스×승인 | 프로파일·블루프린트 | headless 자동승인 등 |
| 무게 | 가벼움 | 무거움(구성요소 多) | 중간 |

---

## 결론 / 언제 무엇을

| 상황 | 권장 |
|------|------|
| 빠른 단발~중간 작업, 직접 통제, 가벼움 | **Codex** |
| 큰 작업의 구조적 분해·병렬·영속 추적 | **Hermes**(kanban 모드 명시 구동) |
| 긴 컨텍스트 작업, 다양한 surface(웹/IDE/ACP), 자동 압축 | **OpenHands** |

**공통점:** 세 도구 다 이 시스템에선 **동일한 LiteLLM :4000 → 로컬 qwen** 을 공유한다(백엔드 1곳,
비용 0). 차이는 *모델*이 아니라 *오케스트레이션·컨텍스트 관리·surface* 다.

**비교의 한계(정직하게):**
- 단일 과제(KV 스토어) 한 건 기준. 더 크고 모호한 과제일수록 Hermes 분해/ OpenHands condenser의
  이점이 커질 수 있다.
- 세 도구 모두 qwen-122b 기준. 더 작은 모델(예: qwen-35b)로 바꾸면 속도는 빨라지되 품질은 모델만큼 달라진다.
- 토큰/시간은 도구별 로그 형식이 달라 정밀 수치 비교는 생략(Codex만 ~849k 관측).

---
*조사 기준: Codex CLI 0.142.0, Hermes Agent v0.16.0, OpenHands(uv tool 설치). 모두 qwen-122b/LiteLLM:4000. 2026-06-26.*
