# Benchmark — 고정 과제 정의 (Codex vs OpenHands)

같은 과제를 두 코딩 도구(**Codex CLI**, **OpenHands**)에 **완전히 동일한 조건**으로
던지고, 그 산출물을 **재현·검증 가능한 형태**로 채점하기 위한 **정식 과제 정의** 묶음이다.
모델 변수를 제거하기 위해 두 도구 모두 동일한 로컬 `qwen-122b` 백엔드를 쓴다(런너는 Phase 2).

여기 들어 있는 것은 **과제 텍스트(PROMPT.md)뿐**이다. 채점기(test.py)와 검증용 레퍼런스 해답은
Plan 02에서 추가된다. 이 디렉터리는 어떤 도구 런너와도 독립적이다(decoupling).

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
  README.md                       # 이 파일 (합격 기준 + 공통 규약)
  tasks/
    l1-fib/PROMPT.md              # L1 정식 프롬프트 (단일 canonical 위치)
    l2-wordstat/PROMPT.md         # L2 정식 프롬프트
    l3-kvstore/PROMPT.md          # L3 정식 프롬프트
    <level>/test.py               # 채점기(judge) — Plan 02에서 추가
  reference/<level>/              # 채점기 검증용 레퍼런스 해답 — Plan 02에서 추가
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

## 공통 규약 (Plan 02 채점기가 의존하는 약속)

1. **채점기 호출:** `python3 tasks/<level>/test.py <solution_dir>` 형태로 실행한다.
   `<solution_dir>` 가 생략되면 현재 디렉터리(`.`)를 기본값으로 쓴다.
2. **종료 코드 계약:** `0` = 모든 검사 통과, `nonzero` = 한 개 이상 검사 실패.
3. **stdlib-only:** 과제와 채점기 모두 **파이썬 표준 라이브러리만** 사용한다(pip 설치 없음).
   이것이 재현성을 보장한다(PROJECT.md 제약).
4. **동일 프롬프트 규칙:** `PROMPT.md` 의 **정확한 텍스트를 모든 도구에 그대로(verbatim)** 먹인다.
   도구별 맞춤 문구는 없다(TASK-03).
5. **decoupling:** 프롬프트/테스트는 여기에 살고, 어떤 도구 런너와도 독립적이다(런너는 Phase 2).
