# L7 — kvapi (HTTP REST KV API 서비스)

**복잡도 차원:** multi-module / 장기 실행 서버 + HTTP + 영속 + 재시작
**무엇을 분별하나:** 패키지 구조 위에 **실제 HTTP 서버**를 세우고(라우팅·상태코드), 디스크에 영속해
**서버를 껐다 켜도 데이터가 유지**되는가. L3(멀티모듈+영속)보다 한 단계 위 — 서버 수명주기와
HTTP 계약까지 끝까지 완성해야 한다.

## 결과물 (파일 리스트)

정답이 만드는 파일:

| 파일 | 역할 |
|------|------|
| `serve.py` | 서버 진입점 — `--port` 파싱, HTTP 서버 기동, 라우팅(PUT/GET/DELETE) |
| `kvapi/__init__.py` | 패키지 초기화 |
| `kvapi/storage.py` | 디스크 영속 — 로드/저장(get/put/delete/keys), `KVAPI_PATH` |
| `kvapi.db` | 실행 중 생성되는 상태 파일 (경로는 `KVAPI_PATH`, 기본 `./kvapi.db`) |

> "멀티모듈" 요구: 진입점 `serve.py` + `kvapi/` 패키지(`__init__.py`, `storage.py`).

## 수행결과 (기능 및 사용법)

장기 실행 HTTP 서버가 키-값을 CRUD로 노출하고, 값은 디스크에 영속된다(서버 재시작 후에도 유지).

- 기동: `python3 serve.py --port <PORT>` → `127.0.0.1:<PORT>` 에서 수신.
- 라우트:
  - `PUT /kv/<key>` — **요청 본문이 값**. 저장 후 **200**.
  - `GET /kv/<key>` — 있으면 **200** + 저장된 값(본문), 없으면 **404**.
  - `DELETE /kv/<key>` — 있었으면 **200**(삭제), 없으면 **404**.
  - `GET /kv` — 전체 키의 **JSON 배열(정렬)**, **200**.
- 영속: `KVAPI_PATH`(기본 `./kvapi.db`). **다른 서버 프로세스가 같은 경로로 읽으면 데이터가 보존**돼야 함.

### 사용 예

```sh
KVAPI_PATH=./kvapi.db python3 serve.py --port 8080 &
curl -s -X PUT --data 'world' localhost:8080/kv/hello     # 200
curl -s               localhost:8080/kv/hello             # 200, body: world
curl -s               localhost:8080/kv                   # 200, body: ["hello"]
curl -s -o/dev/null -w '%{http_code}' localhost:8080/kv/nope   # 404
# 서버를 죽이고 같은 KVAPI_PATH로 새 서버를 띄우면:
curl -s               localhost:8081/kv/hello             # 200, body: world  (영속!)
curl -s -X DELETE     localhost:8081/kv/hello             # 200
```

## 채점 방식

`tasks/l7-kvapi/test.py` 가 빈 포트에 `serve.py` 를 **서브프로세스로 기동**→수신 대기 폴링→PUT/GET/
DELETE/list·상태코드 검증→서버를 죽이고 **새 서버를 같은 KVAPI_PATH로 재기동**해 **영속 유지**까지
확인한다(모두 stdlib HTTP). `python3 benchmark/tasks/l7-kvapi/test.py <solution_dir>` → exit 0 = PASS.
