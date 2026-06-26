#!/usr/bin/env python3
"""L7 reference — HTTP key-value API server (stdlib http.server)."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from kvapi import storage


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _send(self, code, body=b"", ctype="text/plain"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _key(self):
        # path like /kv/<key> or /kv
        path = self.path.split("?", 1)[0]
        if path == "/kv" or path == "/kv/":
            return None
        if path.startswith("/kv/"):
            return path[len("/kv/"):]
        return False  # not a kv path

    def do_GET(self):
        k = self._key()
        if k is False:
            return self._send(404)
        if k is None:  # list keys
            return self._send(200, json.dumps(storage.keys()), "application/json")
        v = storage.get(k)
        if v is None:
            return self._send(404)
        self._send(200, v)

    def do_PUT(self):
        k = self._key()
        if not k:  # None or False → no key
            return self._send(404)
        n = int(self.headers.get("Content-Length", 0) or 0)
        value = self.rfile.read(n).decode("utf-8") if n else ""
        storage.put(k, value)
        self._send(200, "ok")

    def do_DELETE(self):
        k = self._key()
        if not k:
            return self._send(404)
        self._send(200, "ok") if storage.delete(k) else self._send(404)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, required=True)
    args = ap.parse_args()
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
