from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

__all__ = (
    "MAIN_MENU_KEYBOARD",
    "SCHEDULE",
    "STATISTICS",
    "SETTINGS",
    "INFO",
)

SCHEDULE: str = "Расписание 🗓️"
STATISTICS: str = "Статистика посещений 📊"
SETTINGS: str = "Настройки 📝"
INFO: str = "О группе ℹ️"

MAIN_MENU_KEYBOARD: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=SCHEDULE)],  # TODO: KeyboardButton(text=STATISTICS)
        [KeyboardButton(text=INFO)],
        [KeyboardButton(text=SETTINGS)],
    ],
    resize_keyboard=True,
    row_width=2,
    input_field_placeholder="Выбери интересующий тебя пункт в меню"
)
