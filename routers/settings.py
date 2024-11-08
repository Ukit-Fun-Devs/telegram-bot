from __future__ import annotations

import ast
from random import choice
from typing import Optional, TYPE_CHECKING

from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, InputMediaPhoto

from utils.basic import GROUP_KAB
from utils.filters.is_registered import IsRegistered
from utils.keybords import DELETE_MESSAGE_MARKUP
from utils.services.database.handlers import UserTools
from utils.services.draw import DrawService
from utils.services.draw.models import Design
from utils.services.parser import MgutmTools
from utils.states import GroupAddState

if TYPE_CHECKING:
    from aiogram.types import Message

settings_router = Router()

HEARTS = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💗", "💓", "💕", "💞", "💝"]


class ChangeGroupCallback(CallbackData, prefix="callback-data-change-group"):
    group_id: int


class ChangeThemeCallback(CallbackData, prefix="callback-data-change-theme"):
    theme_id: str


@settings_router.callback_query(F.data == "clear-all-saved-groups", IsRegistered())
async def clear_all_saved_groups_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "✅ \\| Список сохраненных групп был отчищен\\!",
        reply_markup=DELETE_MESSAGE_MARKUP
    )
    await UserTools.clean_saved_groups(tg_id=callback.from_user.id)


@settings_router.callback_query(F.data == "add-group-start", IsRegistered())
async def add_group_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(GroupAddState.group_id)

    await callback.message.edit_text(
        "📤 \\| Отправь ссылку на группy\\!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📚 Туториал", callback_data="tutorial")]
            ]
        )
    )


@settings_router.message(GroupAddState.group_id, IsRegistered())
async def get_group_id_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    matcher = GROUP_KAB.match(message.text)

    group_id: Optional[int] = None
    if not ((group_id := int(matcher.group(1))) if matcher else False):
        await message.answer(
            "🚫 \\| Указала неверная ссылка\\!",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="💔 Пройти туториал еще раз ", callback_data="tutorial")],
                    [InlineKeyboardButton(text="🙂 Попробовать еще раз", callback_data="add-group-start")]
                ]
            )
        )
        return

    user = await UserTools.get(message.chat.id)
    saved_groups = ast.literal_eval(user.saved_groups)
    if len(saved_groups) >= 5:
        await message.answer(
            "💔 \\| Максимальное число добавленных групп достигнуто\\!"
        )
        return

    if group_id in saved_groups:
        await message.answer(
            "💔 \\| Данная группа уже находится в твоем списке\\!"
        )
        return
    if group_id == user.group_id:
        await message.answer(
            "💔 \\| Вы уже находитесь в этой группе\\!"
        )
        return

    await UserTools.update_groups(message.chat.id, [group_id])
    await message.answer(
        "✅ \\| Группа успешно добавлена\\, теперь ее можно сменить в настройках\\!",
        reply_markup=DELETE_MESSAGE_MARKUP
    )


@settings_router.callback_query(ChangeGroupCallback.filter(F.group_id), IsRegistered())
async def change_group_callback_handler(callback: CallbackQuery, callback_data: ChangeGroupCallback) -> None:
    user = await UserTools.get(callback.message.chat.id)
    await UserTools.update_groups(
        callback.message.chat.id,
        groups=[user.group_id],
        remove_groups=[callback_data.group_id],
        set_group=callback_data.group_id
    )

    await callback.message.edit_text(
        "✅ \\| Группа успешно изменена\\, сменить обратно можно в настройках\\!",
        reply_markup=DELETE_MESSAGE_MARKUP
    )


@settings_router.callback_query(F.data == "change-group", IsRegistered())
async def change_group_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "💫 \\| Выбери группу\\/добавь ее\\:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(
                text=f"{choice(HEARTS)} "
                     f"{info.text_id if (info := (await MgutmTools.get_info(group_id))) else group_id}",
                callback_data=ChangeGroupCallback(group_id=group_id).pack()
            )] for group_id in await UserTools.get_groups(callback.from_user.id)] + [[
                InlineKeyboardButton(text="💖 Добавить группу", callback_data="add-group-start"),
                InlineKeyboardButton(text="✨ Очистить группы", callback_data="clear-all-saved-groups")
            ]]
        )
    )


@settings_router.callback_query(F.data == "change-design", IsRegistered())
async def change_design_handler(callback: CallbackQuery) -> None:
    user = await UserTools.get(callback.from_user.id)
    await callback.message.edit_text(
        "🔧 \\| Выбери дизайн для бота\\:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text=design.name + (" | ⭐" if user.theme == design.key else ""),
                    callback_data=ChangeThemeCallback(theme_id=design.key).pack()
                )]
                for design in await DrawService.get_designs()
            ]
        )
    )


@settings_router.callback_query(ChangeThemeCallback.filter(F.theme_id), IsRegistered())
async def selected_design_handler(callback: CallbackQuery, callback_data: ChangeThemeCallback) -> None:
    design: Design = list(filter(lambda x: x.key == callback_data.theme_id, await DrawService.get_designs()))[0]
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=design.preview,
            caption=f"✅ \\| Дизайн успешно изменен\\! Пример выше\\."
        ),
        reply_markup=DELETE_MESSAGE_MARKUP
    )

    await UserTools.set_theme(tg_id=callback.from_user.id, theme_key=design.key)
