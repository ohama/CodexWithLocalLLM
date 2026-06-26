# L2 — Word statistics CLI (multi-file)

## Task

Build a small Python CLI **`wordstat.py`** (standard library only) that reads a UTF-8
text file whose path is given as `argv[1]` and reports word statistics.

Split the logic into **at least two files** (for example, `wordstat.py` as the CLI entry
point plus a helper module that does tokenization/counting) to keep it a genuine
multi-file project. Also create a sample input text file and your own tests.

## Contract (must hold exactly)

- **Entry file:** `wordstat.py` at the solution root, invoked as
  `python3 wordstat.py <textfile>`.
- **Tokenization:** a *word* is a maximal run of ASCII alphanumerics `[A-Za-z0-9]`,
  compared **case-insensitively** (lowercased). Every other character is a separator.
  - Example: `"The cat's"` tokenizes to `the`, `cat`, `s`.
- **Stdout format** — EXACTLY these lines, in this order, with lowercase labels:

  ```
  total: <int>
  unique: <int>
  top:
  <word> <count>
  ...
  ```

  - `total:` is the total number of word tokens.
  - `unique:` is the number of distinct words.
  - Under `top:`, list up to **5** entries, most frequent first.
    - Ordering: **count descending, then word ascending** for ties.
    - Emit at most 5 entries (fewer if there are fewer distinct words).
    - Exactly **one space** between the word and its count.
- **Exit 0** on success.

## Note

Standard library only. Do not assume any specific hidden test; just satisfy the
contract above.
