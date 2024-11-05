from __future__ import annotations

from enum import Enum


class Hull(Enum):
    NEW: int = 12
    OLD: int = 11
    UNKNOWN: int = 0

    @classmethod
    def from_value(cls, value: int) -> Hull:
        return cls(value) if 11 <= value <= 12 else cls.UNKNOWN

    def get_name(self) -> str:
        match self.value:
            case 11:
                return "Старый"
            case 12:
                return "Новый"
            case _:
                return "Unknown"
