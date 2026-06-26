# L1 — Fibonacci (single file)

## Task

Create a single file **`fib.py`** (Python standard library only) at the project root.
It must define a function **`fib(n)`** that returns the n-th Fibonacci number, where:

- `fib(0) == 0`
- `fib(1) == 1`
- `fib(n) == fib(n-1) + fib(n-2)` for `n >= 2`

Include a few `assert`-based self-tests in the file, and make `python3 fib.py` run
cleanly (exit 0, no traceback).

## Contract (must hold exactly)

- **File:** `fib.py` at the solution root.
- **Public API:** a function `fib(n: int) -> int`.
- **Required values:**
  - `fib(0) == 0`
  - `fib(1) == 1`
  - `fib(2) == 1`
  - `fib(3) == 2`
  - `fib(5) == 5`
  - `fib(10) == 55`
  - `fib(20) == 6765`
  - `fib(30) == 832040`
- `fib(n)` must return an `int`.
- No non-stdlib import is allowed.

## Note

Standard library only. Do not assume any specific hidden test; just satisfy the
contract above.
