"""L2 reference helper — tokenization + counting (stdlib only).

A *word* is a maximal run of ASCII alphanumerics [A-Za-z0-9], lowercased;
every other character is a separator. Ordering for `top` is count descending,
then word ascending for ties.
"""

import re

_TOKEN = re.compile(r"[A-Za-z0-9]+")


def tokenize(text):
    """Return the list of lowercased word tokens in `text`."""
    return [m.group(0).lower() for m in _TOKEN.finditer(text)]


def analyze(text, top_n=5):
    """Return (total, unique, top) for `text`.

    total = number of tokens, unique = distinct tokens,
    top = up to `top_n` (word, count) pairs, count desc then word asc.
    """
    tokens = tokenize(text)
    total = len(tokens)
    counts = {}
    for tok in tokens:
        counts[tok] = counts.get(tok, 0) + 1
    unique = len(counts)
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return total, unique, ordered[:top_n]
