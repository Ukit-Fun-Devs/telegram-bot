from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from utils.filters.is_registered import IsNotRegistered
from utils.keybords import AUTHORIZE_KEYBOARD

start_router = Router()


@start_router.message(CommandStart(), IsNotRegistered())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привет 👋\\! Это бот\\- мульти тул для УКИТ\\. "
        f"Поддержку бота осуществляет @imkristaa",
        reply_markup=AUTHORIZE_KEYBOARD
    )
