import re
from datetime import datetime

from utils.basic import DISCIPLINE_ICONS, COUPLE_COUNT_ICONS
from utils.basic.time import now
from utils.services.parser.models.enums import Hull, DisciplineType
from utils.services.parser.models.typed_dict import CoupleType

DISCIPLINE_TYPE_ICONS = {
    DisciplineType.LECTURE: "📖",
    DisciplineType.PRACTICE: "🛠️",
    DisciplineType.LABORATORY: "🧬",
}


class Couple:
    PATTERN = re.compile(r"(?P<type>лек|пр\.|лаб) (?P<text>[А-Яа-я\s\d]+)(?:, п/г \d)?")

    def __init__(self, data: dict[str, str]) -> None:
        self.raw = data

        hull, classroom = tuple(data["аудитория"].split("-"))
        self.full_classroom: str = data["аудитория"]
        self.classroom: int = int(''.join(filter(lambda x: x.isdigit(), classroom)))  # type: ignore
        self.hull: Hull = Hull.from_value(int(hull))

        self.number: int = int(data["номерЗанятия"])

        self.lecturer: str = (
            data["преподаватель"]
            .replace("преп. СПО", "")
        )
        self.short_lecturer: str = (
            data["фиоПреподавателя"]
            .replace("преп. СПО", "")
        )

        searcher = self.PATTERN.search(data["дисциплина"])
        self.discipline: str = searcher.group("text")
        self.type: DisciplineType = DisciplineType(searcher.group("type"))

        self.start: datetime = datetime.fromisoformat(data["датаНачала"])
        self.end: datetime = datetime.fromisoformat(data["датаОкончания"])

    def deserialize(self) -> CoupleType:
        return {
            "number": self.number,
            "is_launch": self.number == 3,
            "launch_type": self.get_launch_english(),
            "couple_type": self.type.get_english(),
            "is_active": self.start <= now() <= self.end,

            "name": self.discipline,
            "description": "",
            "teacher": self.short_lecturer,
            "audience": str(self.classroom),

            "start": self.start.strftime("%H:%M"),
            "end": self.end.strftime("%H:%M")
        }

    def get_launch_formatted(self) -> str:
        if self.hull == Hull.NEW:
            return "13:20 \\- 13:40"
        elif self.hull == Hull.OLD and self.classroom // 10 in [1, 2]:
            return "11:50 \\- 12:10"
        elif self.hull == Hull.OLD and self.classroom // 10 in [3, 4]:
            return "12:30 \\- 12:50"

    def get_launch_english(self) -> str:
        if self.hull == Hull.NEW:
            return "end"
        elif self.hull == Hull.OLD and self.classroom // 10 in [1, 2]:
            return "start"
        elif self.hull == Hull.OLD and self.classroom // 10 in [3, 4]:
            return "middle"

    def calculate_launch(self) -> tuple[datetime, datetime]:
        if self.hull == Hull.NEW:
            return self._convert_time_range_to_tuple("13:20", "13:40")
        elif self.hull == Hull.OLD and self.classroom // 10 in [1, 2]:
            return self._convert_time_range_to_tuple("11:50", "12:10")
        elif self.hull == Hull.OLD and self.classroom // 10 in [3, 4]:
            return self._convert_time_range_to_tuple("12:30", "12:50")

    @classmethod
    def _convert_time_range_to_tuple(cls, _st: str, _et) -> tuple[datetime, datetime]:
        today = datetime.today().date()
        start_time = datetime.combine(today, datetime.strptime(_st, "%H:%M").time()).replace(tzinfo=cls.ZONE)
        end_time = datetime.combine(today, datetime.strptime(_et, "%H:%M").time()).replace(tzinfo=cls.ZONE)

        return start_time, end_time

    def generate_str(self) -> str:
        text_couple = (
            f"{COUPLE_COUNT_ICONS[self.number]} "
            f"*{self.start.strftime("%H:%M")} \\- {self.end.strftime("%H:%M")}*\n"
            f"{DISCIPLINE_ICONS.get(self.discipline, "💼")} *{self.discipline}* \\(_{self.type.get_name()}_\\)\n"
            f"🧑‍🏫 *{self.lecturer}*\n"
            f"🏢 *{self.hull.get_name()}* корпус {DISCIPLINE_TYPE_ICONS[self.type]} Аудитория *{self.classroom}*"
        )
        if self.number == 3 and (launch_time := self.get_launch_formatted()):
            text_couple += f"\n☕ Обед *{launch_time}*"

        return text_couple

    def __repr__(self) -> str:
        return (
            f"Couple<"
            f"number={self.number}, "
            f"discipline={self.discipline}, "
            f"classroom={self.full_classroom}, "
            f"start={self.start.strftime("%H:%M")}, "
            f"end={self.end.strftime("%H:%M")}"
            f">"
        )
