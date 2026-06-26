---
phase: 01-fixed-tasks
plan: 02
type: execute
wave: 2
depends_on: ["01"]
files_modified:
  - benchmark/tasks/l1-fib/test.py
  - benchmark/tasks/l2-wordstat/test.py
  - benchmark/tasks/l3-kvstore/test.py
  - benchmark/reference/l1-fib/fib.py
  - benchmark/reference/l2-wordstat/wordstat.py
  - benchmark/reference/l2-wordstat/wordcount.py
  - benchmark/reference/l3-kvstore/cli.py
  - benchmark/reference/l3-kvstore/kvstore/__init__.py
  - benchmark/reference/l3-kvstore/kvstore/storage.py
autonomous: true

must_haves:
  truths:
    - "Each level has an independent judge test.py using only the Python standard library."
    - "Running `python3 tasks/<level>/test.py reference/<level>` exits 0 for all three levels (judge passes a correct solution)."
    - "Each judge exits nonzero when pointed at a deliberately broken solution (the judge actually discriminates pass from fail)."
    - "Each judge loads the solution from argv[1] (defaulting to cwd) and checks the exact contract from the matching PROMPT.md."
  artifacts:
    - path: "benchmark/tasks/l1-fib/test.py"
      provides: "Independent judge for L1: imports fib from solution dir, asserts required values, exit 0/nonzero"
      contains: "argv"
    - path: "benchmark/tasks/l2-wordstat/test.py"
      provides: "Independent judge for L2: runs wordstat.py as subprocess on crafted input, parses exact stdout"
      contains: "subprocess"
    - path: "benchmark/tasks/l3-kvstore/test.py"
      provides: "Independent judge for L3: runs cli.py set/get/delete/list via subprocess, checks persistence + exit codes"
      contains: "subprocess"
    - path: "benchmark/reference/l1-fib/fib.py"
      provides: "Reference L1 solution to validate the judge"
      contains: "def fib"
    - path: "benchmark/reference/l2-wordstat/wordstat.py"
      provides: "Reference L2 multi-file CLI solution to validate the judge"
      contains: "argv"
    - path: "benchmark/reference/l3-kvstore/cli.py"
      provides: "Reference L3 CLI entry to validate the judge"
      contains: "KVSTORE_PATH"
  key_links:
    - from: "benchmark/tasks/l1-fib/test.py"
      to: "benchmark/tasks/l1-fib/PROMPT.md"
      via: "judge asserts exactly the fib values pinned in the L1 contract"
      pattern: "fib\\("
    - from: "benchmark/tasks/l2-wordstat/test.py"
      to: "benchmark/tasks/l2-wordstat/PROMPT.md"
      via: "judge parses the exact total:/unique:/top: stdout format from the L2 contract"
      pattern: "total|unique|top"
    - from: "benchmark/tasks/l3-kvstore/test.py"
      to: "benchmark/tasks/l3-kvstore/PROMPT.md"
      via: "judge drives the set/get/delete/list CLI and checks the exit codes from the L3 contract"
      pattern: "set|get|delete|list"
---

<objective>
Write the three independent, stdlib-only judge tests (one per level) plus a reference solution per level, then validate that each judge exits 0 on its reference and nonzero on a broken solution.

Purpose: The judge is the objective, tool-agnostic pass criterion (TASK-02). It must judge any tool's output in Phase 2 without modification, so it reads the solution from a directory argument and checks only the black-box contract frozen in Plan 01. Reference solutions exist to prove each judge is correct (Success Criterion 4: test passes against a reference solution).

Output: 3 test.py judges + reference solutions for L1/L2/L3, validated.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/phases/01-fixed-tasks/01-PLAN.md

# Frozen contracts from Plan 01 (the judges must mirror these exactly):
@benchmark/README.md
@benchmark/tasks/l1-fib/PROMPT.md
@benchmark/tasks/l2-wordstat/PROMPT.md
@benchmark/tasks/l3-kvstore/PROMPT.md

# Existing validated reference material to adapt (do NOT rebuild from scratch):
@examples/codex-tests/.runs/03-single-file-20260624-110248/fib.py
@examples/codex-tests/.runs/04-multi-step-20260624-110302/wordstat.py
@documentation/codex-hermes-openhands-comparison.md
</context>

<design_notes>
Judge conventions (from README, established in Plan 01):
- Invocation: `python3 tasks/<level>/test.py <solution_dir>`, where <solution_dir> defaults to '.' (cwd) when omitted.
- Exit 0 = all checks pass; exit nonzero = any check failed. Print a short PASS/FAIL summary to stdout/stderr.
- stdlib only.

How each judge locates the solution:
- L1: insert <solution_dir> at sys.path[0], then `import fib` and call fib(). Use importlib so a stale 'fib' module isn't cached.
- L2 / L3: run the solution as a SUBPROCESS (`python3 <solution_dir>/wordstat.py ...`, `python3 <solution_dir>/cli.py ...`) with cwd set appropriately and a temp working area. Black-box subprocess keeps the judge independent of internal module names (the prompts only fix the entry-file names).

