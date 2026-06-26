#!/usr/bin/env python3
"""L7 reference — JSON-file persistence for the KV API (survives restarts)."""
import json
import os
import threading

_lock = threading.Lock()


def _path():
    return os.environ.get("KVAPI_PATH", "./kvapi.db")


def _load():
    p = _path()
    if not os.path.exists(p):
        return {}
    with open(p, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except ValueError:
            return {}


def _save(d):
    with open(_path(), "w", encoding="utf-8") as f:
        json.dump(d, f)


def get(key):
    with _lock:
        return _load().get(key)


def put(key, value):
    with _lock:
        d = _load()
        d[key] = value
        _save(d)


def delete(key):
    with _lock:
        d = _load()
        if key in d:
            del d[key]
            _save(d)
            return True
        return False


def keys():
    with _lock:
        return sorted(_load().keys())
