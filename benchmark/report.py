#!/usr/bin/env python3
"""Generate the committed comparison report (benchmark/RESULTS.md) from the
aggregated matrix metrics (results.json) produced by Plan 04-01.

Usage:
    python3 benchmark/report.py [results.json | matrix_dir]

Input resolution:
  - argv[1] optional: a results.json path OR a matrix dir (uses <dir>/results.json).
  - default: auto-discover the latest matrix:
        sorted(glob("benchmark/.runs/matrix-*/results.json"))[-1]
  - if none found: exit nonzero with a clear message.

This is PURE FORMATTING over already-scored results.json. It re-runs no agent
and no judge (~0 LLM time) and is idempotent: same results.json -> same RESULTS.md.

Why this file exists: benchmark/.runs/ is GITIGNORED, so the raw run dirs never
enter version control. RESULTS.md must therefore be SELF-CONTAINED — it bakes the
metrics table plus short transcript excerpts/references into a durable committed
artifact (REP-02 + REP-03).

Reporting constraint carried from Phase 3: step counts use DIFFERENT units per
tool (codex = count of 'exec' tool-call blocks; openhands = 'Number of agent
messages'). step_method is surfaced beside every step number; raw step counts are
NEVER compared as identical units in the per-level summaries.

stdlib-only: json, os, sys, glob, re.
"""

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT_PATH = os.path.join(HERE, "RESULTS.md")

DASH = "—"
LEVELS = ["l1-fib", "l2-wordstat", "l3-kvstore"]
TOOLS = ["codex", "openhands"]

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


# --------------------------------------------------------------------------- #
# Input resolution
# --------------------------------------------------------------------------- #
def resolve_results_path(argv):
    """Return a results.json path from argv[1] (file or matrix dir) or the
    latest matrix dir. Exit nonzero if nothing is found."""
    if len(argv) > 1:
        arg = argv[1]
        if os.path.isdir(arg):
            cand = os.path.join(arg, "results.json")
        else:
            cand = arg
        if not os.path.isfile(cand):
            sys.exit(f"error: no results.json at {cand!r}")
        return cand

    pattern = os.path.join(REPO, "benchmark", ".runs", "matrix-*", "results.json")
    matches = sorted(glob.glob(pattern))
    if not matches:
        sys.exit(
            "error: no matrix results.json found "
            f"(looked for {pattern}). Run benchmark/run-matrix.sh first."
        )
    return matches[-1]


