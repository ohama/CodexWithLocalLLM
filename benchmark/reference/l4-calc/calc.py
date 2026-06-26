#!/usr/bin/env python3
"""L4 reference — arithmetic expression evaluator (recursive descent, no eval)."""
import sys


def tokenize(s):
    toks, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
        elif c in "+-*/()":
            toks.append(c)
            i += 1
        elif c.isdigit() or c == ".":
            j = i
            while j < n and (s[j].isdigit() or s[j] == "."):
                j += 1
            num = s[i:j]
            if num.count(".") > 1:
                raise ValueError("bad number")
            toks.append(float(num) if "." in num else int(num))
            i = j
        else:
            raise ValueError(f"bad char: {c!r}")
    return toks


class P:
    def __init__(self, toks):
        self.t, self.i = toks, 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def eat(self):
        tok = self.t[self.i]
        self.i += 1
        return tok

    def expr(self):  # + -
        v = self.term()
        while self.peek() in ("+", "-"):
            op = self.eat()
            r = self.term()
            v = v + r if op == "+" else v - r
        return v

    def term(self):  # * /
        v = self.factor()
        while self.peek() in ("*", "/"):
            op = self.eat()
            r = self.factor()
            if op == "*":
                v = v * r
            else:
                if r == 0:
                    raise ZeroDivisionError()
                v = v / r
        return v

    def factor(self):  # unary minus, parens, number
        tok = self.peek()
        if tok == "-":
            self.eat()
            return -self.factor()
        if tok == "(":
            self.eat()
            v = self.expr()
            if self.peek() != ")":
                raise ValueError("expected )")
            self.eat()
            return v
        if isinstance(tok, (int, float)):
            return self.eat()
        raise ValueError("expected number")


def fmt(x):
    return str(int(x)) if x == int(x) else str(x)


def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    try:
        toks = tokenize(sys.argv[1])
        if not toks:
            sys.exit(1)
        p = P(toks)
        v = p.expr()
        if p.i != len(p.t):  # leftover tokens → malformed
            sys.exit(1)
        print(fmt(v))
    except (ValueError, ZeroDivisionError, IndexError):
        sys.exit(1)


if __name__ == "__main__":
    main()