Hermeticity:
- L2: write the crafted input to a tempfile.TemporaryDirectory; pass its path as argv[1].
- L3: set env KVSTORE_PATH to a path inside a TemporaryDirectory so the store is fresh; run cli.py with cwd = that temp dir (or pass absolute KVSTORE_PATH) so nothing leaks between checks and persistence-across-process is genuinely tested by separate subprocess calls.

Reference solutions live under benchmark/reference/<level>/ and are ONLY used to validate the judges here. Phase 2 runs tools in their own isolated dirs and points the judge at those instead.
</design_notes>

<tasks>

<task type="auto">
  <name>Task 1: L1 judge + reference, validated both ways</name>
  <files>benchmark/tasks/l1-fib/test.py, benchmark/reference/l1-fib/fib.py</files>
  <action>
Write benchmark/reference/l1-fib/fib.py: a correct stdlib-only fib(n) (iterative) matching the L1 contract, with the required values, runnable via `python3 fib.py` with a couple of asserts. (Adapt the validated examples/codex-tests/.runs/03-single-file-20260624-110248/fib.py.)

Write benchmark/tasks/l1-fib/test.py (the judge):
  - Read solution_dir = sys.argv[1] if given else '.'.
  - Insert os.path.abspath(solution_dir) at sys.path[0]; import the module `fib` (use importlib.import_module / invalidate caches so re-runs are clean).
  - Assert the contract values: fib(0)=0, fib(1)=1, fib(2)=1, fib(3)=2, fib(5)=5, fib(10)=55, fib(20)=6765, fib(30)=832040; assert each result is an int.
  - Collect failures; on any failure print "FAIL: ..." and sys.exit(1). On all pass print "PASS l1-fib" and sys.exit(0).

Validate (run in <verify>): judge exits 0 on the reference; judge exits nonzero on a broken solution.
  </action>
  <verify>
`python3 benchmark/tasks/l1-fib/test.py benchmark/reference/l1-fib` exits 0.
Negative check (must exit nonzero): create a temp dir with a broken fib (e.g. fib that returns n), point the judge at it, confirm nonzero:
`d=$(mktemp -d); printf 'def fib(n):\n    return n\n' > "$d/fib.py"; python3 benchmark/tasks/l1-fib/test.py "$d"; test $? -ne 0` exits 0.
  </verify>
  <done>L1 judge imports fib from the given dir, enforces all contract values, exits 0 on the reference and nonzero on a broken solution; reference fib.py runs cleanly.</done>
</task>

<task type="auto">
  <name>Task 2: L2 judge + multi-file reference, validated both ways</name>
  <files>benchmark/tasks/l2-wordstat/test.py, benchmark/reference/l2-wordstat/wordstat.py, benchmark/reference/l2-wordstat/wordcount.py</files>
  <action>
Write the reference (multi-file, stdlib-only) matching the L2 contract:
  - benchmark/reference/l2-wordstat/wordcount.py: helper with the tokenizer (maximal [A-Za-z0-9] runs, lowercased) and a function returning (total, unique, top_n) with ordering count-desc then word-asc.
  - benchmark/reference/l2-wordstat/wordstat.py: CLI entry; reads argv[1], uses wordcount helper, prints the EXACT contract format:
        total: <int>
        unique: <int>
        top:
        <word> <count>   (up to 5, count desc then word asc)
  (Adapt examples/codex-tests/.runs/04-multi-step-20260624-110302/wordstat.py but split into two files and conform stdout to the contract.)

Write benchmark/tasks/l2-wordstat/test.py (the judge):
  - solution_dir = sys.argv[1] if given else '.'.
  - In a tempfile.TemporaryDirectory, write a crafted input file with KNOWN, tie-free top counts, e.g. content producing: apple x5, banana x4, cherry x3, date x2, egg x1, plus a couple more distinct words so total/unique are non-trivial and the top-5 boundary is exercised. Compute expected total, unique, and the exact top-5 lines yourself.
  - Run `python3 <solution_dir>/wordstat.py <inputfile>` via subprocess.run(capture_output=True, text=True), assert returncode 0.
  - Parse stdout: regex/line-parse "total: N", "unique: M", then the lines after "top:". Assert total, unique, and that the top entries equal the expected ordered list (word and count).
  - Also test the ordering/tie-break with a small second input where two words share a count (assert alphabetical order among the tie).
  - On any mismatch print "FAIL: ..." + actual stdout and sys.exit(1); else "PASS l2-wordstat" + sys.exit(0).

Validate both ways in <verify>.
  </action>
  <verify>
`python3 benchmark/tasks/l2-wordstat/test.py benchmark/reference/l2-wordstat` exits 0.
Negative check: `d=$(mktemp -d); printf 'print("total: 0")\n' > "$d/wordstat.py"; python3 benchmark/tasks/l2-wordstat/test.py "$d"; test $? -ne 0` exits 0.
  </verify>
  <done>L2 judge runs wordstat.py as a subprocess on crafted input, parses the exact stdout format, validates total/unique/top-5 and tie ordering, exits 0 on the multi-file reference and nonzero on a broken solution.</done>
