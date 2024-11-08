from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

DELETE_MESSAGE_MARKUP: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="🗑️ Удалить сообщение",
            callback_data="delete-message"
        )]
    ]
)
