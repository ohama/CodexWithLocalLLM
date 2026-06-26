# 재현 가이드 — Codex vs OpenHands 벤치마크 (REPRODUCE)

이 문서는 **벤치마크 전체를 문서만 보고 처음부터 재현**할 수 있게 한다. 모든 명령은
복사·붙여넣기 가능하고, 각 명령 바로 아래에 **그 명령이 무엇을 만드는지(effect)** 를 적었다.
한 곳(이 파일)에서: ① 사전조건 확인 → ② 명령별 효과 → ③ 처음부터 재실행 순서를 모두 다룬다.

## 무엇을 만드는가 (Overview)

이 가이드를 따르면, **하나의 로컬 `qwen-122b` 백엔드**에 두 코딩 도구(**Codex CLI**,
**OpenHands**)를 **완전히 동일한 조건**으로 돌려, 최종 산출물인 **`benchmark/RESULTS.md`**
(도구×레벨 비교 리포트)를 재현한다. 핵심 가치는 *숫자*가 아니라 *재현성*이다 — 같은 조건에서
같은 절차로 측정을 다시 돌릴 수 있다는 것.

처음 읽을 때 반드시 알아둘 두 가지:

- **직렬(serial) 실행만 한다.** mlx 백엔드가 하나뿐이라 한 번에 한 셀(cell)만 돌 수 있다.
  여러 셀을 동시에 돌리거나 `run-matrix.sh` 를 백그라운드(`&`)로 돌리지 말 것. `run.sh` 는
  `mkdir` 기반 뮤텍스(`.runs/.lock`)를 잡아 이를 강제한다(다른 실행이 잡고 있으면 exit 3).
- **`benchmark/.runs/` 는 gitignore** 되어 있다(`benchmark/.gitignore = .runs/`). 따라서
  원시 실행물(transcript/meta/results)은 보존되지 않는다. **유일하게 남는 기록은
  `benchmark/RESULTS.md`** 이며, 리포트를 다시 만든 뒤에는 이 파일을 커밋해야 한다.

## 사전조건 (Preconditions)

각 항목은 **실제 검증 명령 + 기대 출력 + 실패 시 대처**로 구성된다. 모두 `curl`/`grep`/
`python3`(표준 라이브러리)/`lsof` 만 쓴다 — `jq` 나 `pip` 설치는 필요 없다(stdlib-only 가
이 프로젝트의 재현성 제약이다).

### 0. 환경변수 — 게이트웨이 키

```bash
export LITELLM_API_KEY=dummy
```

효과: 하니스가 LiteLLM 게이트웨이에 붙을 때 쓰는 키. `run.sh` 는 미설정 시 `"dummy"` 로
기본값을 채우지만, 재현을 위해 **명시적으로 설정**해 두는 것을 권한다.

### 1. 백엔드 가동 (주 점검 — `run.sh` 가 프리플라이트하는 바로 그 검사)

```bash
curl -sf localhost:4000/v1/models -H "Authorization: Bearer dummy"
```

기대: **exit 0** 과 함께 JSON 모델 목록이 출력된다. 이게 되면 백엔드 체인이 살아 있는 것이다.
실패하면 LiteLLM 게이트웨이(:4000)가 죽어 있는 것이다. 장애 위치를 좁히려면 다음 체인을 기억하라:

```
LiteLLM :4000  ->  role-shim :8011  ->  mlx_lm.server :8001 (qwen-122b)
```

위 `curl` 이 실패할 때만 보조로 포트 리슨을 확인한다:

```bash
lsof -nP -iTCP:8011 -sTCP:LISTEN   # role-shim
lsof -nP -iTCP:8001 -sTCP:LISTEN   # mlx_lm.server (qwen-122b)
```

효과: 각 단(role-shim / mlx)이 LISTEN 중인지 보여준다 — 어느 단이 죽었는지 짚어낼 수 있다.

