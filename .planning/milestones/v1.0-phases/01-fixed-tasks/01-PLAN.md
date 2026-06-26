---
phase: 01-fixed-tasks
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - benchmark/README.md
  - benchmark/tasks/l1-fib/PROMPT.md
  - benchmark/tasks/l2-wordstat/PROMPT.md
  - benchmark/tasks/l3-kvstore/PROMPT.md
autonomous: true

must_haves:
  truths:
    - "Each of the three levels (L1 fib, L2 wordstat, L3 kvstore) has a single canonical PROMPT.md containing the exact task text fed identically to every tool."
    - "Each PROMPT.md specifies a precise, tool-agnostic contract (file names, signatures/CLI commands, exact stdout format, exit codes) that a black-box test can verify."
    - "Every task is Python-stdlib-only and the prompts contain no external dependency."
    - "One benchmark/README.md states the objective pass criterion (independent test exits 0) and the shared conventions all three tasks follow."
  artifacts:
    - path: "benchmark/README.md"
      provides: "Pass criterion + shared conventions (solution-dir argument, exit-code contract, identical-prompt rule, stdlib-only rule)"
      min_lines: 30
    - path: "benchmark/tasks/l1-fib/PROMPT.md"
      provides: "L1 single-file fib task text + contract (fib.py, fib(n) signature)"
      contains: "fib"
    - path: "benchmark/tasks/l2-wordstat/PROMPT.md"
      provides: "L2 multi-file CLI wordstat task text + exact stdout contract"
      contains: "wordstat.py"
    - path: "benchmark/tasks/l3-kvstore/PROMPT.md"
      provides: "L3 multi-module KV service task text + CLI/persistence contract"
      contains: "cli.py"
  key_links:
    - from: "benchmark/README.md"
      to: "benchmark/tasks/l{1,2,3}-*/PROMPT.md"
      via: "README enumerates the three task dirs as the single canonical prompt location"
      pattern: "tasks/l1-fib|tasks/l2-wordstat|tasks/l3-kvstore"
---

<objective>
Define and freeze the three fixed-complexity benchmark tasks (L1 single-file fib, L2 multi-file CLI wordstat, L3 multi-module KV service) as canonical, tool-agnostic prompt files, and document the objective pass criterion plus shared conventions in one README.

Purpose: These prompts are the single source of truth fed identically to both Codex and OpenHands in Phase 2. Their contracts (file names, signatures, exact stdout, exit codes) are what makes a single independent test (Plan 02) able to judge any tool's output without modification.

Output: benchmark/README.md and three PROMPT.md files — the frozen task definitions. No tests, no reference solutions, no tool execution in this plan.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md

# Existing validated task material to reuse (do NOT rebuild from scratch):
@examples/codex-tests/levels/03-single-file.sh
@examples/codex-tests/levels/04-multi-step.sh
@examples/codex-tests/levels/06-multi-file.sh
@documentation/codex-hermes-openhands-comparison.md
</context>

<design_notes>
Critical separation of concerns:
- The PROMPT.md text is what the AGENT sees. It must read as a natural coding task AND embed the exact interface contract (so the produced code is shaped the way the hidden judge expects).
- The independent test (Plan 02) is the HIDDEN JUDGE. Prompts must NOT mention or reference the judge test, and must NOT tell the agent to satisfy "the test in test.py". Prompts MAY tell the agent to write and pass their own tests (realistic), but trust is decided by our independent test later (forward ref MET-01).
- Because the judge is black-box, every prompt must pin down: exact file/dir names, function signatures or CLI command syntax, exact stdout format, and exit-code behavior. Vague prompts make a single tool-agnostic test impossible.

Canonical layout this plan establishes:
  benchmark/
    README.md
    tasks/
      l1-fib/PROMPT.md
      l2-wordstat/PROMPT.md
      l3-kvstore/PROMPT.md
Plan 02 will add tasks/<level>/test.py (the judge) and reference/<level>/ (solutions to validate the judge).

Shared conventions to state in README (Plan 02 tests will rely on these):
- The judge is run as `python3 tasks/<level>/test.py <solution_dir>` where <solution_dir> defaults to the current directory if omitted.
- Pass = judge exits 0; fail = judge exits nonzero. Tool self-report is never trusted.
- All tasks and tests use only the Python standard library.
- The same PROMPT.md text is fed verbatim to every tool — no per-tool wording.
</design_notes>

<tasks>

<task type="auto">
  <name>Task 1: Create benchmark/ structure and README with pass criterion + conventions</name>
  <files>benchmark/README.md</files>
  <action>
Create the benchmark/ directory tree: benchmark/tasks/l1-fib/, benchmark/tasks/l2-wordstat/, benchmark/tasks/l3-kvstore/ (Task 2/3 fill the PROMPT.md files; an empty dir is fine here, just ensure the README and the three task dirs exist).

