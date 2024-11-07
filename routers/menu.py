from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.filters.is_registered import IsRegistered
from utils.keybords.main_menu import INFO, SETTINGS, STATISTICS, MAIN_MENU_KEYBOARD
from utils.services.database.handlers import UserTools
from utils.services.database.models import User
from utils.services.parser import MgutmTools

if TYPE_CHECKING:
    from aiogram.types import Message

menu_router = Router()


@menu_router.message(Command("menu"), IsRegistered())
async def menu_handler(message: Message) -> None:
    await message.answer("✅ \\| Клавиатура применена\\!", reply_markup=MAIN_MENU_KEYBOARD)


@menu_router.message(F.text == STATISTICS, IsRegistered())
async def statistics_handler(message: Message) -> None:
    await message.answer("Статистика")


@menu_router.message(F.text == SETTINGS, IsRegistered())
async def settings_handler(message: Message) -> None:
    user: User = await UserTools.get(message.chat.id)
    remind_status_text = "❤️ Выключить напоминания" if user.reminded else "💚 Включить напоминания"

    await message.answer(
        "⚙️ \\| Настройки бота",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=remind_status_text, callback_data="change-remind-status")],
                [InlineKeyboardButton(text="💎 Настроить оформление", callback_data="change-design")],
                [InlineKeyboardButton(text="💫 Сменить группу", callback_data="change-group")]
            ]
        )
    )


@menu_router.message(F.text == INFO, IsRegistered())
async def info_handler(message: Message) -> None:
    user: User = await UserTools.get(message.chat.id)
    if not (info := await MgutmTools.get_info(user.group_id)):
        await message.answer("🚫 \\| Ошибка получения информации о группе")
        return

    await message.answer(
        f"👥 Группа №*{info.text_id}*\n\n"
        f"🏫 Факультет: *{info.faculty}*\n"
        f"🏢 Кафедра: *{info.department}*\n"
        f"📚 Форма: *{info.form}*\n"
        f"🔢 Уровень: *{info.level}*\n"
        f"🗓 Год: *{info.years}*\n"
        f"🎓 Курс: *{info.course}*\n"
        f"👨‍🎓 Учащихся: *{info.students_count}*\n"
        f"💻 Специальность: *{info.special}*\n"
        f"🆔 ID: *{info.text_id}*\n",
        parse_mode="Markdown"
    )
