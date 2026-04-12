from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass

from app.core.errors import CircuitOpenError


@dataclass(slots=True)
class CircuitBreakerConfig:
    window_sec: int
    failure_rate_threshold: float
    min_requests: int
    open_sec: int


class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig) -> None:
        self.config = config
        self._events: deque[tuple[float, bool]] = deque()
        self._opened_until = 0.0

    def before_call(self) -> None:
        if time.time() < self._opened_until:
            raise CircuitOpenError("circuit breaker is open")

    def record_success(self) -> None:
        self._record(True)

    def record_failure(self) -> None:
        self._record(False)

    def _record(self, success: bool) -> None:
        now = time.time()
        self._events.append((now, success))
        self._trim(now)
        if self._should_open():
            self._opened_until = now + self.config.open_sec

    def _trim(self, now: float) -> None:
        while self._events and now - self._events[0][0] > self.config.window_sec:
            self._events.popleft()

    def _should_open(self) -> bool:
        if len(self._events) < self.config.min_requests:
            return False
        failures = sum(1 for _, success in self._events if not success)
        rate = failures / len(self._events)
        return rate > self.config.failure_rate_threshold
