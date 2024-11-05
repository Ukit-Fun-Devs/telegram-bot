import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from routers.authorize import authorize_router
from routers.base import base_router
from routers.menu import menu_router
from routers.reminders import check_reminders, reminders_router
from routers.schedule import schedule_router
from routers.settings import settings_router
from routers.start import start_router
from utils import env
from utils.services.database import init_database


async def main() -> None:
    dp = Dispatcher()
    dp.include_routers(
        start_router,
        menu_router,
        authorize_router,
        schedule_router,
        base_router,
        reminders_router,
        settings_router
    )

    bot = Bot(
        token=env.TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.MARKDOWN_V2
        )
    )

    await init_database()
    asyncio.create_task(check_reminders(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
