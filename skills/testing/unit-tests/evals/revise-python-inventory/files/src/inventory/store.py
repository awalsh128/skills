"""Stock levels with time-limited reservations."""
import itertools
import time
from typing import Callable


class OutOfStock(Exception):
    pass


class UnknownReservation(Exception):
    pass


class Inventory:
    def __init__(self, hold_seconds: float = 600, clock: Callable[[], float] = time.monotonic):
        self._items: dict[str, int] = {}
        self._holds: dict[int, tuple[str, int, float]] = {}
        self._ids = itertools.count(1)
        self._hold_seconds = hold_seconds
        self._clock = clock
        self._log: list[str] = []

    def add(self, sku: str, qty: int) -> None:
        if qty <= 0:
            raise ValueError("qty must be positive")
        self._items[sku] = self._items.get(sku, 0) + qty
        self._record(f"add {sku} {qty}")

    def available(self, sku: str) -> int:
        self._expire_holds()
        held = sum(q for s, q, _ in self._holds.values() if s == sku)
        return self._items.get(sku, 0) - held

    def reserve(self, sku: str, qty: int) -> int:
        if qty > self.available(sku):
            raise OutOfStock(sku)
        hold_id = next(self._ids)
        self._holds[hold_id] = (sku, qty, self._clock() + self._hold_seconds)
        self._record(f"reserve {sku} {qty}")
        return hold_id

    def release(self, hold_id: int) -> None:
        if self._holds.pop(hold_id, None) is None:
            raise UnknownReservation(hold_id)
        self._record(f"release {hold_id}")

    def commit(self, hold_id: int) -> None:
        self._expire_holds()
        hold = self._holds.pop(hold_id, None)
        if hold is None:
            raise UnknownReservation(hold_id)
        sku, qty, _ = hold
        self._items[sku] -= qty
        self._record(f"commit {hold_id}")

    def _expire_holds(self) -> None:
        now = self._clock()
        for hold_id in [h for h, (_, _, until) in self._holds.items() if until <= now]:
            del self._holds[hold_id]

    def _record(self, entry: str) -> None:
        self._log.append(entry)
