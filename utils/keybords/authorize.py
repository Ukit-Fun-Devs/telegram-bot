from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

__all__ = (
    "AUTHORIZE_KEYBOARD",
    "AUTHORIZE",
)

AUTHORIZE: str = "Авторизоваться 🔑"

AUTHORIZE_KEYBOARD: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=AUTHORIZE)]
    ],
    resize_keyboard=True,
    row_width=1,
    input_field_placeholder="Авторизуйся /register",
    is_persistent=True
)
