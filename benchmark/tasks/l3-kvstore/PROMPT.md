# L3 — Key-value store service (multi-module)

## Task

Build a **multi-module key-value store service** in Python (standard library only).

Create a package **`kvstore/`** (at minimum `kvstore/__init__.py` and
`kvstore/storage.py` for persistence) plus a command-line entry **`cli.py`** at the
project root. Values must **persist on disk across separate process invocations**.
Write your own unit/integration tests.

## Contract (black-box CLI — this is what is checked)

Internal module names beyond the required ones are up to you, but the structure must
remain multi-module.

- **Files required:**
  - `cli.py` at the solution root.
  - a `kvstore/` package directory containing `__init__.py` and `storage.py`.
- **Persistence path:** the store reads/writes the file named by the environment
  variable **`KVSTORE_PATH`** if it is set; otherwise it uses **`./kvstore.db`** in the
  current directory. (This lets each run be hermetic.)
- **CLI commands** (run as `python3 cli.py <cmd> ...`):
  - `set <key> <value>` — store the pair; **exit 0**.
  - `get <key>` — print the stored value on its own line to stdout; **exit 0**.
    If the key does not exist: print **nothing** to stdout and **exit 1**.
  - `delete <key>` — remove the key if present; **exit 0** whether or not it existed
    (idempotent).
  - `list` — print all keys, one per line, **sorted ascending**; **exit 0**
    (no output if empty).
- **Persistence guarantee:** a value `set` in one process invocation is returned by
  `get` in a later, separate invocation (same `KVSTORE_PATH`).
- Keys and values are non-empty strings without newlines.

### Exit-code summary (the contract keys on these)

| command            | condition          | stdout            | exit |
|--------------------|--------------------|-------------------|------|
| `set k v`          | always             | (none required)   | 0    |
| `get k`            | key exists         | value + newline   | 0    |
| `get k`            | key missing        | (nothing)         | 1    |
| `delete k`         | key existed        | (none required)   | 0    |
| `delete k`         | key missing        | (none required)   | 0    |
| `list`             | any                | keys asc, 1/line  | 0    |

## Note

Standard library only. Do not assume any specific hidden test; just satisfy the CLI
contract above. Internal structure beyond the required files is up to you, but it must
remain multi-module.
