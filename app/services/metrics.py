import threading


class Counter:
    """线程安全的计数器（单进程内存版）。"""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._calls = 0

    def incr(self) -> None:
        with self._lock:
            self._calls += 1

    @property
    def calls(self) -> int:
        with self._lock:
            return self._calls


counter = Counter()
