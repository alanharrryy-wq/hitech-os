"""Public surface for sentinel_observability."""

from .drift_detector import detect_drift, hash_directory
from .failure_snapshot import capture_failure
from .run_metrics import RunMetrics
from .structured_logger import log_event

__all__ = ['detect_drift', 'hash_directory', 'capture_failure', 'RunMetrics', 'log_event']