</task>

<task type="auto">
  <name>Task 3: L3 judge + multi-module reference, validated both ways</name>
  <files>benchmark/tasks/l3-kvstore/test.py, benchmark/reference/l3-kvstore/cli.py, benchmark/reference/l3-kvstore/kvstore/__init__.py, benchmark/reference/l3-kvstore/kvstore/storage.py</files>
  <action>
Write the multi-module reference (stdlib-only) matching the L3 contract:
  - benchmark/reference/l3-kvstore/kvstore/storage.py: a Store class persisting to a JSON file at KVSTORE_PATH (env) or ./kvstore.db; methods set/get/delete/keys with safe load/save.
  - benchmark/reference/l3-kvstore/kvstore/__init__.py: expose Store (and a helper to resolve the path).
  - benchmark/reference/l3-kvstore/cli.py: argparse/argv dispatch implementing the CLI contract exactly:
        set <key> <value> -> exit 0
        get <key>         -> print value + exit 0; missing -> no stdout, exit 1
        delete <key>      -> exit 0 (idempotent)
        list              -> keys sorted asc, one per line, exit 0
  (Base the design on the KV-store task in documentation/codex-hermes-openhands-comparison.md; keep it minimal.)

Write benchmark/tasks/l3-kvstore/test.py (the judge), black-box via subprocess:
  - solution_dir = sys.argv[1] if given else '.'.
  - Use tempfile.TemporaryDirectory for KVSTORE_PATH (e.g. <tmp>/store.db). Helper run(*args): subprocess.run(["python3", os.path.join(abs_solution_dir,"cli.py"), *args], env={**os.environ, "KVSTORE_PATH": store_path}, cwd=<tmp>, capture_output=True, text=True).
  - Checks: (1) verify required files exist: cli.py, kvstore/__init__.py, kvstore/storage.py (multi-module requirement). (2) set a few keys -> exit 0. (3) get existing key in a SEPARATE process -> exit 0 and stdout == value (persistence across processes). (4) get missing key -> exit code 1 and empty stdout. (5) delete existing key -> exit 0, then get -> exit 1. (6) delete missing key -> exit 0 (idempotent). (7) list -> keys sorted ascending, one per line.
  - On any failure print "FAIL: ..." + captured output and sys.exit(1); else "PASS l3-kvstore" + sys.exit(0).

Validate both ways in <verify>.
  </action>
  <verify>
`python3 benchmark/tasks/l3-kvstore/test.py benchmark/reference/l3-kvstore` exits 0.
Negative check: `d=$(mktemp -d); mkdir -p "$d/kvstore"; : > "$d/kvstore/__init__.py"; : > "$d/kvstore/storage.py"; printf 'import sys\nsys.exit(0)\n' > "$d/cli.py"; python3 benchmark/tasks/l3-kvstore/test.py "$d"; test $? -ne 0` exits 0.
  </verify>
  <done>L3 judge drives cli.py set/get/delete/list via subprocess with a temp KVSTORE_PATH, verifies multi-module files, persistence across separate processes, and the exact exit codes (get-miss=1, delete idempotent=0); exits 0 on the reference and nonzero on a broken solution.</done>
</task>

</tasks>

<verification>
Run all three judges against their references — all exit 0:
- `python3 benchmark/tasks/l1-fib/test.py benchmark/reference/l1-fib`
- `python3 benchmark/tasks/l2-wordstat/test.py benchmark/reference/l2-wordstat`
- `python3 benchmark/tasks/l3-kvstore/test.py benchmark/reference/l3-kvstore`
Each negative check (broken solution) exits nonzero.
Confirm no judge or reference imports a non-stdlib module: `! grep -RnE "^\s*(import|from)\s+(?!os|sys|re|json|argparse|tempfile|subprocess|pathlib|collections|importlib|unittest|string|io|typing)" benchmark/tasks benchmark/reference` (manual scan acceptable — the rule is stdlib-only).
</verification>

<success_criteria>
- 3 independent judges exist at tasks/<level>/test.py, stdlib-only, with the exit-code contract (TASK-02).
- Each judge passes (exit 0) against its reference solution (Phase 1 Success Criterion 4).
- Each judge fails (nonzero) against a broken solution — proving it discriminates.
- Judges read the solution dir from argv (default cwd), so the Phase 2 runner can point them at any tool's output unchanged.
- Each judge enforces the exact contract frozen in the matching PROMPT.md.
</success_criteria>

<output>
After completion, create `.planning/phases/01-fixed-tasks/01-02-SUMMARY.md` per the summary template: list the judges + references created, the exact judge invocation per level, and confirmation that all three judges exit 0 on references and nonzero on broken solutions.
</output>
