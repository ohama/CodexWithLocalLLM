"""L1 reference solution — fib.py (Python standard library only).

Iterative Fibonacci satisfying the L1 contract:
    fib(0)=0, fib(1)=1, fib(n)=fib(n-1)+fib(n-2) for n>=2.
Returns an int. `python3 fib.py` runs the self-tests and exits 0.
"""


def fib(n: int) -> int:
    """Return the n-th Fibonacci number (iterative, O(n))."""
    if n == 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


# Self-tests (contract values).
assert fib(0) == 0
assert fib(1) == 1
assert fib(2) == 1
assert fib(3) == 2
assert fib(5) == 5
assert fib(10) == 55
assert fib(20) == 6765
assert fib(30) == 832040

if __name__ == "__main__":
    print("All tests passed!")
