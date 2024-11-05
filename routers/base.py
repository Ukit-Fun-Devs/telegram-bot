from aiogram import Router, F
from aiogram.types import CallbackQuery

base_router = Router()


@base_router.callback_query(F.data == "delete-message")
async def delete_message(callback: CallbackQuery) -> None:
    await callback.message.delete()
