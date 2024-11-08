from datetime import datetime

__all__ = (
    "now",
)


class CurrentDate:

    def __call__(self, *args, **kwargs) -> datetime:
        return datetime.now()


now = CurrentDate()