### 2. 모델 = qwen-122b (두 도구 같은 모델 = 공정성 기준, 오프라인 확인 가능)

```bash
grep -E '^[[:space:]]*model[[:space:]]*=' ~/.codex/config.toml
```

기대: `model = "qwen-122b-codex"`

```bash
python3 -c "import json;print(json.load(open(__import__('os').path.expanduser('~/.openhands/agent_settings.json')))['llm']['model'])"
```

기대: `openai/qwen-122b`

효과: 두 도구의 설정이 같은 `qwen-122b` 백엔드를 가리키는지 **백엔드를 깨우지 않고** 확인한다.
둘 다 `base_url http://localhost:4000/v1` 을 쓰며, 단지 모델 문자열 표기만 도구별로 다르다.

### 3. 도구 설치 확인

```bash
codex --version
openhands --version
```

기대: 둘 다 버전 문자열을 출력하고 정상 종료한다(예: `codex-cli 0.142.0`,
`OpenHands CLI 1.16.0`). 둘 중 하나라도 실패하면 해당 도구가 PATH 에 없는 것이다.

## 벤치마크 실행 (Running the benchmark)

위에서 아래로 그대로 따라 읽으면 된다. 각 단계는 명령 한 블록 + 그 효과 + 만들어지는 산출물로 이루어진다.

### 1단계 — 단일 셀 실행

```bash
bash benchmark/run.sh <tool> <level>
```

- `<tool>` = `codex` | `openhands`
- `<level>` = `l1`|`l1-fib`|`1` (fib) · `l2`|`l2-wordstat`|`2` (wordstat) · `l3`|`l3-kvstore`|`3` (kvstore)

효과: 고정된 `tasks/<level>/PROMPT.md` 를 **그대로(verbatim)** 도구에 먹인다. 실행은 매번
**새로 격리된 디렉터리** `benchmark/.runs/<tool>-<level>-<stamp>/` 에서, **직렬 mkdir-lock**
아래(다른 실행이 잡고 있으면 exit 3), :4000 의 `qwen-122b` 를 상대로 이루어진다. codex 는
`< /dev/null` 과 함께 돌고(stdin-hang 가드), openhands 는 인라인 `--task ... --headless` 로
돌며 작업 디렉터리는 `OPENHANDS_WORK_DIR` 로 RUN_DIR 에 고정된다(파일 경로 앵커를 쓰지 않는다).
실행이 끝나면 `transcript.log` + `meta.json` 을 쓰고, 이어서 `score.py` 를 자동 호출해
`meta.json` 에 네 지표(`passed` / `duration_seconds` / `steps[step_method]` / `files`+`loc`)를
채운다. 마지막 요약(summary)이 그 지표들을 그대로 echo 한다.

레벨별 예상 소요(무엇을 기대해야 하는지):

```
L1 ~30-50s · L2 ~100-145s · L3 ~145s+
```

(codex 의 L3 는 진짜로 FAIL/truncate 날 수 있다 — 아래 Caveats 참조.)

### 2단계 — 전체 매트릭스 (6셀)

```bash
bash benchmark/run-matrix.sh
```

효과: `(tool, level)` 조합마다 `run.sh` 를 **엄격히 직렬로**, tool-major 순서(codex l1/l2/l3 →
openhands l1/l2/l3)로 한 번씩 호출한다. **절대 백그라운드(`&`)로 돌리지 말 것** — 백엔드가
하나라 한 번에 한 셀만 가능하다. 결과는 `benchmark/.runs/matrix-<stamp>/` 에 쌓인다:
`results.json`(집계 지표), `manifest.txt`, 그리고 셀마다 `<tool>-<level>.console.log`. 한 셀이
실패해도(`passed=false`) 그것은 **유효한 기록**이지 중단 사유가 아니다. 총 소요 ~10-15분.

### 3단계 — 리포트 생성

```bash
python3 benchmark/report.py
```

