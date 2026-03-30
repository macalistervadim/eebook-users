import abc
import datetime


class ABCTimeProvider(abc.ABC):
    @abc.abstractmethod
    def now(self) -> datetime.datetime:
        """Возвращает текущее время в UTC."""
        raise NotImplementedError