Write benchmark/README.md covering:
1. What this is: the canonical, tool-agnostic task definitions for the Codex-vs-OpenHands benchmark (3 fixed complexity levels). Note these are reused/validated tasks: fib (single file), wordstat (multi-file CLI), KV store (multi-module service).
2. Layout: list tasks/l1-fib, tasks/l2-wordstat, tasks/l3-kvstore as the SINGLE canonical place each prompt lives (TASK-03). State that tasks/<level>/test.py (judge) and reference/<level>/ (validation solutions) are added in Plan 02.
3. Objective pass criterion (TASK-02): a solution PASSES level X iff `python3 benchmark/tasks/<level>/test.py <solution_dir>` exits 0. Nonzero = fail. Tool self-report is NOT trusted (forward ref: MET-01, Phase 3).
4. Conventions (so Plan 02 tests are consistent):
   - Judge invocation: `python3 tasks/<level>/test.py <solution_dir>`, <solution_dir> defaults to cwd ('.') when omitted.
   - Exit-code contract: 0 = all checks pass, nonzero = at least one check failed.
   - stdlib-only: tasks and judges use only the Python standard library (no pip installs) — guarantees reproducibility (Constraint in PROJECT.md).
   - Identical-prompt rule: the exact PROMPT.md text is fed verbatim to every tool; no tool-specific wording (TASK-03).
   - Decoupling: prompts/tests live here, independent of any tool runner (the runner arrives in Phase 2).
5. A one-line-per-level summary table: level | what it builds | canonical prompt | complexity dimension (single-file / multi-file CLI / multi-module service).

Keep it concise (English or Korean consistent with existing docs is fine; existing project docs mix both — match PROJECT.md tone). Do NOT include the full prompt text here; that lives in the PROMPT.md files.
  </action>
  <verify>
`test -f benchmark/README.md && test -d benchmark/tasks/l1-fib && test -d benchmark/tasks/l2-wordstat && test -d benchmark/tasks/l3-kvstore` exits 0.
`grep -q "test.py" benchmark/README.md && grep -q "exit" benchmark/README.md` exits 0 (pass criterion documented).
  </verify>
  <done>benchmark/README.md exists, names the three canonical task dirs, and states the exit-0 pass criterion plus the four conventions (judge invocation, exit-code contract, stdlib-only, identical-prompt).</done>
</task>

<task type="auto">
  <name>Task 2: Write L1 (fib) and L2 (wordstat) PROMPT.md with precise contracts</name>
  <files>benchmark/tasks/l1-fib/PROMPT.md, benchmark/tasks/l2-wordstat/PROMPT.md</files>
  <action>
Write two prompt files. Each must read as a natural coding task to an agent AND pin the exact contract the hidden judge will check. Do NOT mention any judge/test.py.

benchmark/tasks/l1-fib/PROMPT.md — L1 single-file:
  Task text: "Create a single file `fib.py` (Python standard library only) defining a function `fib(n)` that returns the n-th Fibonacci number, with fib(0)=0, fib(1)=1, and fib(n)=fib(n-1)+fib(n-2) for n>=2. Include a few assert-based self-tests and make `python3 fib.py` run cleanly."
  Contract section (explicit, so judge can import it):
    - File: `fib.py` at the solution root.
    - Public API: function `fib(n: int) -> int`.
    - Required values: fib(0)=0, fib(1)=1, fib(2)=1, fib(3)=2, fib(5)=5, fib(10)=55, fib(20)=6765, fib(30)=832040.
    - Must return an int, must not require any non-stdlib import.

benchmark/tasks/l2-wordstat/PROMPT.md — L2 multi-file CLI:
  Task text: "Build a small Python CLI `wordstat.py` (standard library only) that reads a UTF-8 text file path given as argv[1] and reports word statistics. Split logic into at least two files (e.g. wordstat.py CLI entry + a helper module) to keep it a multi-file project. Also create a sample input file and your own tests."
  Contract section (exact stdout, so a black-box judge can parse it):
    - Entry file: `wordstat.py` at the solution root, invoked as `python3 wordstat.py <textfile>`.
    - Tokenization: a "word" is a maximal run of ASCII alphanumerics [A-Za-z0-9], compared case-insensitively (lowercased). All other characters are separators. (So "The cat's" -> the, cat, s.)
    - Stdout format, EXACTLY these lines in this order, lowercase labels:
        total: <int>            # total number of word tokens
        unique: <int>           # number of distinct words
        top:
        <word> <count>          # up to 5 lines, most frequent first
        ...                     # order: count descending, then word ascending for ties
      Emit at most 5 entries under `top:` (fewer if there are fewer distinct words). One space between word and count.
    - Exit 0 on success.
  Add a note in BOTH files: "Standard library only. Do not assume any specific hidden test; just satisfy the contract above."

