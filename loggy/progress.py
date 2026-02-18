"""Progress and timing helpers for pyloggy."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Callable, Dict, Optional


Clock = Callable[[], float]


@dataclass(frozen=True)
class ProgressSnapshot:
    current: int
    total: int
    remaining: int
    percent: float
    elapsed: float
    rate: float
    eta: Optional[float]


class Stopwatch:
    """Simple monotonic stopwatch with context-manager support."""

    def __init__(self, auto_start: bool = True, clock: Clock = time.monotonic):
        self._clock = clock
        self._started_at: Optional[float] = None
        self._accumulated = 0.0
        if auto_start:
            self.start()

    @property
    def running(self) -> bool:
        return self._started_at is not None

    def start(self) -> None:
        if not self.running:
            self._started_at = self._clock()

    def stop(self) -> float:
        if self.running and self._started_at is not None:
            self._accumulated += self._clock() - self._started_at
            self._started_at = None
        return self.elapsed

    def reset(self, auto_start: bool = False) -> None:
        self._started_at = None
        self._accumulated = 0.0
        if auto_start:
            self.start()

    @property
    def elapsed(self) -> float:
        if self.running and self._started_at is not None:
            return self._accumulated + (self._clock() - self._started_at)
        return self._accumulated

    def lap(self) -> float:
        return self.elapsed

    @staticmethod
    def format_seconds(seconds: float) -> str:
        if seconds < 1:
            return f"{seconds * 1000:.0f}ms"
        minutes, secs = divmod(seconds, 60)
        hours, minutes = divmod(int(minutes), 60)
        if hours:
            return f"{hours}h {minutes}m {secs:.1f}s"
        if minutes:
            return f"{minutes}m {secs:.1f}s"
        return f"{secs:.2f}s"

    def __enter__(self) -> "Stopwatch":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop()


class ProgressTracker:
    """Track progress, throughput, and ETA for known totals."""

    def __init__(self, total: int, current: int = 0, clock: Clock = time.monotonic):
        if total <= 0:
            raise ValueError("total must be > 0")
        if current < 0 or current > total:
            raise ValueError("current must be within [0, total]")

        self.total = total
        self.current = current
        self._timer = Stopwatch(auto_start=True, clock=clock)

    @property
    def percent(self) -> float:
        return (self.current / self.total) * 100.0

    @property
    def complete(self) -> bool:
        return self.current >= self.total

    def advance(self, amount: int = 1) -> int:
        if amount < 0:
            raise ValueError("amount must be >= 0")
        self.current = min(self.total, self.current + amount)
        return self.current

    def set(self, value: int) -> int:
        if value < 0 or value > self.total:
            raise ValueError("value must be within [0, total]")
        self.current = value
        return self.current

    def snapshot(self) -> ProgressSnapshot:
        elapsed = self._timer.elapsed
        remaining = self.total - self.current
        rate = self.current / elapsed if elapsed > 0 else 0.0
        eta = (remaining / rate) if rate > 0 else None
        return ProgressSnapshot(
            current=self.current,
            total=self.total,
            remaining=remaining,
            percent=self.percent,
            elapsed=elapsed,
            rate=rate,
            eta=eta,
        )

    def render(self, width: int = 24, fill: str = "#", empty: str = "-") -> str:
        width = max(1, width)
        filled = min(width, math.floor((self.current / self.total) * width))
        bar = f"{fill * filled}{empty * (width - filled)}"
        snap = self.snapshot()
        eta_text = "--" if snap.eta is None else Stopwatch.format_seconds(snap.eta)
        return (
            f"[{bar}] {self.current}/{self.total} "
            f"({snap.percent:.1f}%) elapsed={Stopwatch.format_seconds(snap.elapsed)} eta={eta_text}"
        )


def time_call(fn: Callable[[], object], clock: Clock = time.monotonic) -> Dict[str, object]:
    """Execute a callable and return result + elapsed seconds."""
    timer = Stopwatch(auto_start=True, clock=clock)
    result = fn()
    return {"result": result, "elapsed": timer.stop()}


__all__ = ["ProgressSnapshot", "ProgressTracker", "Stopwatch", "time_call"]
