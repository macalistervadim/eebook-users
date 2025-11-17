import datetime

from src.adapters.interfaces import AbstractClock


class SystemClock(AbstractClock):
    def now(self) -> datetime.datetime:
        return datetime.datetime.now(datetime.UTC)
