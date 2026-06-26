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
