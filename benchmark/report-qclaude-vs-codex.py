#!/usr/bin/env python3
"""Generate benchmark/RESULTS-qclaude-vs-codex.md — a self-contained comparison of
qclaude (Claude Code → local qwen-122b via claude-code-proxy, --model opus) against
codex (Codex CLI → local qwen-122b), both driven over the SAME frozen task PROMPTs
under the SAME isolated-run harness (benchmark/run.sh) and scored by the SAME
independent judges (tasks/<level>/test.py).

Why this is a fair "same-model" comparison:
  - codex   → qwen-122b-codex  → role-shim :8011 → mlx :8001  (qwen122b weights)
  - qclaude → qwen-122b-claude → role-shim :8011 → mlx :8001  (qwen122b weights)
  Both hit the identical local qwen-122b; only the client + API-translation path
  differs (codex: Responses→chat; qclaude: Anthropic→chat via claude-code-proxy).

Inputs (best-effort, overridable):
  - codex cells:   benchmark/.runs/results-14.json (filtered to tool==codex), or
                   argv[1] if given (a results.json with codex cells).
  - qclaude cells: latest benchmark/.runs/qclaude-<level>-*/meta.json per level.

This is PURE FORMATTING over already-scored meta — it re-runs NO agent and NO judge.
benchmark/.runs/ is gitignored, so the generated .md bakes the metrics + transcript
excerpts into a durable committed artifact (same contract as RESULTS.md).

stdlib-only: json, os, sys, glob, re.
"""

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
RUNS = os.path.join(HERE, ".runs")
OUT_PATH = os.path.join(HERE, "RESULTS-qclaude-vs-codex.md")

DASH = "—"
LEVEL_ORDER = ["l1-fib", "l2-wordstat", "l3-kvstore", "l4-calc", "l5-todo",
               "l6-csvstat", "l7-kvapi"]
# Comparison columns: codex (baseline) vs qclaude (new).
TOOLS = ["codex", "qclaude"]
ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #
def load_codex_cells(argv):
    """codex cells from argv[1] or .runs/results-14.json, filtered to tool==codex."""
    path = argv[1] if len(argv) > 1 else os.path.join(RUNS, "results-14.json")
    if not os.path.isfile(path):
        sys.exit(f"error: no codex results.json at {path!r} "
                 "(pass one as argv[1], or run the codex matrix first)")
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return [c for c in data if c.get("tool") == "codex"]


def load_qclaude_cells():
    """Latest qclaude meta.json per level from .runs/qclaude-<level>-*/meta.json."""
    cells = []
    for level in LEVEL_ORDER:
        # run dirs are qclaude-<level>-<stamp>; newest by name (stamp sorts).
        matches = sorted(glob.glob(os.path.join(RUNS, f"qclaude-{level}-*")))
        meta = None
        for d in reversed(matches):
            mp = os.path.join(d, "meta.json")
            if os.path.isfile(mp):
                with open(mp, encoding="utf-8") as fh:
                    meta = json.load(fh)
                break
        if meta:
            cells.append(meta)
    return cells


# --------------------------------------------------------------------------- #
# Field formatting (best-effort: missing -> em dash)
# --------------------------------------------------------------------------- #
def fmt_success(c):
    p = c.get("passed")
    return "PASS" if p is True else ("FAIL" if p is False else "ERROR")


def fmt_time(c):
    d = c.get("duration_seconds")
    return f"{d}s" if isinstance(d, (int, float)) else DASH


def fmt_steps(c):
    s, m = c.get("steps"), c.get("step_method")
    if s is None and not m:
        return DASH
    return f"{DASH if s is None else s} ({m or 'method unknown'})"


def fmt_size(c):
    f, loc = c.get("files"), c.get("loc")
    return f"{DASH if f is None else f'{f}f'} / {DASH if loc is None else f'{loc}loc'}"


def find_cell(cells, level):
    for c in cells:
        if c.get("level") == level:
            return c
    return None


def levels_in(by_tool):
    present = {c.get("level") for cells in by_tool.values() for c in cells if c.get("level")}
    ordered = [lv for lv in LEVEL_ORDER if lv in present]
    ordered += sorted(lv for lv in present if lv not in LEVEL_ORDER)
    return ordered


def transcript_path(c):
    rd, tr = c.get("run_dir"), c.get("transcript") or "transcript.log"
    if not rd:
        return None
    return tr if os.path.isabs(tr) else os.path.join(rd, tr)


def read_excerpt(path, head=12, tail=8):
    if not path or not os.path.isfile(path):
        return [], "transcript unavailable (.runs/ is gitignored)"
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            raw = fh.read()
    except OSError as exc:
        return [], f"transcript unreadable: {exc}"
    lines = [ANSI_RE.sub("", ln).rstrip() for ln in raw.splitlines()]
    lines = [ln for ln in lines if ln.strip()]
    if len(lines) <= head + tail:
        return lines, ""
    return lines[:head] + ["    ... (excerpt trimmed) ..."] + lines[-tail:], ""


