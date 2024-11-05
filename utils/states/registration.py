from aiogram.fsm.state import StatesGroup, State


class RegistrationState(StatesGroup):
    group_id = State()
    first_name = State()
    second_name = State()
    third_name = State()
    reminded = State()