def load_cells(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        sys.exit(f"error: {path} did not contain a JSON list of cells")
    return data


# --------------------------------------------------------------------------- #
# Field access (best-effort: missing -> em dash)
# --------------------------------------------------------------------------- #
def g(cell, key, default=DASH):
    val = cell.get(key)
    return default if val is None else val


def fmt_success(cell):
    p = cell.get("passed")
    if p is True:
        return "PASS"
    if p is False:
        return "FAIL"
    return "ERROR"


def fmt_time(cell):
    d = cell.get("duration_seconds")
    return f"{d}s" if isinstance(d, (int, float)) else DASH


def fmt_steps(cell):
    s = cell.get("steps")
    m = cell.get("step_method")
    if s is None and not m:
        return DASH
    s_txt = DASH if s is None else str(s)
    m_txt = m if m else "method unknown"
    return f"{s_txt} ({m_txt})"


def fmt_size(cell):
    f = cell.get("files")
    loc = cell.get("loc")
    f_txt = DASH if f is None else f"{f}f"
    loc_txt = DASH if loc is None else f"{loc}loc"
    return f"{f_txt} / {loc_txt}"


def find_cell(cells, tool, level):
    for c in cells:
        if c.get("tool") == tool and c.get("level") == level:
            return c
    return None


def transcript_path(cell):
    rd = cell.get("run_dir")
    tr = cell.get("transcript") or "transcript.log"
    if not rd:
        return None
    if os.path.isabs(tr):
        return tr
    return os.path.join(rd, tr)


def read_excerpt(path, head=14, tail=10):
    """Return (lines_list, note). ANSI-stripped. Head + tail of a transcript,
    best-effort. Returns ([], reason) if unavailable."""
    if not path or not os.path.isfile(path):
        return [], "transcript unavailable (run dir not present; .runs/ is gitignored)"
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            raw = fh.read()
    except OSError as exc:
        return [], f"transcript unreadable: {exc}"
    lines = [ANSI_RE.sub("", ln).rstrip() for ln in raw.splitlines()]
    # drop blank lines for a tighter excerpt
    lines = [ln for ln in lines if ln.strip()]
    if len(lines) <= head + tail:
        return lines, ""
    excerpt = lines[:head] + ["    ... (excerpt trimmed) ..."] + lines[-tail:]
    return excerpt, ""


# --------------------------------------------------------------------------- #
# Markdown builders
# --------------------------------------------------------------------------- #
def build_provenance(results_path, cells):
    rel = os.path.relpath(results_path, REPO)
    matrix_dir = os.path.basename(os.path.dirname(results_path))
    ts = matrix_dir.replace("matrix-", "") if matrix_dir.startswith("matrix-") else matrix_dir
    models = {}
    for c in cells:
        models.setdefault(c.get("tool", "?"), c.get("model", DASH))
    model_bits = ", ".join(f"{t} → `{m}`" for t, m in sorted(models.items()))
    lines = [
        "# Benchmark Results — codex vs openhands (qwen-122b)",
        "",
        f"- **Source:** `{rel}`",
        f"- **Matrix timestamp:** {ts}",
        f"- **Model(s):** {model_bits}",
        "  - Both are the same local **qwen-122b** family served at "
        "`http://localhost:4000/v1`; the two tools merely report the model string "
        "differently (codex: `qwen-122b-codex`, openhands: `openai/qwen-122b`).",
        f"- **Cells:** {len(cells)} (2 tools × 3 levels)",
        "",
        "> This report is the **durable** record. `benchmark/.runs/` is gitignored, so the "
        "raw run directories are not committed — the metrics table and transcript excerpts "
        "below bake the evidence into version control (REP-02 + REP-03).",
        "",
    ]
    return "\n".join(lines)


def build_matrix_table(cells):
    out = [
        "## Results matrix (REP-02)",
        "",
        "| Tool | Level | Success | Time | Steps (step_method) | Size (files / loc) |",
        "|------|-------|---------|------|---------------------|--------------------|",
    ]
    for level in LEVELS:
        for tool in TOOLS:
            c = find_cell(cells, tool, level)
            if c is None:
                out.append(f"| {tool} | {level} | ERROR | {DASH} | {DASH} | {DASH} |")
                continue
            out.append(
                f"| {tool} | {level} | {fmt_success(c)} | {fmt_time(c)} | "
                f"{fmt_steps(c)} | {fmt_size(c)} |"
            )
    out.append("")
    return "\n".join(out)


def build_reading_note():
    return "\n".join(
        [
            "### Reading the numbers",
            "",
            "- **Success** is decided ONLY by each level's independent black-box judge "
            "(`tasks/<level>/test.py`) re-run against the files the agent produced — the "
            "tool's own \"all tests pass\" claim is never trusted (MET-01).",
            "- **Steps are NOT directly comparable across tools.** The two tools expose "
            "different units, so each count is shown with its `step_method`:",
            "  - **codex** = count of `exec` tool-call blocks in the transcript.",
            "  - **openhands** = the `Number of agent messages` reported in its conversation summary.",
            "  A codex `10` and an openhands `16` are different kinds of events — compare the "
            "*shape* of the work, never the raw integers as if identical.",
            "- **Size** = files produced in the run dir and total lines of code, excluding "
            "harness artifacts (`transcript.log`, `meta.json`, `__pycache__/`) (MET-04).",
            "",
        ]
    )


def build_honesty_note():
    return "\n".join(
        [
            "### Scoring honesty note (read this)",
            "",
            "Two corrections were applied to the first raw matrix; both are disclosed here "
            "rather than silently baked into the numbers:",
            "",
            "1. **openhands L2 / L3 were initially mis-scored FAIL** because of a harness "
            "isolation leak: an early `run.sh` invoked openhands with `--file` pointing at the "
            "prompt, which anchored the agent's working directory to the *canonical task dir* "
            "instead of the isolated run dir, so its output never landed where the judge looked. "
            "After switching to an inline `--task` (no workdir leak), L2 and L3 were **re-run** "
            "and both **PASS**. The numbers above are from those clean re-runs.",
            "2. **codex L3 (`l3-kvstore`) is a GENUINE failure**, not a harness artifact. codex "
            "truncated at ~14s after only running `mkdir kvstore` — it produced an empty package "
            "(0 files, 0 loc) and the judge correctly fails it. This is reported as a real FAIL, "
            "not hidden or re-run away.",
            "",
        ]
    )


def build_transcripts(cells):
    out = ["## Transcript references & evidence excerpts (REP-03)", ""]
    out.append(
        "Each run's transcript path and a short ANSI-stripped excerpt are embedded below so "
        "the evidence survives in the committed report even though `benchmark/.runs/` is "
        "gitignored.\n"
    )
    for level in LEVELS:
        for tool in TOOLS:
            c = find_cell(cells, tool, level)
            if c is None:
                continue
            tp = transcript_path(c)
            disp = tp if tp else "(no run_dir recorded)"
            out.append(f"### {tool} / {level} — {fmt_success(c)} in {fmt_time(c)}")
            out.append("")
            out.append(f"- **Transcript:** `{disp}`")
            out.append(
                f"- **Steps:** {fmt_steps(c)} · **Size:** {fmt_size(c)}"
            )
            out.append("")
            excerpt, note = read_excerpt(tp)
            if note:
                out.append(f"_{note}_")
                out.append("")
            if excerpt:
                out.append("```text")
                out.extend(excerpt)
                out.append("```")
                out.append("")
    return "\n".join(out)


def build_per_level(cells):
    out = ["## Per-level codex vs openhands difference summary (REP-03)", ""]
    for level in LEVELS:
        cx = find_cell(cells, "codex", level)
        oh = find_cell(cells, "openhands", level)
        out.append(f"### {level}")
        out.append("")
        if cx is None or oh is None:
            out.append("_One tool's cell is missing for this level — cannot compare._")
            out.append("")
            continue

        cx_t = cx.get("duration_seconds")
        oh_t = oh.get("duration_seconds")
        if isinstance(cx_t, (int, float)) and isinstance(oh_t, (int, float)):
            delta = oh_t - cx_t
            faster = "codex" if cx_t < oh_t else "openhands"
            time_line = (
                f"- **Time:** codex {cx_t}s vs openhands {oh_t}s "
                f"(Δ {delta:+d}s; **{faster}** faster)."
            )
        else:
            time_line = f"- **Time:** codex {fmt_time(cx)} vs openhands {fmt_time(oh)}."
        out.append(time_line)

        out.append(
            "- **Process (units differ — not directly comparable):** "
            f"codex {fmt_steps(cx)} vs openhands {fmt_steps(oh)}."
        )

        cx_f, cx_l = cx.get("files"), cx.get("loc")
        oh_f, oh_l = oh.get("files"), oh.get("loc")
        if all(isinstance(v, (int, float)) for v in (cx_f, cx_l, oh_f, oh_l)):
            out.append(
                f"- **Output:** codex {cx_f}f/{cx_l}loc vs openhands {oh_f}f/{oh_l}loc "
                f"(Δ {oh_f - cx_f:+d}f / {oh_l - cx_l:+d}loc)."
            )
        else:
            out.append(
                f"- **Output:** codex {fmt_size(cx)} vs openhands {fmt_size(oh)}."
            )

        out.append(
            f"- **Verdict:** codex **{fmt_success(cx)}**, openhands **{fmt_success(oh)}**."
        )
        out.append("")
    return "\n".join(out)


def build_report(results_path, cells):
    sections = [
        build_provenance(results_path, cells),
        build_matrix_table(cells),
        build_reading_note(),
        build_honesty_note(),
        build_per_level(cells),
        build_transcripts(cells),
        "---",
        "",
        "_Generated by `benchmark/report.py` from the aggregated matrix metrics. "
        "Re-runnable and idempotent: same `results.json` → identical `RESULTS.md` "
        "(no agents or judges are re-run)._",
        "",
    ]
    return "\n".join(sections).rstrip() + "\n"


def main(argv):
    results_path = resolve_results_path(argv)
    cells = load_cells(results_path)
    md = build_report(results_path, cells)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"wrote {OUT_PATH} from {results_path} ({len(cells)} cells)")


if __name__ == "__main__":
    main(sys.argv)
