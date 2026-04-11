from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://127.0.0.1:8101"


def _wait_for_health(timeout_s: float = 10.0) -> None:
    start = time.time()
    while time.time() - start <= timeout_s:
        try:
            with request.urlopen(f"{BASE_URL}/health", timeout=1.0) as response:
                if response.status == 200:
                    return
        except Exception:
            pass
        time.sleep(0.2)
    raise RuntimeError("Timed out waiting for ai-agent health")


def _get(path: str) -> dict:
    with request.urlopen(f"{BASE_URL}{path}", timeout=3.0) as response:
        return json.loads(response.read().decode("utf-8"))


def _post(path: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        f"{BASE_URL}{path}",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with request.urlopen(req, timeout=3.0) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    proc = subprocess.Popen(
        [sys.executable, "-m", "app.main", "--host", "127.0.0.1", "--port", "8101"],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        _wait_for_health()
        capabilities = _get("/capabilities")
        result = _post(
            "/jobs/run",
            {
                "jobId": "smoke-ai-001",
                "kind": "summarize_text",
                "input": {"text": "Hello world. Another sentence."},
                "requestedAtUtc": "2026-01-01T00:00:00Z",
                "flags": {
                    "enableAiExecution": True,
                    "enableCapabilitiesProxy": False,
                    "enableExperimentalUi": False,
                    "enableHealthDashboard": False,
                },
            },
        )
        print("[smoke-ai-agent] capabilities", json.dumps(capabilities, sort_keys=True))
        print("[smoke-ai-agent] result", json.dumps(result, sort_keys=True))
        return 0
    except (RuntimeError, error.URLError, json.JSONDecodeError) as exc:
        print(f"[smoke-ai-agent] FAILED: {exc}", file=sys.stderr)
        return 1
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3.0)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
