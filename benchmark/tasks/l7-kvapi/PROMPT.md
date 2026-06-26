# L7 — HTTP key-value API service (multi-module, server + persistence + restart)

## Task

Build an **HTTP REST key-value service** in Python (standard library only). A long-running server
exposes CRUD over HTTP, and values **persist on disk across server restarts**.

Structure it as a **multi-module project**: a package **`kvapi/`** (at minimum `kvapi/__init__.py`
and `kvapi/storage.py` for persistence) plus a server entry **`serve.py`** at the project root.
Write your own tests.

## Contract (black-box HTTP — this is what is checked)

- **Files required:**
  - `serve.py` at the solution root.
  - a `kvapi/` package directory containing `__init__.py` and `storage.py`.
- **Start:** `python3 serve.py --port <PORT>` starts an HTTP server bound to `127.0.0.1:<PORT>` and
  keeps running until terminated (SIGTERM/SIGINT). It must begin accepting connections within a few seconds.
- **Persistence path:** the store reads/writes the file named by the environment variable
  **`KVAPI_PATH`** if set; otherwise **`./kvapi.db`** in the current directory. Data written by one
  server process must still be readable by a **later** server process with the same `KVAPI_PATH`
  (persistence across restarts).
- **Routes** (keys appear in the path after `/kv/`):
  - `PUT /kv/<key>` — the **request body is the value** (raw UTF-8 string). Store it. Respond **200**.
  - `GET /kv/<key>` — respond **200** with the **exact stored value** as the response body if the key
    exists; respond **404** if it does not.
  - `DELETE /kv/<key>` — respond **200** if the key existed (and remove it); **404** if it did not.
  - `GET /kv` — respond **200** with a **JSON array of all keys, sorted ascending** (e.g. `["a","b"]`).
- Standard library only (`http.server`, `json`, …). No external packages, no frameworks.

### Example (server on port 8080, then a second server reusing the same KVAPI_PATH)

```
$ KVAPI_PATH=./kvapi.db python3 serve.py --port 8080 &
$ curl -s -X PUT  --data 'world'  localhost:8080/kv/hello     # 200
$ curl -s         localhost:8080/kv/hello                     # 200 body: world
$ curl -s         localhost:8080/kv                           # 200 body: ["hello"]
$ curl -s -o/dev/null -w '%{http_code}'  localhost:8080/kv/nope   # 404
# kill the server, start a new one with the same KVAPI_PATH:
$ curl -s         localhost:8081/kv/hello                     # 200 body: world  (persisted)
$ curl -s -X DELETE localhost:8081/kv/hello                  # 200
$ curl -s -o/dev/null -w '%{http_code}' -X DELETE localhost:8081/kv/hello   # 404
```

## Note

Standard library only. Do not assume any specific hidden test; just satisfy the contract above.
