from aiogram.fsm.state import StatesGroup, State


class GroupAddState(StatesGroup):
    group_id = State()
    name = State()
