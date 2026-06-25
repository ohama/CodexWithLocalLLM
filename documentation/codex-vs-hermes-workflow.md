# Codex vs Hermes — 대형 코딩 요청의 Research → Planning → Execute 비교

사용자가 큰 코딩 요청을 줬을 때, **Codex CLI** 와 **Hermes Agent** 가 각각 어떻게
(1) 이해/조사(research), (2) 분해/계획(planning), (3) 실행/검증(execute) 하는지 비교한 리서치 문서.
이 시스템(로컬 qwen-122b 공유)에 설치된 실제 도구 기준으로 조사했다.

> 참고용 제3 기준으로, 이 문서를 만들게 한 **GSD**(get-shit-done) 방법론도 끝에 짧게 대비한다.

---

## 한눈 비교

| 축 | **Codex CLI** | **Hermes Agent** |
|----|---------------|------------------|
| 기본 모델 | **단일 에이전트** 반복 루프 (Responses API) | **프레임워크/플랫폼** (Kanban 커널 + 다중 구성요소) |
| Research | 내장 없음 — 루프 안에서 파일 읽기·명령 실행으로 즉석 조사 | `kanban specify`(아이디어→스펙), 보조 LLM으로 명세화 |
| Planning | **inline 플랜**(`update_plan` 투두) — 세션 내 가벼운 단계 목록 | `kanban decompose`(작업→자식 task 그래프), `swarm`(plan→workers→verifier) |
| Execute | 도구 호출 반복(shell/apply_patch) + 샌드박스/승인 | Kanban task 그래프 진행 + **goals 루프(Ralph)** + 병렬 워커 |
| 병렬성 | 기본 없음 (세션 `fork` 로 수동 병렬) | **swarm**: 병렬 specialist 워커 + verifier 토폴로지 |
| 상태 지속 | 세션 단위(resume/fork/archive) | **영속 Kanban DB**(task 그래프), goals, state.db |
| 사람 개입 | 승인 모드(untrusted/on-failure/never) | 블루프린트 폼/대화, 프로파일 로스터, 대시보드 |
| 대형 프로젝트 적합성 | 단일 컨텍스트 한계 → 수동 분할 의존 | 구조적 분해·병렬·지속 추적에 유리 |

핵심 한 줄: **Codex는 "잘 실행하는 단일 에이전트", Hermes는 "분해·오케스트레이션 프레임워크"** 다.

---

## Codex CLI — 단일 에이전트, inline 플랜

### Research
- 별도 리서치 단계/아티팩트가 **없다**. 에이전트가 작업 루프 안에서 필요할 때 파일을 읽고(`cat`/grep),
  명령을 실행해 스스로 맥락을 파악한다. (이번 세션의 self-repair에서 `실행→실패→소스 읽기→수정`이 그 예)
- 표준 지침은 **`AGENTS.md`** 로 주입(프로젝트 규약·빌드 방법 등)을 상시 참고.

### Planning
- 내장 **plan 도구(`update_plan`)** 로 세션 내에 단계 목록(투두)을 세우고 체크해 나간다.
  (테트리스/멀티파일 예제에서 "Setting up a plan… → ✓ step" 출력으로 관측됨)
- 이 플랜은 **세션 휘발성**이다 — 영속 로드맵/페이즈 구조가 아니라 그때그때의 작업 목록.

### Execute
- Responses API 루프: 모델이 도구 호출(shell, apply_patch) → Codex가 로컬 실행 → 결과 반영 → 반복.
- **샌드박스**(read-only/workspace-write/danger-full-access) × **승인 모드**(untrusted/on-failure/on-request/never).
- 자가 검증: 테스트/명령을 직접 돌려 확인. `review` 서브커맨드로 비대화형 코드리뷰.
- 연속성: `resume`/`fork`/`archive` 로 세션 이어가기·분기. `apply` 로 마지막 diff를 git apply.

### 대형 프로젝트에서
- 본질이 **하나의 에이전트 + 하나의 컨텍스트**. 큰 작업은 사람이 작업을 쪼개 여러 세션으로 돌리거나,
  `fork` 로 병렬화하고, `AGENTS.md`/`/clear` 로 컨텍스트를 관리해야 한다.
- 자동 분해·병렬 오케스트레이션·영속 작업그래프는 **없다**. 단순·예측가능·디버깅 쉬움이 강점.

---

## Hermes Agent — 분해 · 스웜 · goals 루프

### Research / Spec
- **`kanban specify`**: Triage 칼럼의 한 줄 아이디어를 보조 LLM으로 **실제 스펙**(제목 정리 + 상세)으로 확장.
- 즉 "막연한 요청 → 구체 명세"를 명시적 단계로 만든다(Codex엔 없는 단계).

### Planning / Decompose
- **`kanban decompose`**: 한 triage task를 **자식 task 그래프**로 펼친다. 프로파일 로스터(역할군)를 읽어
  보조 LLM에게 task 그래프(JSON)를 요청 → 자식들을 원자적으로 생성·링크하고 root를 `triage→todo`로 전환.
- **`kanban swarm`**: 추가 스케줄러 없이 Kanban 위에 토폴로지를 쓴다 —
  `planning root → 병렬 specialist 워커들 → verifier(워커 완료 후)`.
- 계획이 **영속 Kanban DB의 task 그래프**로 남는다(세션 휘발 아님).

