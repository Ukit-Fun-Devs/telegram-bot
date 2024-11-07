from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram.filters import Filter
from aiogram.types import CallbackQuery
from sqlalchemy import select

from utils.services.database import async_session
from utils.services.database.models import User

if TYPE_CHECKING:
    from aiogram.types import Message

__all__ = (
    "IsRegistered",
    "IsNotRegistered",
    "check_registered",
)


async def check_registered(message: Message | CallbackQuery) -> bool:
    if isinstance(message, CallbackQuery):
        message = message.message

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(User).where(User.tg_id == message.chat.id)  # type: ignore
            )
            user = result.scalar_one_or_none()

    return user is not None


class IsRegistered(Filter):
    key = 'is_registered'

    async def __call__(self, message: Message | CallbackQuery) -> bool:
        return await check_registered(message)


class IsNotRegistered(Filter):
    key = 'is_not_registered'

    async def __call__(self, message: Message | CallbackQuery) -> bool:
        return not (await check_registered(message))
