from enum import Enum


class DisciplineType(Enum):
    PRACTICE: str = "пр."
    LECTURE: str = "лек"
    LABORATORY: str = "лаб"

    def get_name(self) -> str:
        match self.value:
            case "пр.":
                return "Практика"
            case "лек":
                return "Лекция"
            case "лаб":
                return "Лабораторная"
            case _:
                return "Unknown"

    def get_english(self) -> str:
        match self.value:
            case "пр.":
                return "practice"
            case "лек":
                return "lecture"
            case "лаб":
                return "laboratory"
            case _:
                return "lecture"
