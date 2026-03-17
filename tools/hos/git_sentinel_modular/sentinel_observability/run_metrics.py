import time
from dataclasses import dataclass

@dataclass
class RunMetrics:
    start_time: float = None
    end_time: float = None
    files_scanned: int = 0
    errors: int = 0

    def start(self):
        self.start_time = time.time()

    def finish(self):
        self.end_time = time.time()

    @property
    def duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