# --------------------------------------------------------------------------- #
# Markdown builders
# --------------------------------------------------------------------------- #
def build_provenance(by_tool):
    cx, qc = by_tool["codex"], by_tool["qclaude"]
    cx_model = cx[0].get("model", DASH) if cx else DASH
    qc_model = qc[0].get("model", DASH) if qc else DASH
    return "\n".join([
        "# Benchmark Results — qclaude vs codex (local qwen-122b)",
        "",
        f"- **Tools:** `codex` (Codex CLI) vs `qclaude` (Claude Code → local qwen via claude-code-proxy, `--model opus`)",
        f"- **Model(s):** codex → `{cx_model}`, qclaude → `{qc_model}`",
        "  - **Same underlying weights.** Both resolve to the local **qwen-122b** "
        "(`/Users/ohama/llm-system/models/qwen122b`) served through role-shim `:8011` "
        "→ mlx `:8001`. Only the client and API-translation path differ "
        "(codex: Responses→chat; qclaude: Anthropic→chat via claude-code-proxy `:8082`). "
        "qclaude is pinned to `--model opus` so it hits the 122b tier, not the 35b "
        "Sonnet/Haiku tier — making this a like-for-like model comparison.",
        f"- **Levels:** {len(levels_in(by_tool))} (L1–L7), one cell per tool per level",
        "",
        "> Durable record: `benchmark/.runs/` is gitignored, so the metrics table and "
        "transcript excerpts below bake the evidence into version control.",
        "",
    ])


def build_matrix(by_tool):
    out = [
        "## Results matrix",
        "",
        "| Tool | Level | Success | Time | Steps (step_method) | Size (files / loc) |",
        "|------|-------|---------|------|---------------------|--------------------|",
    ]
    for level in levels_in(by_tool):
        for tool in TOOLS:
            c = find_cell(by_tool[tool], level)
            if c is None:
                out.append(f"| {tool} | {level} | ERROR | {DASH} | {DASH} | {DASH} |")
                continue
            out.append(f"| {tool} | {level} | {fmt_success(c)} | {fmt_time(c)} | "
                       f"{fmt_steps(c)} | {fmt_size(c)} |")
    out.append("")
    return "\n".join(out)


def build_scoreboard(by_tool):
    levels = levels_in(by_tool)
    out = ["### Scoreboard", ""]
    for tool in TOOLS:
        cells = by_tool[tool]
        passed = sum(1 for lv in levels if (find_cell(cells, lv) or {}).get("passed") is True)
        times = [find_cell(cells, lv).get("duration_seconds") for lv in levels
                 if find_cell(cells, lv) and isinstance(find_cell(cells, lv).get("duration_seconds"), (int, float))]
        total_t = sum(times) if times else 0
        out.append(f"- **{tool}**: {passed}/{len(levels)} passed · total wall-clock {total_t}s")
    out.append("")
    return "\n".join(out)


def build_reading_note():
    return "\n".join([
        "### Reading the numbers",
        "",
        "- **Success** is decided ONLY by each level's independent black-box judge "
        "(`tasks/<level>/test.py`) re-run against the files the agent produced — never the "
        "tool's own self-report.",
        "- **Steps are NOT directly comparable across tools** (different units, shown with "
        "`step_method`):",
        "  - **codex** = count of `exec` tool-call blocks in the transcript.",
        "  - **qclaude** = count of `tool_use` events in the `--output-format stream-json` "
        "transcript (Write/Edit/Bash/Read…).",
        "  Compare the *shape* of the work, not the raw integers.",
        "- **Time is heavily skewed by the path, not just the model.** qclaude runs through "
        "claude-code-proxy with **prompt caching disabled** (caching only works in Anthropic-"
        "native format) and stream-json, so every turn resends full context — expect qclaude "
        "to be much slower per task than codex even though the weights are identical. Read "
        "time as a *path* cost, not a model-quality signal.",
        "- **Size** = files + total LOC the agent produced, excluding harness artifacts.",
        "",
    ])