효과: 가장 최신 `benchmark/.runs/matrix-*/results.json` 을 자동으로 찾아 `benchmark/RESULTS.md`
를 쓴다(도구×레벨 표: 성공/시간/`steps[step_method]`/크기 + transcript 발췌 + 레벨별 차이).
순수 포매팅이라 어떤 에이전트/채점기도 다시 돌리지 않는다(LLM 시간 0). **idempotent** —
같은 `results.json` 이면 byte-identical 한 RESULTS.md 가 나온다. 선택 인자로 특정 results.json
이나 매트릭스 디렉터리를 줄 수 있다:

```bash
python3 benchmark/report.py benchmark/.runs/matrix-<stamp>/
```

### 4단계 — 결과 읽기

```bash
# benchmark/RESULTS.md 를 연다
```

효과: 커밋되는, 자기 완결적인 비교 리포트다. 이것이 당신이 보존/공유하는 산출물이다.

### 주의 — openhands 를 직접 호출하지 말 것

이 가이드의 모든 실행은 **반드시 `run.sh` 를 거친다.** openhands 를 손으로 직접 돌리되
PROMPT.md 를 가리키는
`--file`
플래그를 넘기는 방식은 금지한다. 그렇게 하면 openhands 가 그 파일이 있는 디렉터리(정식 task
폴더)로 작업 디렉터리를 앵커링해, 격리된 RUN_DIR 바깥(정식 task 폴더)으로 산출물이 새어 나간다
(Phase 4 에서 관측된 버그). `run.sh` 는 프롬프트를 인라인 `--task` 로 먹이므로 이 누수가 없다.

## 처음부터 전부 재현 (Reproduce everything from scratch)

깨끗한 체크아웃에서 **이 순서 하나만** 따르면 측정 전체가 재현된다(REPRO-03):

```bash
# 1. 게이트웨이 키 설정
export LITELLM_API_KEY=dummy

# 2. 사전조건 확인 — 위 "사전조건(Preconditions)" 섹션의 검사들을 그대로 실행해
#    게이트웨이(:4000), 모델(qwen-122b x2), 도구(codex/openhands) 가 OK 인지 확인

# 3. 전체 매트릭스 (6셀, 직렬, ~10-15분) — 절대 백그라운드 금지
bash benchmark/run-matrix.sh

# 4. 리포트 생성 -> benchmark/RESULTS.md
python3 benchmark/report.py

# 5. benchmark/RESULTS.md 를 열어 확인하고 커밋한다
#    (.runs/ 는 gitignore 되므로 RESULTS.md 가 유일하게 남는 기록이다)
```

단일 셀만 빠르게 돌려보려면:

```bash
bash benchmark/run.sh <tool> <level>
```

## Caveats / 정직성 노트

재실행자가 놀라지 않도록, 알아야 할 것들:

- **LLM 비결정성(nondeterminism):** 성공 여부·시간·스텝 수는 실행마다 달라진다. 당신의 숫자가
  커밋된 `RESULTS.md` 와 다를 수 있다 — 정상이다. 우리가 보장하는 것은 *숫자*가 아니라 *절차*다.
- **스텝 단위가 도구마다 다르다(step_method):** codex 는 `exec` 툴콜 블록 수, openhands 는
  `Number of agent messages` 수다. **원시 스텝 수를 같은 단위로 비교하지 말 것.**
- **`benchmark/.runs/` 는 gitignore** 된다 → `RESULTS.md` 가 유일한 영속 기록이다. `report.py`
  실행 후 **반드시 커밋**하라.
- **codex L3(kvstore) truncation 은 알려진 실제 결과**다(진짜 FAIL — `mkdir kvstore` 만 하고
  0f/0loc). 하니스 버그가 아니다.
- **직렬 전용:** mlx 백엔드가 하나뿐이라 한 번에 한 셀만. `run-matrix.sh` 를 절대 백그라운드로
  돌리지 말 것.
