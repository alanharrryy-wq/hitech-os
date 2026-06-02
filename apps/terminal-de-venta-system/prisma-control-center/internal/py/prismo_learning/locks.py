# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Tiny cross-process lock file helper for store writes."""
from __future__ import annotations
from pathlib import Path
import os, time

class StoreLock:
    def __init__(self, path: str | Path, timeout: float = 10.0) -> None:
        self.path = Path(path)
        self.timeout = timeout
        self.acquired = False
    def __enter__(self):
        start = time.time()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        while True:
            try:
                fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                self.acquired = True
                return self
            except FileExistsError:
                if time.time() - start > self.timeout:
                    raise TimeoutError(f"Store lock timeout: {self.path}")
                time.sleep(0.05)
    def __exit__(self, exc_type, exc, tb):
        if self.acquired:
            try: self.path.unlink()
            except FileNotFoundError: pass
