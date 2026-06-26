# 여기서 시작 — Codex vs OpenHands 비교 검증 (초보자용)

처음 보는 사람이 **codex와 openhands를 같은 조건으로 비교 검증**하려면 이 문서 하나만 위에서
아래로 따라가면 된다. 각 단계는 "무엇을·왜" 한 줄 + 실제 명령으로 되어 있고, 더 깊은 내용은
해당 전용 문서로 링크한다.

> 큰 그림: **두 도구(codex, openhands)를 같은 로컬 모델(qwen-122b)에 연결 → 같은 3단계 과제를
> 동일 조건으로 시킴 → 성공·시간·과정을 자동 측정 → 비교 리포트로 읽기.**

전체 순서:
```
0. 백엔드(qwen-122b) 떠 있나      ─┐ 한 번만 셋업
1. codex 를 qwen-122b 에 연결      │  (이미 됐으면 건너뜀)
2. openhands 를 qwen-122b 에 연결  ─┘
3. 벤치마크 실행 (6셀 매트릭스)
4. 결과 읽기 / 해석
```

---

## 0. 백엔드가 떠 있는지 확인 (qwen-122b @ LiteLLM :4000)

두 도구 모두 로컬 LiteLLM 게이트웨이(:4000)를 통해 같은 qwen-122b를 쓴다. 먼저 살아있는지 확인:

```sh
curl -sf localhost:4000/v1/models -H "Authorization: Bearer dummy" >/dev/null && echo "gateway OK" || echo "gateway DOWN"
```
- **효과:** OK 면 백엔드 준비됨. DOWN 이면 백엔드 스택(LiteLLM :4000 + role-shim :8011 + mlx :8001)을
  먼저 띄워야 한다 → 배선/기동은 `../documentation/howto/connect-codex-to-local-qwen122b.md` 참고.
  (이 시스템에선 launchd 서비스 `com.ohama.litellm` / `com.ohama.role-shim` / `com.ohama.qwen122b`)

환경변수(게이트웨이 키, 아무 값이나 됨):
```sh
export LITELLM_API_KEY=dummy
```

---

## 1. codex 를 qwen-122b 에 연결 (한 번만)

이미 `codex` 가 로컬 qwen 으로 동작하면 건너뛴다. 확인:
```sh
grep -E '^[[:space:]]*model[[:space:]]*=' ~/.codex/config.toml   # qwen-122b-codex 가 보이면 연결됨
```
- 아직이면 → **[connect-codex-to-local-qwen122b](../documentation/howto/connect-codex-to-local-qwen122b.md)**
  를 따라 설치 + 연결(responses→chat 브릿지 + role-shim). 그 문서 하나로 codex 쪽은 끝난다.

---

## 2. openhands 를 qwen-122b 에 연결 (한 번만)

확인:
```sh
python3 -c "import json,os;print(json.load(open(os.path.expanduser('~/.openhands/agent_settings.json')))['llm']['model'])"
# → openai/qwen-122b 가 나오면 연결됨
```

아직이면 셋업(이 시스템 기준):

1. **설치** — OpenHands CLI (uv tool 로 설치되어 `~/.local/bin/openhands` 제공):
   ```sh
   openhands --version    # 이미 있으면 버전 출력
   # 없으면: uv tool install openhands   (또는 공식 설치 안내를 따른다)
   ```
2. **모델을 qwen-122b 로 지정** — `~/.openhands/agent_settings.json` 의 `llm` (그리고 `condenser.llm`)
   을 로컬 게이트웨이로:
   - `llm.model` = `openai/qwen-122b`
   - `llm.base_url` = `http://localhost:4000/v1`
   - `llm.api_key` = `dummy`
   설정 후 다시 확인 명령(위)으로 `openai/qwen-122b` 가 나오는지 본다.

> 왜 같은 모델? codex와 openhands를 **같은 qwen-122b** 로 맞춰야 "도구 차이"만 비교된다(모델 변수 제거).

---

## 3. 벤치마크 실행

연결이 끝났으면 한 줄로 한 셀을 먼저 시험:
```sh
bash benchmark/run.sh codex l1     # codex 에게 L1 과제를 시키고 채점까지
```
- **효과:** 격리 폴더 `benchmark/.runs/codex-l1-fib-<시각>/` 에 솔루션 + transcript.log + meta.json(4지표)
  를 남긴다. (openhands 도 `bash benchmark/run.sh openhands l1`)

전체 6셀(2 도구 × 3 레벨, 직렬, ~10–15분):
```sh
bash benchmark/run-matrix.sh       # 절대 백그라운드로 돌리지 말 것(단일 백엔드, 직렬)
python3 benchmark/report.py        # 결과 → benchmark/RESULTS.md 생성
```

> 명령별 효과·사전조건 검증·"처음부터 전부" 시퀀스의 **완전판은 → [REPRODUCE.md](REPRODUCE.md)**.
> 이 START-HERE 는 그 길잡이이고, 실제 재현 레퍼런스는 REPRODUCE.md 다.

⚠️ openhands 를 손으로 직접 부르지 말 것 — 반드시 `run.sh`/`run-matrix.sh` 로. (직접 호출 시
프롬프트 파일 위치로 출력이 새는 격리 버그가 있어, 러너가 인라인 방식으로 이를 막는다.)

---

## 4. 결과 읽기 / 해석

```sh
open benchmark/RESULTS.md     # 또는 에디터로 열기
```
- **도구 × 레벨 표**: 성공 여부 · 시간 · 단계수(step_method) · 산출 규모
- **레벨별 차이 요약** + **honesty note**(어떤 셀이 왜 실패/재측정됐는지)

읽을 때 주의:
- **성공/실패는 도구의 자기보고가 아니라 독립 judge 재실행 결과**다.
- **steps 숫자는 도구끼리 직접 비교 금지** — codex(‘exec’ 블록) vs openhands(agent 메시지)로 단위가 다르다.
  그래서 `step_method` 를 같이 본다.
- **결과는 실행마다 달라질 수 있다**(LLM 비결정성). `benchmark/.runs/` 는 git 에 안 올라가므로
  **RESULTS.md 가 유일하게 남는 기록**이다.

지표 의미·표 읽는 순서·흔한 오독을 자세히 → **[INTERPRETING.md](INTERPRETING.md)**.

해설/분석을 더 보고 싶으면 → **[../documentation/codex-hermes-openhands-comparison.md](../documentation/codex-hermes-openhands-comparison.md)**
(codex/hermes/openhands 동작 방식 비교).

---

## 막혔을 때

| 증상 | 확인 |
|------|------|
| `gateway DOWN` | 백엔드 스택 기동 (connect 문서) / `lsof -ti tcp:4000` |
| codex 가 멈춤(hang) | 러너가 `< /dev/null` 로 처리함 — 손으로 `codex exec` 할 땐 반드시 `< /dev/null` |
| openhands 출력이 run 폴더에 없음 | `run.sh` 로 돌렸는지 확인(손으로 `--file` 호출 금지) |
| 모델이 qwen-122b 가 아님 | 1·2단계 확인 명령 재실행 |

---

**한 줄 요약:** 백엔드 확인(0) → codex 연결(1) → openhands 연결(2) → `run-matrix.sh` + `report.py`(3)
→ `RESULTS.md` 읽기(4). 세부는 REPRODUCE.md, codex 배선은 connect 문서.
