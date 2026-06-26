# L5 — Todo manager CLI (multi-file, subcommands + persistence)

## Task

Build a Python **todo manager CLI** (standard library only) with subcommands that **persist tasks
across separate process invocations** (each command runs as its own process).

Split the logic into **at least two files** (for example, `todo.py` as the CLI entry point plus a
storage helper module). Write your own tests.

## Contract (black-box CLI — this is what is checked)

- **Entry file:** `todo.py` at the solution root, invoked as `python3 todo.py <cmd> ...`.
- **Persistence path:** read/write the file named by the environment variable **`TODO_PATH`** if set;
  otherwise use **`./todos.json`** in the current directory. (Lets each run be hermetic.)
- **Task ids** are positive integers assigned sequentially starting at **1**, and are **stable**
  (removing a task does NOT renumber the others; the next add keeps increasing).
- **Subcommands:**
  - `add <text>` — append a new open task with the given text. Print exactly `added <id>` (the new id)
    on its own line. **Exit 0**.
  - `list` — print every task, in ascending id order, one per line, in the exact form:
    ```
    <id> <status> <text>
    ```
    where `<status>` is `[ ]` for an open task or `[x]` for a done task, with **single spaces** between
    the three parts. An empty list prints nothing. **Exit 0**.
  - `done <id>` — mark that task done. **Exit 0** if the id exists; **exit nonzero** if it does not.
  - `rm <id>` — remove that task. **Exit 0** if the id exists; **exit nonzero** if it does not.
- Unknown subcommand or missing argument → **exit nonzero**.

### Example session (each line is a separate process; same `TODO_PATH`)

```
$ python3 todo.py add "buy milk"
added 1
$ python3 todo.py add "write report"
added 2
$ python3 todo.py done 1
$ python3 todo.py list
1 [x] buy milk
2 [ ] write report
$ python3 todo.py rm 1
$ python3 todo.py list
2 [ ] write report
$ python3 todo.py done 99      # nonexistent
$ echo $?
1
```

## Note

Standard library only. Do not assume any specific hidden test; just satisfy the contract above.
