# Codex 테스트 — 입력 → 출력 모음

각 레벨에서 **무엇을 시키면(입력) → 무엇이 나오는지(출력)**를 실제 실행 결과로 보여준다.
스크립트(`levels/*.sh`)를 읽지 않아도 이 문서만으로 테스트 내용을 파악할 수 있다.

> 아래 출력은 로컬 **qwen-122b**로 실제 실행해 얻은 결과다. 실행하려면:
> `cd examples/codex-tests && ./run.sh 03` (번호는 레벨).

---

## Level 1 — 스모크 (배선 생존 확인)

**입력**
```bash
codex exec --sandbox read-only "Reply with exactly: CODEX_OK and nothing else."
```

**출력**
```
user> Reply with exactly: CODEX_OK and nothing else.
codex> CODEX_OK
```

**무엇을 보나** — 폰/PC에서 Codex→LiteLLM→shim→mlx 경로가 살아있고 모델이 응답하는지.
✅ `CODEX_OK` 가 보이면 통과.

---

## Level 2 — 셸 도구 사용 (명령 실행·보고)

**입력**
```bash
codex exec --sandbox read-only \
  "Run the command 'python3 --version' and report the exact version string it prints."
```

**출력**
```
codex> The command `python3 --version` outputs: Python 3.14.6
```

**무엇을 보나** — 모델이 추측이 아니라 **실제로 명령을 실행**해서 결과를 가져오는지(도구 사용).
✅ 시스템의 진짜 파이썬 버전을 보고하면 통과.

---

## Level 3 — 단일 파일 코딩

**입력**
```bash
codex exec --sandbox workspace-write \
  "Create fib.py with a function fib(n) (fib(0)=0, fib(1)=1) plus a few assert tests
   covering fib(0), fib(1), and fib(10)==55. Then run it with 'python3 fib.py'."
```

**출력** (콘솔)
```
All tests passed!
fib(0) = 0
fib(1) = 1
fib(10) = 55
```

**생성 결과** — `fib.py`
```python
def fib(n):
    """Compute the nth Fibonacci number where fib(0)=0, fib(1)=1."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

# Test cases
assert fib(0) == 0, "fib(0) should be 0"
assert fib(1) == 1, "fib(1) should be 1"
assert fib(10) == 55, "fib(10) should be 55"
print("All tests passed!")
```

**무엇을 보나** — 함수 작성 → 테스트 작성 → 실행까지. ✅ 반복(iterative) 구현 + 테스트 통과.

---

## Level 4 — 멀티스텝 프로젝트 (CLI 도구)

**입력**
```bash
codex exec --sandbox workspace-write \
  "Build a CLI 'wordstat.py' (stdlib only): read a text file from argv[1], print total word
   count, unique word count, and top 5 frequent words (case-insensitive, ignore punctuation).
   Create sample.txt, write test_wordstat.py, run the tests, then run wordstat.py on sample.txt."
```

**출력** (콘솔)
```
Total word count: 41
Unique word count: 27
Top 5 most frequent words:
  the: 7
  quick: 3
  fox: 2
  dog: 2
  and: 2
```

**생성 결과** — `wordstat.py` (핵심부)
```python
import sys, re
from collections import Counter

def count_words(text: str) -> list[str]:
    return re.findall(r'\w+', text.lower())          # 소문자화 + 단어만 추출

def get_word_stats(text: str) -> dict:
    words = count_words(text)
    return {'total': len(words), 'unique': len(set(words)),
            'top_5': Counter(words).most_common(5)}
# main(): argv 검증 → 파일 읽기(에러 처리) → 통계 출력
```

**무엇을 보나** — 도구 작성 + 샘플 + 테스트 + 실행을 **한 번에 여러 단계**로. 시키지 않은
인자 검증·파일 에러 처리까지 추가. ✅ 테스트 통과 + 실제 통계 출력.

---

## Level 5 — 디버깅 / 자가수정 (버그 위치 미고지)

심어둔 버그(입력 파일):
```python
# stats.py  (BEFORE — 일부러 틀려 있음)
def mean(nums):
    return sum(nums) // len(nums)        # BUG: 정수 나눗셈
def median(nums):
    s = sorted(nums); n = len(s)
    return s[n // 2]                      # BUG: 짝수 길이에서 두 중앙값 평균 누락
```

**입력**
```bash
codex exec --sandbox workspace-write \
  "stats.py and test_stats.py exist. 'python3 test_stats.py' is FAILING. Find why, fix the
   bug(s) in stats.py only (don't touch the test), iterate until all tests pass, then summarize."
```

**출력** (Codex 요약)
```
진단:
  1) mean 이 정수 나눗셈(//) → mean([1,2,3,4]) 이 2 (정답 2.5)
  2) median 이 짝수 길이에서 두 중앙값 평균을 안 냄
수정:
  1) //  →  /
  2) 짝수일 때 (s[mid-1] + s[mid]) / 2
독립 재검증: All tests passed!
```

**생성 결과** — `stats.py` (AFTER)
```python
def mean(nums):
    return sum(nums) / len(nums)

def median(nums):
    s = sorted(nums); n = len(s); mid = n // 2
    return s[mid] if n % 2 == 1 else (s[mid - 1] + s[mid]) / 2
```

**무엇을 보나** — 실행→실패확인→소스읽기→수정→재검증의 **디버깅 루프**를 스스로.
✅ 버그 2개 모두 수정, **테스트 파일은 건드리지 않음**(꼼수 없음).

---

## Level 6 — 멀티파일 패키지

**입력**
```bash
codex exec --sandbox workspace-write \
  "Create package 'mathpkg' with mathpkg/__init__.py (export add/sub/mul), mathpkg/ops.py
   (implement them), tests/test_ops.py (unittest). Run 'python3 -m unittest discover -s tests'."
```

**출력** (콘솔)
```
...
----------------------------------------------------------------------
Ran 3 tests in 0.000s
OK
```

**생성 결과** — 파일 트리
```
mathpkg/__init__.py     from .ops import add, sub, mul ; __all__ = [...]
mathpkg/ops.py          def add/sub/mul(a, b): ...
tests/test_ops.py       unittest: test_add / test_sub / test_mul (각 3케이스)
```

**무엇을 보나** — 여러 파일에 걸친 **패키지 구조**를 만들고 import 관계·테스트까지 정합.
✅ 3개 테스트 통과.

---

## 요약 표

| 레벨 | 입력 한 줄 | 통과 신호 |
|------|-----------|-----------|
| 1 스모크 | "CODEX_OK 라고만 답해" | `CODEX_OK` |
| 2 셸 | "python3 --version 실행해서 보고" | 실제 버전 보고 |
| 3 단일파일 | "fib.py + 테스트 만들고 실행" | 테스트 통과 |
| 4 멀티스텝 | "wordstat CLI + 샘플 + 테스트 + 실행" | 통계 출력 + 통과 |
| 5 자가수정 | "실패하는 테스트 보고 버그 고쳐" | All tests passed |
| 6 멀티파일 | "mathpkg 패키지 + unittest" | Ran 3 tests OK |

직접 실행 → `./run.sh` (전체) 또는 `./run.sh 05` (특정). 자세한 구조·응용은 [README](README.md).
