# L6 — csvstat (CSV 통계 CLI)

**복잡도 차원:** multi-module / 데이터 파싱 + 수치 집계 + 에러처리
**무엇을 분별하나:** CSV를 파싱해 **수치 컬럼을 집계**하고, 잘못된 입력(없는 파일·없는 컬럼·비수치
컬럼)에 **올바른 종료코드**로 반응하는가. 멀티모듈 패키지로 구조화하는가.

## 결과물 (파일 리스트)

정답이 만드는 파일:

| 파일 | 역할 |
|------|------|
| `csvstat.py` | CLI 진입점 — 인자 파싱(`--cols` / `--col <name>`), CSV 읽기, 출력 |
| `csvstat/__init__.py` | 패키지 초기화 (집계 함수 export) |
| `csvstat/stats.py` | 수치 집계 로직 (count/min/max/sum/mean, 숫자 포맷) |

> "멀티모듈" 요구: 진입점 `csvstat.py` + `csvstat/` 패키지(`__init__.py`, `stats.py`).

## 수행결과 (기능 및 사용법)

헤더가 있는 CSV에서 컬럼 목록을 보거나, 한 수치 컬럼의 통계를 낸다.

- `--cols` — 컬럼 이름을 헤더 순서대로 한 줄씩 출력.
- `--col <name>` — 그 수치 컬럼의 `count / min / max / sum / mean` 을 5줄로 출력.
  - 숫자 포맷: 정수값이면 소수점 없이(`10`, `35`), 아니면 `str(float)`(`2.5`).
- **에러(종료코드 nonzero):** 없는 파일 / 없는 컬럼 / 비수치 컬럼에 `--col` / 인자 누락.

### 사용 예

`data.csv`:
```
name,age,score
amy,30,1
bob,40,2
cid,50,3
dan,20,4
```
```sh
python3 csvstat.py data.csv --cols          # → name / age / score
python3 csvstat.py data.csv --col score     # → count:4 min:1 max:4 sum:10 mean:2.5
python3 csvstat.py data.csv --col age       # → ... sum:140 mean:35
python3 csvstat.py data.csv --col name      # → (비수치) 종료코드 nonzero
```

## 채점 방식

`tasks/l6-csvstat/test.py` 가 임시 CSV를 만들어 `--cols`·`--col`(수치/비수치/없는 컬럼)·없는 파일을
실행해 출력·종료코드를 검증한다. 기대값은 judge가 **독립 계산**한다.
`python3 benchmark/tasks/l6-csvstat/test.py <solution_dir>` → exit 0 = PASS.
