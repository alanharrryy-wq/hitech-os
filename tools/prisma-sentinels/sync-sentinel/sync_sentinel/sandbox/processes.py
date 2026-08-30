from __future__ import annotations

import socket
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class OwnedProcessRegistry:
    processes: list[subprocess.Popen] = field(default_factory=list)

    def start(self, cmd: list[str], *, cwd: Path, env: dict[str, str], stdout=None) -> subprocess.Popen:
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            env=env,
            stdout=stdout,
            stderr=subprocess.STDOUT if stdout is not None else subprocess.PIPE,
            text=True,
        )
        self.processes.append(proc)
        return proc

    def stop_all(self, timeout: float = 8.0) -> dict[str, object]:
        rows: list[dict[str, object]] = []
        for proc in reversed(self.processes):
            row: dict[str, object] = {"pid": proc.pid}
            if proc.poll() is not None:
                row.update({"alreadyExited": True, "returncode": proc.returncode})
                rows.append(row)
                continue
            proc.terminate()
            try:
                proc.wait(timeout=timeout)
                row.update({"terminated": True, "returncode": proc.returncode})
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
                row.update({"killed": True, "returncode": proc.returncode})
            rows.append(row)
        orphan_pids = [proc.pid for proc in self.processes if proc.poll() is None]
        return {"processes": rows, "orphanPids": orphan_pids, "pass": not orphan_pids}


def allocate_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])