### Execute
- **goals (Ralph 루프)**: 사용자 목표를 세션에 고정해두고, 매 턴 후 "이 목표가 충족됐나?"를 보조 모델이
  판정 → 미충족이면 계속 continuation 프롬프트를 넣어 **목표 달성/예산 소진까지 자동 반복**.
- Kanban task들이 그래프 순서대로 진행, swarm은 병렬 워커 + verifier로 검증.
- 주변 기능: **blueprints**(자동화 템플릿), **skills**, **cron**(스케줄), **MCP**, **profiles**(다중 페르소나),
  웹 UI(8787/8788) + Tailscale 원격.

### 대형 프로젝트에서
- triage → specify → decompose(task 그래프) → swarm(병렬+verifier) → goals 루프, **영속 Kanban으로 추적**.
- 구조적 분해·병렬·장기 목표 유지에 유리하나, 구성요소가 많아 **복잡·학습비용·디버깅 난이도**가 높다.

---

## (참고) GSD 와의 대비

GSD는 **사람-주도 + 문서-우선**의 가장 명시적인 파이프라인이다:
`research(4 병렬 에이전트) → requirements → roadmap(phases) → plan-phase → execute-phase(waves) → verify`,
모든 산출물을 `.planning/`에 영속화하고 단계마다 승인 게이트를 둔다.

- **Codex**: 계획이 암묵적(세션 내), 사람 개입은 승인 수준 → 빠르고 가벼움.
- **Hermes**: 계획이 Kanban 그래프로 명시·영속, 자동 분해/스웜 → 자율 오케스트레이션.
- **GSD**: 계획이 사람이 읽는 문서로 명시·영속, 단계별 승인 → 통제·추적 최강, 가장 무거움.

축으로 보면 **암묵적·빠름(Codex) ↔ 자동 분해·자율(Hermes) ↔ 문서·승인 주도(GSD)**.

---

## 결론 / 언제 무엇을

| 상황 | 권장 |
|------|------|
| 단일 파일~중간 작업, 빠른 반복, 직접 통제 | **Codex** (단순·예측가능, 로컬 qwen으로 비용 0) |
| 큰 작업을 자동으로 분해·병렬 실행, 장기 목표 유지 | **Hermes** (decompose/swarm/goals) |
| 사람이 단계마다 검토·승인하며 추적해야 하는 프로젝트 | **GSD** (문서·게이트) |

**조합도 가능**: GSD/Hermes로 분해·계획 → 각 단위 실행은 Codex(또는 Hermes 워커)에 위임.
세 도구 모두 이 시스템에선 **동일한 LiteLLM :4000 → qwen-122b** 를 공유하므로 백엔드는 한 곳이다.

### blueCode(자체 코딩 에이전트) 설계 시사점
- 큰 요청 처리력 = "분해 + 상태 지속 + (선택)병렬 + 검증" 의 유무. Codex의 inline 플랜은 가볍지만
  대형엔 약하고, Hermes의 Kanban 분해/goals 루프가 대형의 핵심 차별점이다.
- blueCode가 대형 작업을 노린다면 최소한 **(a) 요청→스펙화, (b) task 그래프 분해, (c) 목표-충족 판정 루프**
  세 가지를 갖추는 것이 codex 대비 의미 있는 진전이 된다(Hermes가 이미 그 형태).

---

## 실측 검증 (2026-06-25)

동일 과제를 두 도구에 줘서 실제 동작을 대조했다 — *"todo CLI 앱(add/list/done/remove, JSON 영속,
argparse) + unittest 작성 후 실행"* (둘 다 로컬 qwen-122b, 새 디렉터리).

| | **Codex** (`codex exec`) | **Hermes** (`hermes -z` oneshot) |
|---|---|---|
| 결과물 | todo.py(111줄) + test_todo.py | todo.py(104줄) + test_todo.py |
| 테스트 | **9 tests OK** | **9 tests OK** |
| CLI 동작 | 정상(add/list/done) | 정상(add/list/done) |
| 관측된 방식 | **inline 플랜 3단계**(todo 작성→test 작성→실행) 세우고 ✓ 체크하며 exec, 자가검증 | 단일 패스, **최종 요약만 출력**(중간 도구단계 비표시) |

**핵심 발견 — 단일 요청에선 Codex ≈ Hermes(oneshot):**
- 둘 다 *단일 에이전트*로 곧장 빌드했고, 결과 품질도 동등(각 9테스트 통과).
- **Hermes의 차별 기능(`kanban specify/decompose/swarm`, `goals` 루프)은 oneshot에서 작동하지 않았다.**
  이들은 `hermes kanban …` 등 **명시적으로 호출해야** 발동하는 경로다.
- 즉 위 비교표의 "Hermes = 분해/스웜" 우위는 **대형·다단계 작업에서 그 경로를 명시 호출할 때** 드러나며,
  *기본 단발 요청*에서는 codex exec 와 사실상 같은 단일-에이전트 행동을 한다.

**시사점:** "큰 프로젝트"의 분해·병렬·지속 추적 이점은 도구를 *그 모드로 구동*해야 얻는다.
단순 단발 요청이면 더 가벼운 Codex로 충분하다.

---
*조사 기준: 이 시스템 설치본 — Codex CLI 0.142.0, Hermes Agent v0.16.0. 비교표 일부는 소스/도움말 기반, "실측 검증"은 실제 실행 결과.*
