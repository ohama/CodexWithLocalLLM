# L4 — Arithmetic expression evaluator CLI (single-file, algorithmic)

## Task

Build a small Python CLI **`calc.py`** (standard library only) that evaluates a single
arithmetic expression given as `argv[1]` and prints the result.

This is a single-file but algorithmically non-trivial task: you must implement operator
**precedence** and **parentheses** correctly (do not just call `eval`).

## Contract (must hold exactly)

- **Entry file:** `calc.py` at the solution root, invoked as `python3 calc.py "<expression>"`
  (the whole expression is one quoted `argv[1]` string).
- **Grammar:**
  - Non-negative integer and decimal number literals (e.g. `3`, `42`, `2.5`).
  - Binary operators `+ - * /`, and **unary minus** (e.g. `-3`, `2 * -4`).
  - Parentheses `(` `)`.
  - Standard precedence: `*` and `/` bind tighter than `+` and `-`; **left-associative**.
  - Whitespace is ignored.
- **Division** is true (float) division (`/`).
- **Output format (CRITICAL):** print the result on a single line using this rule —
  ```
  fmt(x) = str(int(x))   if x == int(x)     # integral → no decimal point: 14, 20, 1
           str(x)        otherwise          # else Python str(float): 2.5
  ```
  Then **exit 0**.
- **Invalid input** — a malformed expression, division by zero, or empty expression — must
  **exit nonzero** (e.g. `1`). Stdout may be empty; any error text may go to stderr.

### Examples

| Command | Stdout | Exit |
|---|---|---|
| `python3 calc.py "2 + 3 * 4"` | `14` | 0 |
| `python3 calc.py "(2 + 3) * 4"` | `20` | 0 |
| `python3 calc.py "10 / 4"` | `2.5` | 0 |
| `python3 calc.py "-3 + 5"` | `2` | 0 |
| `python3 calc.py "7 - 2 - 1"` | `4` | 0 |
| `python3 calc.py "2 +"` | (empty) | nonzero |
| `python3 calc.py "1 / 0"` | (empty) | nonzero |

## Note

Standard library only. Do not assume any specific hidden test; just satisfy the contract above.