Keep each PROMPT.md self-contained.
  </action>
  <verify>
`test -f benchmark/tasks/l1-fib/PROMPT.md && test -f benchmark/tasks/l2-wordstat/PROMPT.md` exits 0.
`grep -q "fib(10)" benchmark/tasks/l1-fib/PROMPT.md` and `grep -qi "total:" benchmark/tasks/l2-wordstat/PROMPT.md && grep -qi "top:" benchmark/tasks/l2-wordstat/PROMPT.md` all exit 0.
  </verify>
  <done>L1 prompt pins the fib.py / fib(n) signature with concrete required values; L2 prompt pins wordstat.py invocation, tokenization rule, exact stdout format, and tie-break order. Neither references a hidden test. Both state stdlib-only.</done>
</task>

<task type="auto">
  <name>Task 3: Write L3 (KV store) PROMPT.md with multi-module + CLI/persistence contract</name>
  <files>benchmark/tasks/l3-kvstore/PROMPT.md</files>
  <action>
Write benchmark/tasks/l3-kvstore/PROMPT.md — L3 multi-module service. Base it on the validated KV-store task from documentation/codex-hermes-openhands-comparison.md, but make the externally-observable contract precise so a single black-box judge works across tools.

  Task text: "Build a multi-module key-value store service in Python (standard library only). Create a package `kvstore/` (at least `kvstore/__init__.py` and `kvstore/storage.py` for persistence) plus a command-line entry `cli.py` at the project root. Values must persist on disk across separate process invocations. Write your own unit/integration tests."
  Contract section (black-box CLI — this is what the judge checks; internal module names beyond the required ones are free):
    - Files required: `cli.py` at solution root, and a `kvstore/` package directory with `__init__.py` and `storage.py` (multi-module requirement).
    - Persistence path: the store reads/writes the file given by env var `KVSTORE_PATH` if set, otherwise `./kvstore.db` in the current directory. (This lets each run be hermetic.)
    - CLI commands (run as `python3 cli.py <cmd> ...`):
        set <key> <value>   -> store the pair; exit 0.
        get <key>           -> print the stored value on its own line to stdout; exit 0. If the key does not exist: print nothing to stdout and exit 1.
        delete <key>        -> remove the key if present; exit 0 whether or not it existed (idempotent).
        list                -> print all keys, one per line, sorted ascending; exit 0 (no output if empty).
    - Persistence guarantee: a value `set` in one process invocation is returned by `get` in a later, separate invocation (same KVSTORE_PATH).
    - Keys and values are non-empty strings without newlines.
  Add a note: "Standard library only. Do not assume any specific hidden test; just satisfy the CLI contract above. Internal structure beyond the required files is up to you, but it must remain multi-module."

Make the contract section unambiguous about exit codes (get-miss = 1, delete-missing = 0) since the judge keys on these.
  </action>
  <verify>
`test -f benchmark/tasks/l3-kvstore/PROMPT.md` exits 0.
`grep -q "cli.py" benchmark/tasks/l3-kvstore/PROMPT.md && grep -q "KVSTORE_PATH" benchmark/tasks/l3-kvstore/PROMPT.md && grep -qi "storage.py" benchmark/tasks/l3-kvstore/PROMPT.md` exits 0.
  </verify>
  <done>L3 prompt requires a multi-module kvstore/ package + cli.py, and pins the set/get/delete/list CLI contract including exit codes (get-miss=1, delete idempotent=0), the KVSTORE_PATH persistence path, and cross-process persistence. No hidden-test reference.</done>
</task>

</tasks>

<verification>
- All four files exist under benchmark/.
- Each PROMPT.md is self-contained, stdlib-only, and contains an explicit contract section a black-box test can verify.
- README documents the exit-0 pass criterion and the judge invocation convention that Plan 02 tests will implement.
- No PROMPT.md references a hidden test or any tool-specific wording.
</verification>

<success_criteria>
- benchmark/README.md + 3 PROMPT.md files exist at fixed canonical locations (TASK-01, TASK-03).
- Pass criterion is objectively defined as "independent test exits 0" (TASK-02), documented in README.
- Each task is stated as Python-stdlib-only.
- Contracts are precise enough that one tool-agnostic test per level (Plan 02) can judge any tool's output.
</success_criteria>

<output>
After completion, create `.planning/phases/01-fixed-tasks/01-01-SUMMARY.md` per the summary template, listing the files created and quoting the exact contract (signatures / CLI / stdout format) for each level so Plan 02 can mirror them.
</output>