def build_notes():
    return "\n".join([
        "### Notes & honesty (read this)",
        "",
        "The headline is **qclaude 6/7 vs codex 5/7**, but the two failure profiles matter "
        "more than the count — and one qclaude failure is a layout artifact, disclosed here "
        "rather than buried:",
        "",
        "1. **L3-kvstore — qclaude PASS, codex FAIL (the real divergence).** codex's L3 is a "
        "genuine model-loop degeneration: its first action is `mkdir -p kvstore` (empty "
        "stdout), then qwen-122b re-emits its preamble with no tool call, so `codex exec` "
        "exits clean with **0 files**. Same weights under Claude Code's agent loop completed "
        "the multi-module package (9 files / 376 loc, all 17 judge tests pass). This is a "
        "*harness/agent-loop* difference, not a model-capability one — the model is identical.",
        "2. **L7-kvapi — both FAIL, but not the same kind of fail.**",
        "   - **codex**: same degeneration as L3 — `mkdir kvapi`, preamble, exit, **0 files**. "
        "Built nothing.",
        "   - **qclaude**: actually built a working HTTP service — its own pytest shows "
        "**18/18 functional tests pass** (only a server-shutdown `TimeoutExpired` at teardown). "
        "It FAILS the independent judge for a **layout reason**: it nested everything under a "
        "`solution/` subdir, and the frozen contract's judge requires `serve.py` at the "
        "run-dir **root** (`FAIL l7-kvapi: missing serve.py at solution root`). So qclaude's "
        "L7 is a contract-compliance/layout miss, not an inability to build the service.",
        "3. **Time is a path cost, not a model signal.** qclaude is ~2–25× slower per task. "
        "Both tools hit the *same* local qwen-122b, but qclaude's Anthropic→chat proxy path "
        "**disables prompt caching** (caching only works in Anthropic-native format) and uses "
        "stream-json, so full context is resent every turn. Don't read qclaude's longer times "
        "as the model being slower — it's the translation path.",
        "4. **Steps use different units** (codex `exec` blocks vs qclaude `tool_use` events) — "
        "compare the shape of the work, not the integers.",
        "",
    ])


def build_per_level(by_tool):
    out = ["## Per-level codex vs qclaude difference", ""]
    for level in levels_in(by_tool):
        cx = find_cell(by_tool["codex"], level)
        qc = find_cell(by_tool["qclaude"], level)
        out.append(f"### {level}")
        out.append("")
        if cx is None or qc is None:
            out.append("_One tool's cell is missing — cannot compare._\n")
            continue
        cx_t, qc_t = cx.get("duration_seconds"), qc.get("duration_seconds")
        if isinstance(cx_t, (int, float)) and isinstance(qc_t, (int, float)):
            faster = "codex" if cx_t < qc_t else "qclaude"
            out.append(f"- **Time:** codex {cx_t}s vs qclaude {qc_t}s "
                       f"(Δ {qc_t - cx_t:+d}s; **{faster}** faster).")
        else:
            out.append(f"- **Time:** codex {fmt_time(cx)} vs qclaude {fmt_time(qc)}.")
        out.append("- **Process (units differ — not directly comparable):** "
                   f"codex {fmt_steps(cx)} vs qclaude {fmt_steps(qc)}.")
        cf, cl, qf, ql = cx.get("files"), cx.get("loc"), qc.get("files"), qc.get("loc")
        if all(isinstance(v, (int, float)) for v in (cf, cl, qf, ql)):
            out.append(f"- **Output:** codex {cf}f/{cl}loc vs qclaude {qf}f/{ql}loc "
                       f"(Δ {qf - cf:+d}f / {ql - cl:+d}loc).")
        else:
            out.append(f"- **Output:** codex {fmt_size(cx)} vs qclaude {fmt_size(qc)}.")
        out.append(f"- **Verdict:** codex **{fmt_success(cx)}**, qclaude **{fmt_success(qc)}**.")
        out.append("")
    return "\n".join(out)


def build_transcripts(by_tool):
    out = ["## Transcript references & evidence excerpts", "",
           "Short ANSI-stripped excerpts embedded so the evidence survives in the committed "
           "report even though `benchmark/.runs/` is gitignored.\n"]
    for level in levels_in(by_tool):
        for tool in TOOLS:
            c = find_cell(by_tool[tool], level)
            if c is None:
                continue
            tp = transcript_path(c)
            out.append(f"### {tool} / {level} — {fmt_success(c)} in {fmt_time(c)}")
            out.append("")
            out.append(f"- **Transcript:** `{tp or '(no run_dir recorded)'}`")
            out.append(f"- **Steps:** {fmt_steps(c)} · **Size:** {fmt_size(c)}")
            out.append("")
            excerpt, note = read_excerpt(tp)
            if note:
                out.append(f"_{note}_\n")
            if excerpt:
                out.append("```text")
                out.extend(excerpt)
                out.append("```")
                out.append("")
    return "\n".join(out)


def main(argv):
    by_tool = {"codex": load_codex_cells(argv), "qclaude": load_qclaude_cells()}
    if not by_tool["qclaude"]:
        sys.exit("error: no qclaude run dirs found under .runs/qclaude-* — run the qclaude "
                 "matrix first (bash run.sh qclaude l1 .. l7).")
    sections = [
        build_provenance(by_tool),
        build_matrix(by_tool),
        build_scoreboard(by_tool),
        build_reading_note(),
        build_notes(),
        build_per_level(by_tool),
        build_transcripts(by_tool),
        "---",
        "",
        "_Generated by `benchmark/report-qclaude-vs-codex.py`. Pure formatting over "
        "already-scored meta — no agent or judge is re-run._",
        "",
    ]
    md = "\n".join(sections).rstrip() + "\n"
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"wrote {OUT_PATH} "
          f"(codex {len(by_tool['codex'])} cells, qclaude {len(by_tool['qclaude'])} cells)")


if __name__ == "__main__":
    main(sys.argv)
