import asyncio
from datetime import timedelta

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery

from utils.basic.time import now
from utils.filters.is_registered import IsRegistered
from utils.keybords import DELETE_MESSAGE_MARKUP
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
                reply_markup=DELETE_MESSAGE_MARKUP
            )
        case True:
            await callback.message.edit_text(
                "🎉 \\| Уведомления успешно включены",
                reply_markup=DELETE_MESSAGE_MARKUP
            )


async def disable_event_task(user: User, **kwargs) -> None:
    await asyncio.sleep(60 * 3)
    await RemindersTools.update_reminders(
        tg_id=user.tg_id,
        **kwargs
    )


async def start_event_task(user: User, day: Day, bot: Bot) -> None:
    if user.theme != "text" and (media := await DrawService.draw_schedule(day, user)):
        await bot.send_photo(
            chat_id=user.tg_id,
            photo=media,
            caption=f"🗓️ \\| *Пары на этот день\\!*\n\n"
        )
    else:
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
            chat_id=user.tg_id,
            text="✨ \\| *Скоро начнется пара\\!*\n\n" + couple.generate_str()
        )

    await RemindersTools.update_reminders(
        tg_id=user.tg_id,
        couple_start=True
    )
    asyncio.create_task(disable_event_task(user, couple_start=False))


async def launch_start_task(user: User, bot: Bot) -> None:
    await bot.send_message(
        chat_id=user.tg_id,
        text="☕ \\| *Скоро начнется обед\\!*"
    )
    await RemindersTools.update_reminders(
        tg_id=user.tg_id,
        launch_start=True
    )


async def remind_user(user: User, bot: Bot) -> None:
    if days := await MgutmTools.get_schedule(user.group_id):
        reminders = await RemindersTools.get_reminders(user.tg_id)
        if not (filtered_days := list(filter(lambda x: x.date.day == now().day, days))):
            return

        day: Day = filtered_days[0]
        if not day.couples:
            return

        if (
                not reminders.start_event
                and 0 <= (
                        day.couples[0].start.timestamp()
                        - now().timestamp()
                        - timedelta(minutes=30).total_seconds()
                ) <= 60 * 2
        ):
            asyncio.create_task(start_event_task(user, day, bot))

        if not (
                couples := list(filter(
                    lambda x: x.end.timestamp() >= now().timestamp(),
                    day.couples
                ))
        ):
            return

        couple: Couple = couples[0]
        start_launch, _ = couple.calculate_launch()
        if (
                not reminders.launch_start
                and couple.number == 3
                and 0 <= (start_launch.timestamp() - now().timestamp()) <= 60 * 2
        ):
            asyncio.create_task(launch_start_task(user, bot))

        if (
                not reminders.couple_start
                and 0 <= (couple.start.timestamp() - now().timestamp()) <= 60 * 2
        ):
            asyncio.create_task(couple_start_task(user, couple, bot))


async def check_reminders(bot: Bot) -> None:
    truncated = False

    while True:
        if now().hour == 1 and not truncated:
            try:
                await RemindersTools.truncate_reminders()
            finally:
                truncated = True
        else:
            if now().hour != 1:
                truncated = False

        for user in await UserTools.get_if_reminded():
            asyncio.create_task(remind_user(user, bot))

        await asyncio.sleep(30)
