#!/usr/bin/env python3
"""L5 reference — JSON-backed todo storage (persists across processes)."""
import json
import os


def _path():
    return os.environ.get("TODO_PATH", "./todos.json")


def load():
    """Return dict {'next': int, 'tasks': [{'id','text','done'}, ...]}."""
    p = _path()
    if not os.path.exists(p):
        return {"next": 1, "tasks": []}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save(state):
    with open(_path(), "w", encoding="utf-8") as f:
        json.dump(state, f)


def add(text):
    s = load()
    tid = s["next"]
    s["tasks"].append({"id": tid, "text": text, "done": False})
    s["next"] = tid + 1
    save(s)
    return tid


def set_done(tid):
    s = load()
    for t in s["tasks"]:
        if t["id"] == tid:
            t["done"] = True
            save(s)
            return True
    return False


def remove(tid):
    s = load()
    for i, t in enumerate(s["tasks"]):
        if t["id"] == tid:
            del s["tasks"][i]
            save(s)
            return True
    return False


def items():
    return sorted(load()["tasks"], key=lambda t: t["id"])
