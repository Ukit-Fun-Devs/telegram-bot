from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from sqlalchemy import insert

from utils.basic import GROUP_KAB
from utils.filters.is_registered import IsNotRegistered, _check_registered
from utils.keybords import MAIN_MENU_KEYBOARD
from utils.keybords.authorize import AUTHORIZE
from utils.services.database import async_session
from utils.services.database.models import User
from utils.states import RegistrationState

if TYPE_CHECKING:
    from aiogram.types import Message

authorize_router = Router()


@authorize_router.message(F.text == AUTHORIZE, IsNotRegistered())
@authorize_router.callback_query(F.data == "start_registration", IsNotRegistered())
async def authorize_handler(message: Message | CallbackQuery) -> None:
    if isinstance(message, CallbackQuery):
        message = message.message

    text: str = "⚙️ \\| Чтобы настроить бота нажми кнопку ниже\\!"
    reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📚 Туториал", callback_data="tutorial")],
            [InlineKeyboardButton(text="▶️ Начать регистрацию", callback_data="registration-step-1")]
        ]
    )

    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        await message.answer(text, reply_markup=reply_markup)


@authorize_router.callback_query(F.data == "tutorial")
async def tutorial(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "🗓️ \\| Для получения ссылки нужно:\n"
        ">1\\. Зайти на сайт с расписанием",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🌐 Сайт с расписанием", url="https://dec.mgutm.ru")],
                [InlineKeyboardButton(text="▶️ Продолжить", callback_data="tutorial-step-1")]
            ]
        )
    )


@authorize_router.callback_query(F.data == "tutorial-step-1")
async def tutorial_step_1(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.message.answer_photo(
        photo="https://i.ibb.co/phdKgFD/first.png",
        caption=">2\\. Найти панельку \"Группа\"",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🌐 Сайт с расписанием", url="https://dec.mgutm.ru")],
                [InlineKeyboardButton(text="▶️ Продолжить", callback_data="tutorial-step-2")]
            ]
        )
    )


@authorize_router.callback_query(F.data == "tutorial-step-2")
async def tutorial_step_2(callback: CallbackQuery) -> None:
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media="https://i.ibb.co/Nj7LpX9/second.png",
            caption=">3\\. Скопировать ссылку на группу"
        ),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🌐 Сайт с расписанием", url="https://dec.mgutm.ru")],
                [InlineKeyboardButton(text="▶️ Продолжить", callback_data="tutorial-step-3")]
            ]
        )
    )


@authorize_router.callback_query(F.data == "tutorial-step-3")
async def tutorial_step_3(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.message.answer(
        text="✅ \\| Вы прошли туториал по получению ссылки 😄\\!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="▶️ Начать регистрацию!", callback_data="start_registration")]
            ] if not _check_registered(callback.message) else [
                [InlineKeyboardButton(text="💖 Добавить группу", callback_data="add-group-start")]
            ]
        )
    )


@authorize_router.callback_query(F.data == "registration-step-1", IsNotRegistered())
async def registration_step_1(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(RegistrationState.group_id)

    await callback.message.edit_text(
        "📤 \\| Отправь ссылку на свою группy\\!"
    )


@authorize_router.message(RegistrationState.group_id, IsNotRegistered())
async def registration_step_2(message: Message, state: FSMContext) -> None:
    matcher = GROUP_KAB.match(message.text)

    if not (matcher.group(1) if matcher else False):
        await message.answer(
            "🚫 \\| Указала неверная ссылка\\!",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="💔 Пройти туториал еще раз ", callback_data="tutorial")],
                    [InlineKeyboardButton(text="🙂 Попробовать еще раз", callback_data="registration-step-1")]
                ]
            )
        )
        return await state.clear()

    await state.update_data(group_id=int(matcher.group(1)))
    await state.set_state(RegistrationState.first_name)
    await message.answer(
        "📤 \\| Укажи свою фамилию\\!\n"
        ">Эти данные ни на что не влияют, только для удобства оповещений"
    )


@authorize_router.message(RegistrationState.first_name, IsNotRegistered())
async def registration_step_3(message: Message, state: FSMContext) -> None:
    await state.update_data(first_name=message.text)
    await state.set_state(RegistrationState.second_name)
    await message.answer(
        "📤 \\| Укажи свое имя\\!\n"
        ">Эти данные ни на что не влияют, только для удобства оповещений"
    )


@authorize_router.message(RegistrationState.second_name, IsNotRegistered())
async def registration_step_4(message: Message, state: FSMContext) -> None:
    await state.update_data(second_name=message.text)
    await state.set_state(RegistrationState.third_name)
    message = await message.answer(
        "📤 \\| Укажи своe отчество\\!\n"
        ">Эти данные ни на что не влияют, только для удобства оповещений",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⏭️ Пропустить", callback_data="registration-step-5")]
            ]
        )
    )
    await state.update_data(message=message)


@authorize_router.callback_query(F.data == "registration-step-5", IsNotRegistered())
@authorize_router.message(RegistrationState.third_name, IsNotRegistered())
async def registration_step_5(message: Message | CallbackQuery, state: FSMContext) -> None:
    if isinstance(message, CallbackQuery):
        message = message.message
    else:
        await state.update_data(third_name=message.text)

    message = (await state.get_data())["message"]
    await message.bot.delete_message(message.chat.id, message.message_id)
    await message.answer(
        "🔔 \\| Нужно ли вам напоминать об обеде и парах\\?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="👍 Да", callback_data="registration-step-yes"),
                InlineKeyboardButton(text="👎 Нет", callback_data="registration-step-no")
            ]]
        )
    )


@authorize_router.callback_query(F.data == "registration-step-yes", IsNotRegistered())
async def registration_step_yes(message: Message | CallbackQuery, state: FSMContext) -> None:
    await state.update_data(reminded=True)
    await registration_finish(message, state)


@authorize_router.callback_query(F.data == "registration-step-no", IsNotRegistered())
async def registration_step_yes(message: Message | CallbackQuery, state: FSMContext) -> None:
    await state.update_data(reminded=False)
    await registration_finish(message, state)


async def registration_finish(message: Message | CallbackQuery, state: FSMContext) -> None:
    if isinstance(message, CallbackQuery):
        message = message.message

    data = await state.get_data()
    del data["message"]
    data["tg_id"] = message.chat.id

    async with async_session() as session:
        async with session.begin():
            await session.execute(
                insert(User).values(data)
            )

    await message.delete()
    await message.answer(
        "*✅ \\| Вы успешно зарегистрировались\\!*\n\n"
        "*Краткий экскурс по боту:*\n\n"
        "1\\. ⏰ *Напоминания*\n"
        "_Создавайте бесконечные или временные напоминания \\(по какое\\-то число\\)\\. "
        "Можно создавать для себя или группы\\._\n\n"
        "2\\. 📅 *Просмотр расписания*\n"
        "_Здесь вы можете спокойно и удобно посмотреть расписание в нашем любимом тг <3_\n",
        # "3\\. 📊 *Статистика о приходе*\n"
        # "_Автоматически заканчивается при окончании пар\\. Отмечается лично для вас\\._\n"
        # "_Если вы пришли на пары, оповещения о парах/обеде будут работать\\._\n\n",
        reply_markup=MAIN_MENU_KEYBOARD
    )
    await state.clear()
