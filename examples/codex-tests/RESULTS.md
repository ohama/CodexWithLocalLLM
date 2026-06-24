# 실행 결과 기록 (RESULTS)

**돌려보지 않아도** 각 테스트가 실제로 어떻게 동작하는지 알 수 있도록, 6개 레벨을 모두 실행해
**실제 입력과 출력 전체**를 그대로 옮긴 기록이다.

- 실행일: **2026-06-24**
- 모델: `qwen-122b-codex` (LiteLLM :4000 → role-shim :8011 → mlx_lm.server :8001)
- Codex: v0.142.0 · approval: never · sandbox: 레벨별
- 결과: **6/6 통과** (Level 4는 모델이 스스로 3회 실패→디버깅→통과)

> 요약본만 보려면 [EXAMPLES.md](EXAMPLES.md), 직접 실행은 `./run.sh`.

---

## Level 1 — 스모크 (read-only)

**입력**
```
$ codex exec --sandbox read-only "Reply with exactly: CODEX_OK and nothing else."
```

**출력**
```
user> Reply with exactly: CODEX_OK and nothing else.
codex> CODEX_OK
(tokens used: 10,908)
```

✅ 배선 생존 + 모델 응답 확인.

---

## Level 2 — 셸 도구 사용 (read-only)

**입력**
```
$ codex exec --sandbox read-only \
    "Run the command 'python3 --version' and report the exact version string it prints."
```

**출력 (transcript)**
```
codex> I'll run the command to check the Python version.

exec  /bin/zsh -lc 'python3 --version'
  succeeded in 0ms:
  Python 3.14.6

codex> The command `python3 --version` outputs: **Python 3.14.6**
(tokens used: 22,000)
```

✅ 추측이 아니라 **실제로 명령을 실행**해서 보고.

---

## Level 3 — 단일 파일 코딩 (workspace-write)

**입력**
```
$ codex exec --sandbox workspace-write \
    "Create fib.py with fib(n) (fib(0)=0, fib(1)=1) plus asserts for fib(0),fib(1),fib(10)==55.
     Then run it with 'python3 fib.py' and show the output."
```

**출력 (transcript)**
```
codex> I'll create `fib.py` with the Fibonacci function and tests, then run it.

exec  cat > fib.py << 'EOF' ... EOF        # 파일 작성
  succeeded in 0ms

exec  /bin/zsh -lc 'python3 fib.py'
  succeeded in 0ms:
  All tests passed!
  fib(0) = 0
  fib(1) = 1
  fib(10) = 55

codex> Perfect! The `fib.py` file has been created and all tests pass.
(tokens used: 35,025)
```

**생성 파일 — `fib.py`**
```python
def fib(n):
    """Compute the nth Fibonacci number."""
    if n == 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

assert fib(0) == 0, "fib(0) should be 0"
assert fib(1) == 1, "fib(1) should be 1"
assert fib(10) == 55, "fib(10) should be 55"
print("All tests passed!")
```

✅ 작성 → 실행 → 통과.

---

## Level 4 — 멀티스텝 프로젝트 (workspace-write) — *실제 자가 디버깅 포함*

**입력**
```
$ codex exec --sandbox workspace-write \
    "Build a CLI 'wordstat.py' (stdlib only): read argv[1] text file, print total/unique word
     count and top 5 frequent words (case-insensitive, ignore punctuation). Create sample.txt,
     write test_wordstat.py, run the tests, then run wordstat.py on sample.txt."
```

**출력 (transcript 요지 — 실패→수정 반복이 실제로 일어남)**
```
exec  cat > wordstat.py ...            # 1차 작성
exec  cat > test_wordstat.py ...
exec  python3 test_wordstat.py
  exited 1                              # ❌ 테스트 실패
exec  python3 -c "import re; print(re.findall(r'[a-zA-Z0-9]+', 'hello, world! ...'))"
                                        # 정규식 동작을 직접 실험하며 원인 조사
exec  python3 test_wordstat.py
  exited 1                              # ❌ 또 실패
exec  cat > wordstat.py ...            # 로직 수정
exec  python3 test_wordstat.py
  succeeded:  (All 7 tests passed)      # ✅ 통과
exec  python3 wordstat.py sample.txt
  succeeded:
  Total word count: 26
  Unique word count: 17
  Top 5 most frequent words:
    the: 4
    quick: 3
    fox: 3
    brown: 2
    dog: 2
(tokens used: 264,254  ·  테스트 실패 3회 후 자력 통과)
```

