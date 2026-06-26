# 6. 벤치마크 수행

이제 실제로 두 도구에 과제를 시킨다. 모든 실행은 저장소 루트(`/Users/ohama/projs/codex`)에서 한다.

```sh
export LITELLM_API_KEY=dummy   # 아직 안 했으면
```

## 과제 6종 (난이도 + 도메인)

| 레벨 | 과제 | 무엇을 보나 |
|------|------|-------------|
| **L1** | `fib(n)` 단일 파일 | 함수 한 개를 정확히 |
| **L2** | `wordstat` 멀티파일 CLI | 여러 파일 협력 + 표준출력 계약 |
| **L3** | KV 스토어 멀티모듈 서비스 | 패키지 구조 + 프로세스 간 영속성 |
| **L4** | `calc` 산술식 평가 CLI | 파서·우선순위·괄호 (`eval` 금지) |
| **L5** | `todo` 할 일 관리 CLI | 서브커맨드 + JSON 영속 + 종료코드 |
| **L6** | `csvstat` CSV 통계 CLI | CSV 파싱 + 수치 집계 + 에러처리 |

> 각 과제의 결과물(파일 리스트)·기능·사용법은 [2장](02-tasks.md) 및 `benchmark/tasks/<level>/ABOUT.md` 참고.

각 과제의 프롬프트는 `benchmark/tasks/<level>/PROMPT.md` 한 곳에만 있고, 두 도구에 **글자 그대로
동일하게** 주어진다. judge `benchmark/tasks/<level>/test.py` 는 도구가 못 보는 **숨은 judge**다.

## ① 한 셀 먼저 시험

전체를 돌리기 전에, 한 칸(한 도구 × 한 레벨)을 먼저 돌려 흐름을 본다:

```sh
bash benchmark/run.sh codex l1
```
- **효과:** codex에게 L1 과제를 시키고 → 격리 폴더 `benchmark/.runs/codex-l1-fib-<시각>/` 에
  솔루션 + `transcript.log`(대화 기록) + `meta.json`(4지표) 을 남긴다 → 채점까지 자동.

openhands도 똑같이:
```sh
bash benchmark/run.sh openhands l1
```

> 한 셀은 보통 30초~수분. L3가 가장 오래 걸린다.

## ② 전체 매트릭스 (6칸)

두 도구 × 세 레벨 = 6칸을 **순서대로(직렬)** 돌린다:

```sh
bash benchmark/run-matrix.sh
```
- **효과:** codex L1..L6, 이어서 openhands L1..L6 순으로 한 번에 하나씩 실행하고, 12개 결과를
  하나의 `results.json` 으로 모은다. 전체 ~10–15분.
- ⚠️ **절대 백그라운드(`&`)로 돌리지 말 것.** 로컬 백엔드가 하나라 동시에 두 개를 돌리면 서로
  경합한다. 러너가 직렬을 강제하지만, 사람이 백그라운드로 띄우면 깨질 수 있다.

## ③ 리포트 생성

```sh
python3 benchmark/report.py
```
- **효과:** `results.json` 을 읽어 사람이 읽는 리포트 `benchmark/RESULTS.md` 를 만든다(표 + 각 실행
  transcript 발췌 + 레벨별 차이 + honesty note).
- `benchmark/.runs/` 는 git에 올라가지 않으므로 **`RESULTS.md` 가 그 실행의 유일한 영구 기록**이다.

## ④ 결과 열기

```sh
open benchmark/RESULTS.md     # 또는 에디터로 연다
```

여기까지가 "수행"이다. **이 표를 어떻게 읽어야 하는지**가 다음 장의 핵심이다 →
[7. 결과 해석](07-interpret.md).

## 한 줄 요약

```sh
export LITELLM_API_KEY=dummy
bash benchmark/run-matrix.sh     # 6칸 실행 (직렬, ~10-15분)
python3 benchmark/report.py      # → benchmark/RESULTS.md
```
