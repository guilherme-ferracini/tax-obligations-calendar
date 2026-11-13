"""Business-day calendar: Brazilian national holidays, bank holidays and due-date rolling."""

from __future__ import annotations

from datetime import date, timedelta
from functools import lru_cache
from typing import Iterable, Set

FIXED_HOLIDAYS = [(1, 1), (4, 21), (5, 1), (9, 7), (10, 12), (11, 2), (11, 15), (11, 20), (12, 25)]


def easter(year: int) -> date:
    """Anonymous Gregorian algorithm (Meeus/Jones/Butcher)."""
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = (h + l - 7 * m + 114) % 31 + 1
    return date(year, month, day)


@lru_cache(maxsize=None)
def national_holidays(year: int) -> frozenset:
    e = easter(year)
    mobile = {
        e - timedelta(days=48),  # Carnival Monday (no banking)
        e - timedelta(days=47),  # Carnival Tuesday (no banking)
        e - timedelta(days=2),   # Good Friday
    }
    return frozenset({date(year, m, d) for m, d in FIXED_HOLIDAYS} | mobile)


class BusinessCalendar:
    def __init__(self, extra_holidays: Iterable[date] = ()) -> None:
        self.extra: Set[date] = set(extra_holidays)   # state / municipal holidays

    def is_business_day(self, d: date) -> bool:
        return d.weekday() < 5 and d not in national_holidays(d.year) and d not in self.extra

    def roll(self, d: date, direction: str) -> date:
        """'next' postpones to the next business day, 'previous' anticipates, 'none' keeps the date."""
        if direction == "none":
            return d
        step = timedelta(days=1 if direction == "next" else -1)
        while not self.is_business_day(d):
            d += step
        return d

    def last_business_day(self, year: int, month: int) -> date:
        nxt = date(year + (month == 12), month % 12 + 1, 1)
        return self.roll(nxt - timedelta(days=1), "previous")
