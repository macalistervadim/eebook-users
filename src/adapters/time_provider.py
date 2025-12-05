import datetime

from src.adapters.abc_classes import ABCTimeProvider


class UtcTimeProvider(ABCTimeProvider):
    def now(self) -> datetime.datetime:
        return datetime.datetime.now(datetime.UTC)
