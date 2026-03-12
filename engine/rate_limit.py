# engine/rate_limit.py
from __future__ import annotations
import threading
import time


class RateLimiter:
    """
    Simple global QPS limiter (thread-safe).
    Ensures at most `qps` acquisitions per second (roughly).
    """

    def __init__(self, qps: float):
        if qps <= 0:
            raise ValueError("qps must be > 0")
        self.qps = float(qps)
        self._min_interval = 1.0 / self.qps
        self._lock = threading.Lock()
        self._next_allowed = 0.0  # monotonic time

    def acquire(self) -> None:
        """
        Blocks until we are allowed to proceed.
        """
        while True:
            with self._lock:
                now = time.monotonic()
                if now >= self._next_allowed:
                    self._next_allowed = now + self._min_interval
                    return
                sleep_s = self._next_allowed - now

            # sleep outside lock so other threads can compute too
            if sleep_s > 0:
                time.sleep(sleep_s)
