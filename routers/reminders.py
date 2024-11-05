import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from utils.filters.is_registered import IsRegistered
from utils.services.database.handlers import UserTools, RemindersTools
from utils.services.database.models import User
from utils.services.draw import DrawService
from utils.services.parser import MgutmTools
from utils.services.parser.models import Day, Couple

reminders_router = Router()


@reminders_router.callback_query(F.data == "change-remind-status", IsRegistered())
async def change_remind_status_handler(callback: CallbackQuery) -> None:
    user: User = await UserTools.change_remind(callback.from_user.id)
    match user.reminded:
        case False:
            await callback.message.edit_text(
                "💔 \\| Уведомления успешно выключены",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(
                        text="🗑️ Удалить сообщение",
                        callback_data="delete-message"
                    )]]
                )
            )
        case True:
            await callback.message.edit_text(
                "🎉 \\| Уведомления успешно включены",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(
                        text="🗑️ Удалить сообщение",
                        callback_data="delete-message"
                    )]]
                )
            )


async def disable_event_task(user: User, **kwargs) -> None:
    await asyncio.sleep(60 * 3)
    await RemindersTools.update_reminders(
        tg_id=user.tg_id,
        **kwargs
    )


async def start_event_task(user: User, day: Day, bot: Bot) -> None:
    await bot.send_message(
        chat_id=user.tg_id,
        text="🗓️ \\| *Пары на этот день\\!*\n\n"
             + f"\n\n".join([i.generate_str() for i in day.couples])
    )
    await RemindersTools.update_reminders(
        tg_id=user.tg_id,
        start_event=True
    )


async def couple_start_task(user: User, couple: Couple, bot: Bot) -> None:
    if user.theme != "text" and (media := await DrawService.draw_couple(couple, user)):
        await bot.send_photo(
            chat_id=user.tg_id,
            photo=media,
            caption="✨ \\| *Скоро начнется пара\\!*\n\n"
        )
    else:
        await bot.send_message(
            text="✨ \\| *Скоро начнется пара\\!*\n\n" + couple.generate_str()
        )

    await RemindersTools.update_reminders(
        tg_id=user.tg_id,
        couple_start=True
    )
    asyncio.create_task(disable_event_task(user, couple_start=True))


async def launch_start_task(user: User, bot: Bot) -> None:
    await bot.send_message(
        chat_id=user.tg_id,
        text="☕ \\| *Скоро начнется обед\\!*"
    )
    await RemindersTools.update_reminders(
        tg_id=user.tg_id,
        launch_start=True
    )
    asyncio.create_task(disable_event_task(user, launch_start=True))


async def check_reminders(bot: Bot) -> None:
    truncated = False

    while True:
        if datetime.now().hour == 1 and not truncated:
            try:
                await RemindersTools.truncate_reminders()
            finally:
                truncated = True
        else:
            if datetime.now().hour != 1:
                truncated = False

        for user in await UserTools.get_if_reminded():
            if days := await MgutmTools.get_schedule(user.group_id):
                reminders = await RemindersTools.get_reminders(user.tg_id)
                if not (filtered_days := list(filter(lambda x: x.date.day == datetime.now().day, days))):
                    continue

                day = filtered_days[0]
                if not (
                        couples := list(filter(
                            lambda x: x.start.timestamp() >= (datetime.now() - timedelta(minutes=120)).timestamp(),
                            day.couples
                        ))
                ):
                    continue

                first_couple: Couple = day.couples[0]
                if (
                        not reminders.start_event
                        and datetime.now().hour == first_couple.start.hour
                        and (first_couple.start.minute - 2) <= datetime.now().minute <= first_couple.start.minute
                ):
                    asyncio.create_task(start_event_task(user, day, bot))

                for couple in couples:
                    start_launch, _ = couple.calculate_launch()
                    if (
                            couple.number == 3
                            and not reminders.launch_start
                            and datetime.now().hour == start_launch.hour
                            and (start_launch.minute - 2) <= datetime.now().minute <= start_launch.minute
                    ):
                        asyncio.create_task(launch_start_task(user, bot))

                    if (
                            # couple.start.timestamp() - datetime.now().timestamp() < 60 * 4
                            not reminders.couple_start
                    ):
                        asyncio.create_task(couple_start_task(user, couple, bot))

                    break

        await asyncio.sleep(30)
