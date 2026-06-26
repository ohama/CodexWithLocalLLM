# L6 — CSV column statistics CLI (multi-module, data processing)

## Task

Build a Python CLI **`csvstat.py`** (standard library only) that reads a CSV file and reports
statistics for a chosen numeric column, or lists the columns.

Structure it as a **multi-module project**: a package **`csvstat/`** (at minimum
`csvstat/__init__.py` and `csvstat/stats.py` for the numeric logic) plus the entry **`csvstat.py`**
at the project root. Write your own tests.

## Contract (black-box CLI — this is what is checked)

The CSV has a header row (column names) and comma-separated rows. Use the standard library
(`csv` module) for parsing.

- **Files required:**
  - `csvstat.py` at the solution root.
  - a `csvstat/` package directory containing `__init__.py` and `stats.py`.
- **List columns:** `python3 csvstat.py <file.csv> --cols`
  - Print each column name on its own line, **in header order**. **Exit 0**.
- **Column stats:** `python3 csvstat.py <file.csv> --col <name>`
  - For the named column (which must be numeric), print EXACTLY these five lines, in this order:
    ```
    count: <count>
    min: <min>
    max: <max>
    sum: <sum>
    mean: <mean>
    ```
  - `count` is the number of data rows (excluding the header).
  - Numbers are formatted with this rule:
    ```
    fmt(x) = str(int(x))   if x == int(x)     # integral → no decimal point
             str(x)        otherwise
    ```
    (so `sum` of `1,2,3,4` prints `10`, `mean` prints `2.5`).
  - **Exit 0** on success.
- **Errors → exit nonzero:**
  - file does not exist,
  - `--col <name>` where the column is missing, or is non-numeric (a value can't be parsed as a number),
  - missing/invalid arguments.

### Example

Given `data.csv`:
```
name,age,score
amy,30,1
bob,40,2
cid,50,3
dan,20,4
```

```
$ python3 csvstat.py data.csv --cols
name
age
score
$ python3 csvstat.py data.csv --col score
count: 4
min: 1
max: 4
sum: 10
mean: 2.5
$ python3 csvstat.py data.csv --col name      # non-numeric
$ echo $?
1
```

## Note

Standard library only. Do not assume any specific hidden test; just satisfy the contract above.
