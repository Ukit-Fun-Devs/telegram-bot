from __future__ import annotations

from datetime import datetime, timedelta
from random import choice
from typing import TYPE_CHECKING

from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, Message

from utils.basic import COUPLE_COUNT_ICONS, DAY_ICONS, DAY_TYPES, MONTH_TYPES
from utils.basic.time import now
from utils.filters.is_registered import IsRegistered
from utils.keybords.main_menu import SCHEDULE
from utils.services.database.handlers import UserTools
from utils.services.draw import DrawService
from utils.services.parser import MgutmTools
from utils.services.parser.models import Day

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery

schedule_router = Router()


class ScheduleCallback(CallbackData, prefix="schedule-callback"):
    date: str
    number: int


async def schedule_base(callback: CallbackQuery, number: int, sdate: str = None) -> None:
    user = await UserTools.get(callback.from_user.id)
    if not (days := await MgutmTools.get_schedule(group_id=user.group_id, sdate=sdate)):
        await callback.message.answer("🚫 \\| Расписание не найдено")
        await callback.answer()
        return

    day = list(filter(lambda x: x.day_of_week_number == number, days))[0]
    inline_keyboard = [[]]
    if filtered := list(filter(lambda x: x.day_of_week_number <= number - 1, days)):
        inline_keyboard[0].append(
            InlineKeyboardButton(
                text="⬅️ Предыдущий день",
                callback_data=ScheduleCallback(
                    date=datetime.fromisoformat(day.raw["start_date"]).strftime("%Y-%m-%d"),
                    number=filtered.pop().day_of_week_number
                ).pack()
            )
        )

    if filtered := list(filter(lambda x: x.day_of_week_number >= number + 1, days)):
        inline_keyboard[0].append(
            InlineKeyboardButton(
                text="➡️ Следующий день",
                callback_data=ScheduleCallback(
                    date=datetime.fromisoformat(day.raw["start_date"]).strftime("%Y-%m-%d"),
                    number=filtered.pop(0).day_of_week_number
                ).pack()
            )
        )

    if user.theme != "text" and (media := await DrawService.draw_schedule(day, user)):
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=media,
                caption=f"🗓️ \\| *{day.day_of_week.capitalize()}\\, "
                        f"{day.date.strftime("%d\\.%m\\.%y")}*\n"
                        f"📌 \\| *Изменено: {(_d := datetime.fromisoformat(
                            day.raw["changed_date"]
                        )).strftime(
                            f"{DAY_TYPES[_d.weekday()].capitalize()} "
                            f"{MONTH_TYPES[_d.month - 1].capitalize()} "
                            f"%d "
                            "%H:%M"
                        )}*",
            ),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=inline_keyboard
            ) if inline_keyboard else None
        )
    else:
        await callback.message.edit_text(
            text=f"🗓️ \\| *{days[number].day_of_week.capitalize()}\\, {days[number].date.strftime("%d\\.%m\\.%Y")}*\n\n"
                 + f"\n\n".join([i.generate_str() for i in days[number].couples]),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=inline_keyboard
            ) if inline_keyboard else None
        )
    await callback.answer()


@schedule_router.callback_query(ScheduleCallback.filter(F.date and F.number))
async def schedule_callback_handler(callback: CallbackQuery, callback_data: ScheduleCallback) -> None:
    await schedule_base(callback, callback_data.number, callback_data.date)


async def generate_schedule_markup(days: list[Day]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text=f"{choice(DAY_ICONS)} "
                 f"{i.day_of_week.capitalize()} "
                 f"{i.date.strftime("%d.%m")} "
                 f"{COUPLE_COUNT_ICONS[len(i.couples)]}"
                 + (" (Сегодня)" if i.date.day == now().day else ""),
            callback_data=ScheduleCallback(
                date=datetime.fromisoformat(i.raw["start_date"]).strftime("%Y-%m-%d"),
                number=i.day_of_week_number
            ).pack()
        )] for i in days[:5]] + [[
            InlineKeyboardButton(
                text="⬅️ Назад страница",
                callback_data=SchedulePage(
                    date=(datetime.fromisoformat(days[0].raw["start_date"]) - timedelta(days=7)).strftime("%Y-%m-%d")
                ).pack()
            ),
            InlineKeyboardButton(
                text="➡️ Следующая страница",
                callback_data=SchedulePage(
                    date=datetime.fromisoformat(days[0].raw["next_date"]).strftime("%Y-%m-%d")
                ).pack()
            )
        ]]
    )


class SchedulePage(CallbackData, prefix='schedule-page'):
    date: str


@schedule_router.callback_query(SchedulePage.filter(F.date))
async def page_handler(callback: CallbackQuery, callback_data: SchedulePage) -> None:
    user = await UserTools.get(callback.message.chat.id)
    if not (days := await MgutmTools.get_schedule(group_id=user.group_id, sdate=callback_data.date)):
        await callback.message.answer("🚫 \\| Расписание не найдено")
        await callback.answer()
        return

    await callback.message.edit_text(
        "📅 \\| Выберите день недели:",
        reply_markup=await generate_schedule_markup(days)
    )


@schedule_router.message(F.text == SCHEDULE, IsRegistered())
async def schedule_handler(message: Message) -> None:
    user = await UserTools.get(message.chat.id)
    if not (days := await MgutmTools.get_schedule(group_id=user.group_id)):
        await message.answer("🚫 \\| Расписание не найдено")
        return

    await message.answer(
        "📅 \\| Выберите день недели:",
        reply_markup=await generate_schedule_markup(days)
    )
