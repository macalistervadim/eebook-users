import datetime

from src.adapters.interfaces import AbstractTimeProvider


class UtcTimeProvider(AbstractTimeProvider):
    def now(self) -> datetime.datetime:
        return datetime.datetime.now(datetime.UTC)
