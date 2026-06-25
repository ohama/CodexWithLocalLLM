# Hermes Swarm 실행 따라하기 (초보자용)

큰 작업을 **여러 개의 작은 작업(task)으로 쪼개고, 워커(worker)들이 각자 실행**해 하나의 앱으로
합치는 Hermes의 "swarm/kanban" 방식을 **한 줄씩 따라 하며** 익히는 문서.

이 문서대로 하면 작은 멀티파일 앱(키-값 저장소)을 만들고 테스트까지 통과시킨다.
**모든 명령에 "무슨 일이 일어나는지"를 함께 적었다.**

> 전제: 이 시스템엔 `hermes` CLI가 설치돼 있고(`hermes --version`), 로컬 모델(qwen-122b)이
> LiteLLM(:4000)으로 연결돼 있다. 명령은 터미널에서 실행한다.

---

## 0. 큰 그림 (용어 30초)

| 용어 | 뜻 |
|------|----|
| **kanban** | 작업들을 칸(todo/ready/running/done)으로 관리하는 보드. SQLite에 영속 저장. |
| **task** | 하나의 작업 카드(예: "storage.py 만들기"). |
| **worker** | task 하나를 실제로 수행하는 Hermes 에이전트 프로세스. |
| **decompose** | 큰 task를 자식 task들로 자동 분해. |
| **swarm** | 병렬 워커 + 검증자(verifier) + 통합자(synthesizer) 토폴로지. |
| **workspace** | 워커가 파일을 만드는 작업 폴더. |

흐름: **큰 요청 → (분해) 작은 task들 → 워커가 각각 실행 → 합쳐서 완성**.

---

## 1. 준비

```sh
hermes --version
```
**효과:** Hermes가 설치돼 있는지 확인(버전이 찍히면 OK).

```sh
hermes kanban init
```
**효과:** 작업 보드 DB(`~/.hermes/kanban.db`)가 없으면 만든다(있으면 그대로). 여러 번 실행해도 안전.

작업 폴더(워커가 파일을 만들 곳)를 정한다. **절대경로**로 둔다:
```sh
export WS="$HOME/swarm-demo"      # 원하는 경로로
mkdir -p "$WS"
```
**효과:** 결과물이 모일 폴더를 만든다. (Hermes 기본 워크스페이스는 작업 끝나면 삭제되므로,
직접 지정한 폴더를 써야 산출물이 남는다.)

> 이 튜토리얼은 작업들을 `--tenant swarm-demo` 라는 이름표로 묶는다(나중에 한꺼번에 정리하기 쉽게).

---

## 2. (선택) 큰 요청을 자동 분해해 보기

먼저 큰 요청을 하나의 task로 만든다:
```sh
hermes kanban create "KV store service" \
  --body "Build a key-value store: storage module, HTTP server, client, CLI, tests." \
  --tenant swarm-demo --triage --json
```
**효과:** "KV store service" task를 **triage 칸**(아직 다듬어지지 않은 아이디어)으로 만든다.
출력 JSON에서 `"id": "t_xxxxxxxx"` 가 이 task의 ID다. **이 ID를 복사**해 둔다.

```sh
hermes kanban decompose t_xxxxxxxx --tenant swarm-demo --json
```
**효과:** 그 task를 **자식 task들로 자동 분해**한다(예: storage / server / client+cli / tests).
출력에 `"child_ids": [...]` 로 생성된 자식들이 나온다.

```sh
hermes kanban list --tenant swarm-demo
```
**효과:** 보드를 보여준다. 부모(`todo`) 밑에 자식들이 `ready`(바로 실행 가능)로 생긴 걸 확인.

> 여기까지가 "계획" 단계다. Codex의 휘발성 inline 플랜과 달리, **분해 결과가 보드에 영속**으로 남는다.

---

## 3. 워커를 실제로 실행해 파일을 만든다 (핵심)

분해된 task들을 워커가 수행하게 한다. **이 시스템에선 워커를 "포그라운드"로 하나씩 돌리는 게 가장
안정적이다**(이유는 맨 아래 "주의" 참고).

