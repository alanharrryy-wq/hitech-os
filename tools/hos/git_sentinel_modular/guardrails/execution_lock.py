import time
from pathlib import Path
from .defaults import runtime_root, DEFAULT_LOCK_TIMEOUT

class ExecutionLock:

    def __init__(self, name="sentinel.lock"):
        self.lock_file = runtime_root() / "locks" / name

    def acquire(self, timeout=DEFAULT_LOCK_TIMEOUT):
        start = time.time()

        while self.lock_file.exists():

            if time.time() - start > timeout:
                raise RuntimeError(
                    f"Execution lock timeout: {self.lock_file}"
                )

            time.sleep(1)

        self.lock_file.write_text(str(time.time()))

    def release(self):
        if self.lock_file.exists():
            self.lock_file.unlink()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()
