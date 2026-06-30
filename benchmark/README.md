# Benchmark — 로컬 qwen 코딩 에이전트 비교 (Codex · OpenHands · Claude Code)

같은 코딩 과제를 여러 에이전트에 **동일 조건**(같은 로컬 qwen 백엔드, 격리·순차)으로 시키고,
능력·시간·과정을 측정해 **재현·검증 가능한 형태**로 비교하는 하니스.

지원 도구(`run.sh <tool>`):

| tool | 클라이언트 | 모델 | 비고 |
|------|-----------|------|------|
| `codex` | Codex CLI | qwen-122b | Responses→chat 경유 |
| `openhands` | OpenHands | qwen-122b | |
| `qclaude` | Claude Code (`--model opus`) | **qwen-122b** | claude-code-proxy 경유, codex와 동일 weights |
| `qclaude35` | Claude Code (`--model sonnet`) | **qwen-35b** | 빠른 tier |

> **공정성:** `codex`와 `qclaude`는 *같은 122b weights*(role-shim→mlx :8001)를 쓴다 — 차이는
> 클라이언트/API 번역 경로뿐. `qclaude` vs `qclaude35`는 *같은 클라이언트, 다른 모델 크기*(122b vs 35b).

## 📖 문서 길잡이 (여기부터 읽으세요)

| 목적 | 문서 |
|------|------|
| 🟢 **처음 — 비교 검증 따라하기** | [START-HERE.md](START-HERE.md) (백엔드→연결→실행→읽기) |
| 결과를 **어떻게 해석**하나 | [INTERPRETING.md](INTERPRETING.md) (4지표 의미·표 읽는 순서·오독 주의) |
| **재현 레퍼런스** (명령별 효과) | [REPRODUCE.md](REPRODUCE.md) |
| **실제 결과** — codex vs openhands (14셀) | [RESULTS.md](RESULTS.md) |
| **실제 결과** — codex vs qclaude·qclaude35 (3자, qwen) | [RESULTS-3way-qwen.md](RESULTS-3way-qwen.md) · 분석 [RESULTS-3way-notes.md](RESULTS-3way-notes.md) |
| **실제 결과** — codex vs qclaude (2자, 122b) | [RESULTS-qclaude-vs-codex.md](RESULTS-qclaude-vs-codex.md) |
| 이 파일 | 과제 정의·합격 기준·디렉터리 구조 (아래) |

## 실행 한눈에
```sh
export LITELLM_API_KEY=dummy
bash benchmark/run.sh codex l1            # 한 셀(도구,레벨): codex|openhands|qclaude|qclaude35
bash benchmark/run.sh qclaude l3          # Claude Code → 122b
bash benchmark/run.sh qclaude35 l3        # Claude Code → 35b
bash benchmark/run-matrix.sh              # codex+openhands 전체 14셀(직렬)
python3 benchmark/report.py               # → RESULTS.md (codex vs openhands)
python3 benchmark/report-3way.py          # → RESULTS-3way-qwen.md (codex vs qclaude vs qclaude35)
python3 benchmark/report-qclaude-vs-codex.py  # → RESULTS-qclaude-vs-codex.md (2자)
```

> `qclaude`/`qclaude35`는 claude-code-proxy(:8082)를 통해 로컬 qwen에 붙는다. run.sh가 :8082
> 헬스를 선검사하고, `score.py`는 Claude의 `--output-format stream-json` 트랜스크립트에서
> `tool_use` 이벤트로 step을 센다. (3자 리포트는 codex 셀을 `.runs/results-14.json`에서 읽는다.)

> 과제 텍스트는 `tasks/<level>/PROMPT.md` 한 곳에만(TASK-03), judge `tasks/<level>/test.py`(stdlib
> 독립 judge)가 합격을 판정. 프롬프트·judge는 도구 런너와 독립적이다.

## 과제 7종 (분별력을 위해 서로 다른 능력을 자극)

각 과제는 `tasks/<level>/` 에 PROMPT.md(계약) + test.py(독립 judge) + ABOUT.md(결과물·사용법),
정답은 `reference/<level>/` 에 있다. 레벨이 올라갈수록, 또 도메인이 달라질수록 도구의 한계가 드러난다.

