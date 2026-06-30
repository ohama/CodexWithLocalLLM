#!/usr/bin/env python3
"""Generate benchmark/RESULTS-3way-qwen.md — a self-contained 3-way comparison of
the SAME frozen tasks under the SAME harness + judges, across:

  - codex      Codex CLI            → qwen-122b-codex   (122b)
  - qclaude    Claude Code --opus   → qwen-122b-claude  (122b, same weights as codex)
  - qclaude35  Claude Code --sonnet → qwen-35b-claude   (35b, the fast tier)

The point of the 3-way: codex vs qclaude isolates the CLIENT/agent-loop (same 122b
weights); qclaude vs qclaude35 isolates the MODEL SIZE (same client, 122b vs 35b).

Inputs (best-effort):
  - codex     cells: .runs/results-14.json (filter tool==codex), or argv[1].
  - qclaude   cells: latest .runs/qclaude-<level>-*/meta.json   (opus/122b).
  - qclaude35 cells: latest .runs/qclaude35-<level>-*/meta.json (sonnet/35b).

Pure formatting over already-scored meta — re-runs NO agent and NO judge. The .md
bakes metrics + transcript excerpts into version control (.runs/ is gitignored).

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
OUT_PATH = os.path.join(HERE, "RESULTS-3way-qwen.md")

DASH = "—"
LEVEL_ORDER = ["l1-fib", "l2-wordstat", "l3-kvstore", "l4-calc", "l5-todo",
               "l6-csvstat", "l7-kvapi"]
# Display order + labels for the three tools.
TOOLS = ["codex", "qclaude", "qclaude35"]
LABEL = {"codex": "codex (122b)",
         "qclaude": "qclaude (122b/opus)",
         "qclaude35": "qclaude35 (35b/sonnet)"}
ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def load_codex_cells(argv):
    path = argv[1] if len(argv) > 1 else os.path.join(RUNS, "results-14.json")
    if not os.path.isfile(path):
        sys.exit(f"error: no codex results.json at {path!r}")
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return [c for c in data if c.get("tool") == "codex"]


def load_glob_cells(prefix):
    """Latest meta.json per level from .runs/<prefix>-<level>-*/meta.json.
    NB: prefix 'qclaude' does NOT match 'qclaude35-...' (different literal prefix)."""
    cells = []
    for level in LEVEL_ORDER:
        matches = sorted(glob.glob(os.path.join(RUNS, f"{prefix}-{level}-*")))
        for d in reversed(matches):
            mp = os.path.join(d, "meta.json")
            if os.path.isfile(mp):
                with open(mp, encoding="utf-8") as fh:
                    cells.append(json.load(fh))
                break
    return cells


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
    return None if not rd else (tr if os.path.isabs(tr) else os.path.join(rd, tr))


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


def build_provenance(by_tool):
    models = {t: (by_tool[t][0].get("model", DASH) if by_tool[t] else DASH) for t in TOOLS}
    return "\n".join([
        "# Benchmark Results — 3-way on local qwen (codex · qclaude 122b · qclaude35 35b)",
        "",
        "- **Tools & models:**",
        f"  - `codex` (Codex CLI) → `{models['codex']}` — **122b**",
        f"  - `qclaude` (Claude Code, `--model opus`) → `{models['qclaude']}` — **122b** (same weights as codex)",
        f"  - `qclaude35` (Claude Code, `--model sonnet`) → `{models['qclaude35']}` — **35b** (the fast tier)",
        "- **What each axis isolates:**",
        "  - **codex vs qclaude** = same 122b weights, different client/agent-loop (Codex Responses→chat vs Claude Code Anthropic→chat).",
        "  - **qclaude vs qclaude35** = same client (Claude Code), different model size (122b vs 35b).",
        "- All three: same frozen `tasks/<level>/PROMPT.md`, same isolated-run harness "
        "(`benchmark/run.sh`), same independent judges (`tasks/<level>/test.py`). All qwen "
        "served through role-shim → mlx (122b :8001 / 35b :8000).",
        f"- **Levels:** {len(levels_in(by_tool))} (L1–L7).",
        "",
        "> Durable record: `benchmark/.runs/` is gitignored — the table + excerpts below are the committed evidence.",
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
    out = ["### Scoreboard", "",
           "| Tool | Passed | Total wall-clock |",
           "|------|--------|------------------|"]
    for tool in TOOLS:
        cells = by_tool[tool]
        passed = sum(1 for lv in levels if (find_cell(cells, lv) or {}).get("passed") is True)
        times = [find_cell(cells, lv).get("duration_seconds") for lv in levels
                 if find_cell(cells, lv)
                 and isinstance(find_cell(cells, lv).get("duration_seconds"), (int, float))]
        out.append(f"| {LABEL[tool]} | {passed}/{len(levels)} | {sum(times)}s |")
    out.append("")
    return "\n".join(out)


def build_reading_note():
    return "\n".join([
        "### Reading the numbers",
        "",
        "- **Success** = each level's independent black-box judge (`tasks/<level>/test.py`) "
        "re-run against the produced files. Never the tool's self-report.",
        "- **Steps use different units** — codex = `exec` blocks; qclaude/qclaude35 = "
        "`tool_use` events in the stream-json transcript. Compare shape, not integers.",
        "- **Time is dominated by cold prefill of a large prompt — not by the model and not "
        "by 'caching'.** codex also runs on local mlx (no Anthropic caching either). Claude "
        "Code just sends a much larger prompt (system prompt + ~25 tool schemas + skills), "
        "and mlx re-prefills it cold every task (per-task time-to-first-token 79–196s here). "
        "Prefill is linear (~1.75s/1k tokens on this 122b). 35b being faster than 122b is a "
        "real model-size effect. See finding 5 below for the full measurement and levers.",
        "- **Size** = files + LOC produced, excluding harness artifacts.",
        "",
    ])


def build_per_level(by_tool):
    out = ["## Per-level breakdown", ""]
    for level in levels_in(by_tool):
        out.append(f"### {level}")
        out.append("")
        for tool in TOOLS:
            c = find_cell(by_tool[tool], level)
            if c is None:
                out.append(f"- **{LABEL[tool]}:** _missing_")
                continue
            out.append(f"- **{LABEL[tool]}:** {fmt_success(c)} · {fmt_time(c)} · "
                       f"{fmt_steps(c)} · {fmt_size(c)}")
        out.append("")
    return "\n".join(out)


def build_transcripts(by_tool):
    out = ["## Transcript references & evidence excerpts", "",
           "Short ANSI-stripped excerpts embedded so evidence survives in the committed report.\n"]
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
    by_tool = {
        "codex": load_codex_cells(argv),
        "qclaude": load_glob_cells("qclaude"),
        "qclaude35": load_glob_cells("qclaude35"),
    }
    for t in ("qclaude", "qclaude35"):
        if not by_tool[t]:
            sys.exit(f"error: no {t} run dirs under .runs/{t}-* — run that matrix first.")
    notes_path = os.path.join(HERE, "RESULTS-3way-notes.md")
    notes = ""
    if os.path.isfile(notes_path):
        with open(notes_path, encoding="utf-8") as fh:
            notes = fh.read().rstrip() + "\n"
    sections = [
        build_provenance(by_tool),
        build_matrix(by_tool),
        build_scoreboard(by_tool),
        build_reading_note(),
        notes if notes else "",
        build_per_level(by_tool),
        build_transcripts(by_tool),
        "---",
        "",
        "_Generated by `benchmark/report-3way.py`. Pure formatting over already-scored meta — "
        "no agent or judge re-run. Curated findings live in `RESULTS-3way-notes.md` (inlined above)._",
        "",
    ]
    md = "\n".join(s for s in sections if s).rstrip() + "\n"
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"wrote {OUT_PATH} "
          f"(codex {len(by_tool['codex'])}, qclaude {len(by_tool['qclaude'])}, "
          f"qclaude35 {len(by_tool['qclaude35'])} cells)")


if __name__ == "__main__":
    main(sys.argv)
