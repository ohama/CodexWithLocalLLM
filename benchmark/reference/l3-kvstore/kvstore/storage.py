"""L3 reference persistence layer (stdlib only).

A tiny key-value Store backed by a JSON file. The file path comes from the
environment variable KVSTORE_PATH if set, else ./kvstore.db in the cwd, so each
run can be made hermetic.
"""

import json
import os

_MISSING = object()


def resolve_path():
    """Return the store file path: $KVSTORE_PATH or ./kvstore.db."""
    return os.environ.get("KVSTORE_PATH") or os.path.join(os.getcwd(), "kvstore.db")


class Store:
    """JSON-file-backed key-value store with cross-process persistence."""

    def __init__(self, path=None):
        self.path = path or resolve_path()

    def _load(self):
        try:
            with open(self.path, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, ValueError):
            return {}

    def _save(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def set(self, key, value):
        data = self._load()
        data[key] = value
        self._save(data)

    def get(self, key, default=_MISSING):
        data = self._load()
        if key in data:
            return data[key]
        return default

    def delete(self, key):
        data = self._load()
        if key in data:
            del data[key]
            self._save(data)

    def keys(self):
        return sorted(self._load().keys())
