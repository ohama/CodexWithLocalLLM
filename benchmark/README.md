# Benchmark — Codex vs OpenHands (로컬 qwen-122b)

같은 코딩 과제를 두 도구(**Codex CLI**, **OpenHands**)에 **동일 조건**(같은 모델 qwen-122b,
격리·순차)으로 시키고, 능력·시간·과정을 측정해 **재현·검증 가능한 형태**로 비교하는 하니스.

## 📖 문서 길잡이 (여기부터 읽으세요)

| 목적 | 문서 |
|------|------|
| 🟢 **처음 — 비교 검증 따라하기** | [START-HERE.md](START-HERE.md) (백엔드→연결→실행→읽기) |
| 결과를 **어떻게 해석**하나 | [INTERPRETING.md](INTERPRETING.md) (4지표 의미·표 읽는 순서·오독 주의) |
| **재현 레퍼런스** (명령별 효과) | [REPRODUCE.md](REPRODUCE.md) |
| **실제 결과** 데이터 | [RESULTS.md](RESULTS.md) |
| 이 파일 | 과제 정의·합격 기준·디렉터리 구조 (아래) |

## 실행 한눈에
```sh
export LITELLM_API_KEY=dummy
bash benchmark/run.sh codex l1        # 한 셀(도구,레벨)
bash benchmark/run-matrix.sh          # 전체 6셀(직렬, ~10-15분)
python3 benchmark/report.py           # → RESULTS.md
```

> 과제 텍스트는 `tasks/<level>/PROMPT.md` 한 곳에만(TASK-03), 채점기 `tasks/<level>/test.py`(stdlib
> 독립 judge)가 합격을 판정. 프롬프트·채점기는 도구 런너와 독립적이다.

## 복잡도 3단계 (검증된 과제 재사용)

이전에 실측·검증된 과제를 그대로 재사용한다: fib(단일 파일), wordstat(멀티 파일 CLI),
KV 스토어(멀티 모듈 서비스).

| Level | 만드는 것 | 정식 프롬프트 위치 | 복잡도 차원 |
|-------|-----------|--------------------|-------------|
| L1 | `fib.py` 한 파일의 피보나치 함수 | `tasks/l1-fib/PROMPT.md` | single-file |
| L2 | `wordstat.py` 단어 통계 CLI | `tasks/l2-wordstat/PROMPT.md` | multi-file CLI |
| L3 | `kvstore/` 패키지 + `cli.py` KV 서비스 | `tasks/l3-kvstore/PROMPT.md` | multi-module service |

## 레이아웃

```
benchmark/
  START-HERE.md / INTERPRETING.md / REPRODUCE.md / RESULTS.md  # 길잡이·해석·재현·결과
  README.md                       # 이 파일 (과제 정의 + 합격 기준 + 구조)
  run.sh                          # 한 셀(도구,레벨) 실행 — 격리·순차 락·비대화
  run-matrix.sh                   # 6셀 전체 매트릭스(직렬) → results.json
  score.py                        # 4지표 채점/측정 (run.sh가 자동 호출)
  report.py                       # results.json → RESULTS.md
  tasks/
    l1-fib/{PROMPT.md,test.py}    # 정식 프롬프트(단일 canonical) + stdlib 독립 채점기
    l2-wordstat/{PROMPT.md,test.py}
    l3-kvstore/{PROMPT.md,test.py}
  reference/<level>/              # 채점기 검증용 레퍼런스 해답
  .runs/                          # 실행 산출물(gitignore) — RESULTS.md가 영구 기록
```

각 레벨의 프롬프트는 위 `tasks/<level>/PROMPT.md` **단 한 곳에만** 존재한다(TASK-03).
도구별로 다른 문구를 쓰지 않는다.

## 합격 기준 (objective pass criterion, TASK-02)

레벨 X의 어떤 해답이 **합격**이라는 것은 다음 한 줄로 정의된다:

```
python3 benchmark/tasks/<level>/test.py <solution_dir>   # exit 0 → PASS
```

- 채점기가 **exit 0** 으로 끝나면 합격, **nonzero** 면 불합격이다.
- **도구의 자가 보고(self-report)는 신뢰하지 않는다.** "테스트 다 통과했다"는 도구의 말이 아니라,
  우리의 독립 채점기 종료 코드만이 합격을 결정한다(forward ref: MET-01, Phase 3).

## 공통 규약 (채점기가 의존하는 약속)

1. **채점기 호출:** `python3 tasks/<level>/test.py <solution_dir>` 형태로 실행한다.
   `<solution_dir>` 가 생략되면 현재 디렉터리(`.`)를 기본값으로 쓴다.
2. **종료 코드 계약:** `0` = 모든 검사 통과, `nonzero` = 한 개 이상 검사 실패.
3. **stdlib-only:** 과제와 채점기 모두 **파이썬 표준 라이브러리만** 사용한다(pip 설치 없음).
   이것이 재현성을 보장한다(PROJECT.md 제약).
4. **동일 프롬프트 규칙:** `PROMPT.md` 의 **정확한 텍스트를 모든 도구에 그대로(verbatim)** 먹인다.
   도구별 맞춤 문구는 없다(TASK-03).
5. **decoupling:** 프롬프트/테스트는 여기에 살고, 도구 런너(`run.sh`)와 독립적이다.
