# L5 — todo (할 일 관리 CLI)

**복잡도 차원:** multi-file / 서브커맨드 + JSON 영속 + 종료코드 계약
**무엇을 분별하나:** 여러 서브커맨드를 가진 CLI를 만들고, **프로세스를 넘나드는 상태 영속**과
**안정적인 id**(삭제해도 재번호 안 함), 성공/실패 **종료코드**를 정확히 다루는가.

## 결과물 (파일 리스트)

정답이 만드는 파일(예시 — 진입점만 고정, 보조 모듈명은 자유):

| 파일 | 역할 |
|------|------|
| `todo.py` | CLI 진입점 — 서브커맨드 디스패치(add/list/done/rm) |
| `store.py` (또는 유사 모듈) | JSON 파일 영속 — 로드/저장, id 발급, 항목 조회 |
| `todos.json` | 실행 중 생성되는 상태 파일 (경로는 `TODO_PATH` 환경변수, 기본 `./todos.json`) |

> "멀티파일" 요구: 진입점 `todo.py` 외에 최소 한 개의 보조 모듈(또는 패키지)로 분리.

## 수행결과 (기능 및 사용법)

할 일을 추가/조회/완료/삭제하며, 상태는 JSON 파일에 영속된다(각 명령은 별도 프로세스).

- `add <text>` — 새 할 일 추가, `added <id>` 출력. id는 1부터 순차·**안정적**(삭제해도 재사용 안 함).
- `list` — `<id> <status> <text>` 형식으로 id 오름차순 출력. status는 `[ ]`(미완) / `[x]`(완료).
- `done <id>` — 완료 표시. 없는 id면 종료코드 nonzero.
- `rm <id>` — 삭제. 없는 id면 종료코드 nonzero.
- 알 수 없는 명령·인자 누락 → nonzero.

### 사용 예 (같은 `TODO_PATH`, 각 줄은 별도 프로세스)

```sh
export TODO_PATH=./todos.json
python3 todo.py add "buy milk"      # → added 1
python3 todo.py add "write report"  # → added 2
python3 todo.py done 1
python3 todo.py list                # → "1 [x] buy milk"  /  "2 [ ] write report"
python3 todo.py rm 1
python3 todo.py list                # → "2 [ ] write report"
python3 todo.py done 99; echo $?    # → 1 (없는 id)
```

## 채점 방식

`tasks/l5-todo/test.py` 가 임시 `TODO_PATH` 로 add/list/done/rm 시퀀스를 **별도 프로세스**로 돌려
출력·종료코드·**id 안정성**·영속을 검증한다. `python3 benchmark/tasks/l5-todo/test.py <solution_dir>`
→ exit 0 = PASS.
