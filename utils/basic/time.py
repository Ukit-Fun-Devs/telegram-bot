from datetime import datetime
import pytz


__all__ = (
    "now",
)


class CurrentDate:
    ZONE = pytz.timezone('Europe/Moscow')

    def __call__(self, *args, **kwargs) -> datetime:
        return datetime.now(self.ZONE)


now = CurrentDate()