| Level | 만드는 것 | 복잡도 차원 | 자극하는 능력 |
|-------|-----------|-------------|----------------|
| L1 | `fib.py` 피보나치 함수 | single-file | 기본기 |
| L2 | `wordstat.py` 단어 통계 CLI | multi-file CLI | 파일 협력 + 출력 계약 |
| L3 | `kvstore/` + `cli.py` KV 서비스 | multi-module service | 패키지 + 상태 영속 |
| L4 | `calc.py` 산술식 평가 CLI | single-file / 알고리즘 | 파서·우선순위(`eval` 금지) |
| L5 | `todo.py` 할 일 관리 CLI | multi-file / 서브커맨드 | 서브커맨드 + JSON 영속 + 종료코드 |
| L6 | `csvstat.py` + `csvstat/` CSV 통계 CLI | multi-module / 데이터 | CSV 파싱 + 수치 집계 + 에러처리 |
| L7 | `serve.py` + `kvapi/` HTTP KV API | multi-module / 서버 | HTTP 서버 + 라우팅 + 영속 + **재시작 유지** |

> 각 과제의 **결과물(파일 리스트)** 과 **기능·사용법**은 `tasks/<level>/ABOUT.md` 에 정리돼 있다.
> 전체 매트릭스는 이제 **2 도구 × 7 레벨 = 14 셀**이다. L7은 L3보다 한 단계 위(서버 수명주기 + HTTP).

## 레이아웃

```
benchmark/
  START-HERE.md / INTERPRETING.md / REPRODUCE.md / RESULTS.md  # 길잡이·해석·재현·결과
  RESULTS-3way-qwen.md + RESULTS-3way-notes.md  # codex vs qclaude(122b) vs qclaude35(35b)
  RESULTS-qclaude-vs-codex.md     # codex vs qclaude(122b) 2자 비교
  README.md                       # 이 파일 (과제 정의 + 합격 기준 + 구조)
  run.sh                          # 한 셀(도구,레벨) 실행 — codex|openhands|qclaude|qclaude35, 격리·순차 락·비대화
  run-matrix.sh                   # codex+openhands 매트릭스(2도구×7레벨=14셀, 직렬) → results.json
  score.py                        # 4지표 채점/측정 (run.sh가 자동 호출; qclaude는 tool_use로 step 집계)
  report.py                       # results.json → RESULTS.md (codex vs openhands)
  report-3way.py                  # → RESULTS-3way-qwen.md (codex·qclaude·qclaude35)
  report-qclaude-vs-codex.py      # → RESULTS-qclaude-vs-codex.md
  tasks/
    l1-fib/      {PROMPT.md, test.py, ABOUT.md}   # 계약 + 독립 judge + 결과물·사용법
    l2-wordstat/ {PROMPT.md, test.py, ABOUT.md}
    l3-kvstore/  {PROMPT.md, test.py, ABOUT.md}
    l4-calc/     {PROMPT.md, test.py, ABOUT.md}
    l5-todo/     {PROMPT.md, test.py, ABOUT.md}
    l6-csvstat/  {PROMPT.md, test.py, ABOUT.md}
    l7-kvapi/    {PROMPT.md, test.py, ABOUT.md}
  reference/<level>/              # judge 검증용 레퍼런스 해답 (7레벨)
  .runs/                          # 실행 산출물(gitignore) — RESULTS.md가 영구 기록
```

각 레벨의 프롬프트는 위 `tasks/<level>/PROMPT.md` **단 한 곳에만** 존재한다(TASK-03).
도구별로 다른 문구를 쓰지 않는다.

## 합격 기준 (objective pass criterion, TASK-02)

레벨 X의 어떤 해답이 **합격**이라는 것은 다음 한 줄로 정의된다:

```
python3 benchmark/tasks/<level>/test.py <solution_dir>   # exit 0 → PASS
```

- judge가 **exit 0** 으로 끝나면 합격, **nonzero** 면 불합격이다.
- **도구의 자가 보고(self-report)는 신뢰하지 않는다.** "테스트 다 통과했다"는 도구의 말이 아니라,
  우리의 독립 judge 종료 코드만이 합격을 결정한다(forward ref: MET-01, Phase 3).

## 공통 규약 (judge가 의존하는 약속)

1. **judge 호출:** `python3 tasks/<level>/test.py <solution_dir>` 형태로 실행한다.
   `<solution_dir>` 가 생략되면 현재 디렉터리(`.`)를 기본값으로 쓴다.
2. **종료 코드 계약:** `0` = 모든 검사 통과, `nonzero` = 한 개 이상 검사 실패.
3. **stdlib-only:** 과제와 judge 모두 **파이썬 표준 라이브러리만** 사용한다(pip 설치 없음).
   이것이 재현성을 보장한다(PROJECT.md 제약).
4. **동일 프롬프트 규칙:** `PROMPT.md` 의 **정확한 텍스트를 모든 도구에 그대로(verbatim)** 먹인다.
   도구별 맞춤 문구는 없다(TASK-03).
5. **decoupling:** 프롬프트/테스트는 여기에 살고, 도구 런너(`run.sh`)와 독립적이다.