각 task에 대해 아래 한 줄을 실행한다 (`<ID>` 자리에 task ID):
```sh
cd "$WS"
hermes -p default --accept-hooks --skills kanban-worker \
  --toolsets file,terminal,kanban,code_execution,todo \
  chat -q "work kanban task <ID>"
```
**효과(이 한 줄이 하는 일):**
- `-p default` : 기본 프로파일(역할)로 실행.
- `--skills kanban-worker` : "보드의 task를 처리하는 워커" 행동을 로드.
- `--toolsets file,terminal,kanban,code_execution,todo` : 파일 쓰기/명령 실행/보드 갱신 도구를 켠다.
- `chat -q "work kanban task <ID>"` : "이 task를 처리하라"고 지시(조용히 실행).
- → 워커가 **계획 세우기 → 파일 작성 → 직접 실행/검증 → `hermes kanban complete` 호출**까지 자동 수행.
  끝나면 그 task가 `done`이 되고, `$WS`에 파일이 생긴다.

자식 task가 4개라면 위 명령을 **ID만 바꿔 4번** 실행한다(하나 끝나고 다음). 같은 `$WS`에 쌓이므로
뒤 워커는 앞 워커가 만든 파일을 보고 이어서 작업한다(예: 서버가 storage를 import).

진행 확인:
```sh
hermes kanban list --tenant swarm-demo     # done/running 확인
ls "$WS"                                     # 생긴 파일 확인
```
**효과:** task 상태와 실제 산출 파일을 본다.

---

## 4. 결과 검증

```sh
cd "$WS"
python3 -m unittest discover -s tests -v
```
**효과:** 워커가 만든 테스트를 직접 돌려 통과를 확인한다(`OK` 가 나오면 성공).

(이 튜토리얼의 실제 실행 결과: storage/server/client/cli + 테스트 20개 → `Ran 20 tests — OK`.)

---

## 5. (참고) 진짜 "병렬"로 띄우는 명령

병렬 토폴로지를 만들고 한 번에 스폰하는 경로도 있다(개념 확인용):
```sh
hermes kanban swarm "Build a KV store service" \
  --worker "default:Implement storage.py" \
  --worker "default:Build HTTP server" \
  --worker "default:Client and CLI" \
  --worker "default:Tests" \
  --verifier default --synthesizer default --tenant swarm-demo --json
```
**효과:** 루트(즉시 done) + **병렬 워커 4** + 검증자/통합자(의존 대기) 그래프를 만든다.

```sh
hermes kanban dispatch --dry-run
```
**효과:** **실제로 띄우지 않고**, 어떤 워커가 동시에 스폰될지 미리 보여준다(`Spawned: 4`).

```sh
hermes kanban dispatch --max 4
```
**효과:** ready 워커들을 **동시에 스폰**한다.

> ⚠️ 단, 이 방식(분리 실행)은 환경에 따라 워커가 일찍 죽을 수 있고(아래 주의), 로컬 모델이 하나면
> 동시에 띄워도 모델에서 직렬 처리된다. **확실히 따라 하려면 3절의 포그라운드 방식**을 권한다.

---

## 6. 정리(청소)

```sh
hermes kanban list --tenant swarm-demo                    # 남은 task 확인
hermes kanban reclaim <ID>                                 # 'running'에 멈춘 워커 풀어주기
hermes kanban archive <ID>                                 # task 보관(보드에서 치움)
```
**효과:** `reclaim`은 죽은 워커가 점유한 task를 다시 풀고, `archive`는 끝난 task를 보드에서 정리한다.
실습용 task들을 ID마다 archive 하면 보드가 깨끗해진다.

---

## 주의 (이 시스템 특이사항)

- **포그라운드로 실행하라.** 디스패처/백그라운드(`&`, 데몬)로 띄운 워커는 이 환경(터미널 미연결)에서
  산출물 없이 일찍 종료됐다. **터미널에서 직접 실행한 워커는 정상 완주**한다.
- **로컬 모델이 하나면 동시성 이득이 없다.** 워커 여럿이 qwen-122b 하나를 공유 → 모델에서 직렬.
  그래서 **워커를 하나씩(직렬) 돌리는 게 안정적**이다. 진짜 병렬 가속은 워커마다 다른 백엔드가 필요.
- 워크스페이스를 직접 지정(`$WS`)하지 않으면 산출물이 작업 종료 시 삭제된다.

---

## 한 줄 요약

`init → create → decompose`(계획) → 각 task를 `hermes … chat -q "work kanban task <ID>"`(포그라운드)로
실행 → `python3 -m unittest`로 검증 → `archive`로 정리.

(개념·Codex와의 비교는 → `codex-vs-hermes-workflow.md`)
