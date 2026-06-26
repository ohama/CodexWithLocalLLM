#!/usr/bin/env python3
"""L4 judge — independent, stdlib-only, black-box via subprocess.

Runs `python3 calc.py "<expr>"` in the solution dir and checks stdout + exit code.
The judge computes the expected result itself (its own safe evaluator) and formats
with the contract's fmt() rule. It never trusts the solution's self-report.

Usage:  python3 test.py [solution_dir]   (default: current directory)
Exit 0 = PASS, nonzero = FAIL.
"""
import ast
import operator
import os
import subprocess
import sys

SOL = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
ENTRY = os.path.join(SOL, "calc.py")

_BIN = {ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv}


def expected(expr):
    """Compute the contract result independently via Python's AST (arithmetic only)."""
    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN:
            return _BIN[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -ev(node.operand)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("unsupported")
    tree = ast.parse(expr.strip(), mode="eval")
    return ev(tree)


def fmt(x):
    return str(int(x)) if x == int(x) else str(x)


def run(expr):
    p = subprocess.run([sys.executable, "calc.py", expr], cwd=SOL,
                       capture_output=True, text=True, timeout=30)
    return p.returncode, p.stdout.strip()


def fail(msg):
    print(f"FAIL l4-calc: {msg}")
    sys.exit(1)


def main():
    if not os.path.isfile(ENTRY):
        fail("missing calc.py at solution root")

    valid = ["2 + 3 * 4", "(2 + 3) * 4", "10 / 4", "-3 + 5", "7 - 2 - 1",
             "2 * (3 + 4) - 1", "3 + 4 * 2 / (1 - 5)", "2 * -4", "  6/3 + 1 "]
    for expr in valid:
        want = fmt(expected(expr))
        rc, out = run(expr)
        if rc != 0:
            fail(f"valid expr {expr!r} exited {rc} (want 0)")
        if out != want:
            fail(f"expr {expr!r}: got {out!r}, want {want!r}")

    invalid = ["2 +", "(1 + 2", "1 / 0", "", "* 3", "2 3"]
    for expr in invalid:
        rc, _ = run(expr)
        if rc == 0:
            fail(f"invalid expr {expr!r} exited 0 (want nonzero)")

    print("PASS l4-calc")
    sys.exit(0)


if __name__ == "__main__":
    main()
