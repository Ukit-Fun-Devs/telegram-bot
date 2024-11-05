from typing import TypedDict


class CoupleType(TypedDict):
    number: int
    is_launch: bool
    launch_type: str
    couple_type: str
    is_active: bool

    name: str
    description: str
    teacher: str
    audience: str

    start: str
    end: str


class DayType(TypedDict):
    is_today: bool
    number: str
    type: str
    month: str
    couples: list[CoupleType]
