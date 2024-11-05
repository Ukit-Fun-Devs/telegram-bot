from __future__ import annotations

import base64
import json
from datetime import datetime, date

from utils.basic import DAY_TYPES, MONTH_TYPES
from .couple import Couple
from .typed_dict import DayType


class Day:
    def __init__(self, data: list[dict[str, str]], **kwargs) -> None:
        self.raw = kwargs.copy()
        self.raw_couples = data
        couple = data[0]

        self.date: date = datetime.fromisoformat(couple["дата"])
        self.day_of_week_number: int = int(couple["деньНедели"])
        self.day_of_week: str = couple["день_недели"].lower()
        self.group_id: int = int(couple["кодГруппы"])
        self.type: int = int(couple["типНедели"])
        self.couples: list[Couple] = []

        for couple_data in data:
            self.couples.append(Couple(couple_data))

    def deserialize(self) -> DayType:
        return {
            "is_today": self.date.day == date.today().day,
            "number": self.date.strftime("%d"),
            "type": DAY_TYPES[self.day_of_week_number - 1],
            "month": self.date.strftime(f"{MONTH_TYPES[self.date.month - 1]} %Y"),
            "couples": [couple.deserialize() for couple in self.couples]
        }

    def to_base64(self) -> str:
        json_string = json.dumps({
            "data": self.raw_couples,
            **self.raw
        })
        return base64.b64encode(json_string.encode('utf-8')).decode('utf-8')

    @classmethod
    def from_base64(cls, _str: str) -> Day:
        json_string = base64.b64decode(_str.encode('utf-8')).decode('utf-8')
        d = json.loads(json_string)
        return cls(d.pop("data"), **d)
