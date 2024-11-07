from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from utils.filters.is_registered import check_registered
from utils.keybords import AUTHORIZE_KEYBOARD, MAIN_MENU_KEYBOARD

start_router = Router()


@start_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    if await check_registered(message):
        await message.answer(
            f"Привет eще раз 👋\\, ты уже зарегистрирован ❤️\\! Это бот\\- мульти тул для УКИТ\\. "
            f"Поддержку бота осуществляет @imkristaa\n"
            f"Код полуоткрытый\\, если тебе интересно то вот https://github\\.com/Ukit\\-Fun\\-Devs",
            reply_markup=MAIN_MENU_KEYBOARD
        )
    else:
        await message.answer(
            f"Привет 👋\\! Это бот\\- мульти тул для УКИТ\\. "
            f"Поддержку бота осуществляет @imkristaa\n"
            f"Код полуоткрытый\\, если тебе интересно то вот https://github\\.com/Ukit\\-Fun\\-Devs",
            reply_markup=AUTHORIZE_KEYBOARD
        )
