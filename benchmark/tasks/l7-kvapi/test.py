#!/usr/bin/env python3
"""L7 judge — independent, stdlib-only, black-box over HTTP.

Starts `python3 serve.py --port <ephemeral>` as a subprocess in the solution dir with a
hermetic KVAPI_PATH, waits for it to listen, exercises PUT/GET/DELETE/list + status codes,
then restarts a fresh server to confirm on-disk persistence. Never trusts self-report.

Usage:  python3 test.py [solution_dir]   (default: current directory)
Exit 0 = PASS, nonzero = FAIL.
"""
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

SOL = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
ENTRY = os.path.join(SOL, "serve.py")
PKG = os.path.join(SOL, "kvapi")

procs = []


def fail(msg):
    for p in procs:
        try:
            p.terminate()
        except Exception:
            pass
    print(f"FAIL l7-kvapi: {msg}")
    sys.exit(1)


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def start(port, env):
    p = subprocess.Popen([sys.executable, "serve.py", "--port", str(port)], cwd=SOL,
                         env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    procs.append(p)
    deadline = time.time() + 15
    while time.time() < deadline:
        if p.poll() is not None:
            fail(f"server exited early (rc={p.returncode}) on port {port}")
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return p
        except OSError:
            time.sleep(0.15)
    fail(f"server did not start listening on {port} within 15s")


def req(method, port, path, data=None):
    url = f"http://127.0.0.1:{port}{path}"
    body = data.encode("utf-8") if isinstance(data, str) else data
    r = urllib.request.Request(url, data=body, method=method)
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


def stop(p):
    p.terminate()
    try:
        p.wait(timeout=10)
    except subprocess.TimeoutExpired:
        p.kill()


def main():
    if not os.path.isfile(ENTRY):
        fail("missing serve.py at solution root")
    if not (os.path.isdir(PKG) and os.path.isfile(os.path.join(PKG, "__init__.py"))
            and os.path.isfile(os.path.join(PKG, "storage.py"))):
        fail("missing kvapi/ package (need __init__.py and storage.py)")

    tmp = tempfile.mkdtemp()
    env = dict(os.environ, KVAPI_PATH=os.path.join(tmp, "kvapi.db"))

    # ---- server #1 ----
    port = free_port()
    p1 = start(port, env)

    st, _ = req("PUT", port, "/kv/hello", "world")
    if st != 200:
        fail(f"PUT /kv/hello → {st} (want 200)")
    st, body = req("GET", port, "/kv/hello")
    if st != 200 or body != "world":
        fail(f"GET /kv/hello → {st} body={body!r} (want 200/'world')")
    req("PUT", port, "/kv/alpha", "1")
    req("PUT", port, "/kv/beta", "2")
    st, body = req("GET", port, "/kv")
    if st != 200:
        fail(f"GET /kv → {st} (want 200)")
    try:
        import json
        keys = json.loads(body)
    except ValueError:
        fail(f"GET /kv body not JSON: {body!r}")
    if keys != sorted(["hello", "alpha", "beta"]):
        fail(f"GET /kv keys={keys} (want sorted ['alpha','beta','hello'])")
    st, _ = req("GET", port, "/kv/missing")
    if st != 404:
        fail(f"GET missing → {st} (want 404)")

    stop(p1)

    # ---- server #2 (restart, same KVAPI_PATH): persistence must hold ----
    port2 = free_port()
    p2 = start(port2, env)
    st, body = req("GET", port2, "/kv/hello")
    if st != 200 or body != "world":
        fail(f"after restart GET /kv/hello → {st} body={body!r} (persistence broken)")
    st, _ = req("DELETE", port2, "/kv/hello")
    if st != 200:
        fail(f"DELETE existing → {st} (want 200)")
    st, _ = req("GET", port2, "/kv/hello")
    if st != 404:
        fail(f"GET after delete → {st} (want 404)")
    st, _ = req("DELETE", port2, "/kv/hello")
    if st != 404:
        fail(f"DELETE missing → {st} (want 404)")
    stop(p2)

    print("PASS l7-kvapi")
    sys.exit(0)


if __name__ == "__main__":
    main()