✅ 도구 작성 + 샘플 + 테스트 + 실행을 멀티스텝으로. **테스트가 실패하자 정규식을 직접
실험하며 디버깅해 7개 전부 통과**시킴(미리 짜인 정답이 아님).

---

## Level 5 — 디버깅 / 자가수정 (workspace-write)

심어둔 버그 (입력 파일 `stats.py`):
```python
def mean(nums):
    return sum(nums) // len(nums)        # BUG: 정수 나눗셈
def median(nums):
    s = sorted(nums); n = len(s)
    return s[n // 2]                      # BUG: 짝수 길이 평균 누락
```

**입력**
```
$ codex exec --sandbox workspace-write \
    "stats.py and test_stats.py exist. 'python3 test_stats.py' is FAILING. Find why, fix the
     bug(s) in stats.py only (don't touch the test), iterate until all pass, then summarize."
```

**출력 (transcript)**
```
exec  python3 test_stats.py
  exited 1:
  AssertionError: mean wrong: 2          # 실패 재현

exec  cat stats.py                       # 소스 직접 읽어 원인 조사
  (정수나눗셈 // , median 미처리 확인)

codex> Found the bugs! ...
exec  cat > stats.py << 'EOF' ... EOF     # 두 버그 동시 수정

exec  python3 test_stats.py
  succeeded:  All tests passed!           # ✅

codex> ## Summary
  1) mean: //  →  /
  2) median: 짝수일 때 (s[mid-1]+s[mid])/2
(tokens used: 71,007)

▶ 독립 재검증:  All tests passed!
```

✅ 실행→실패확인→소스읽기→수정→재검증 루프. 버그 2개 수정, **테스트 파일 미수정**(꼼수 없음).

---

## Level 6 — 멀티파일 패키지 (workspace-write)

**입력**
```
$ codex exec --sandbox workspace-write \
    "Create package 'mathpkg' with mathpkg/__init__.py (export add/sub/mul), mathpkg/ops.py
     (implement), tests/test_ops.py (unittest). Run 'python3 -m unittest discover -s tests'."
```

**출력 (transcript)**
```
codex> Setting up a plan...
  → Create mathpkg/__init__.py
  • Create mathpkg/ops.py
  • Create tests/test_ops.py
  • Run tests

exec  mkdir -p mathpkg tests
exec  cat > mathpkg/ops.py ...
exec  cat > mathpkg/__init__.py ...
exec  cat > tests/test_ops.py ...
exec  python3 -m unittest discover -s tests
  succeeded:
  ...
  ----------------------------------------------------------------------
  Ran 3 tests in 0.000s
  OK

codex> All 3 tests pass.  (mathpkg/ops.py, __init__.py, tests/test_ops.py)
(tokens used: 133,760)
```

**생성 트리**
```
mathpkg/__init__.py     from .ops import add, sub, mul ; __all__ = ['add','sub','mul']
mathpkg/ops.py          def add/sub/mul(a, b)
tests/test_ops.py       unittest: test_add / test_sub / test_mul (각 3케이스)
```

✅ 여러 파일에 걸친 패키지 + import 관계 + unittest. **계획(plan) 세우고 단계별 실행** 후 통과.

---

## 한눈에 (이번 실행 기준)

| 레벨 | 입력 | 결과 | tokens |
|------|------|------|--------|
| 1 스모크 | "CODEX_OK만 답해" | `CODEX_OK` | 10,908 |
| 2 셸 | "python3 --version 실행·보고" | `Python 3.14.6` | 22,000 |
| 3 단일파일 | "fib.py + 테스트 + 실행" | fib(10)=55, 통과 | 35,025 |
| 4 멀티스텝 | "wordstat CLI + 샘플 + 테스트" | 7 tests pass (실패3회→자가수정) | 264,254 |
| 5 자가수정 | "실패 테스트 보고 버그 고쳐" | 버그2개 수정, All pass | 71,007 |
| 6 멀티파일 | "mathpkg 패키지 + unittest" | Ran 3 tests OK | 133,760 |

전부 로컬 qwen-122b로 비용 0. 모델/설정을 바꾼 뒤 같은 레벨을 다시 돌려 이 기록과 비교하면
**능력 회귀 테스트**로도 쓸 수 있다.
