from aiogram.fsm.state import State, StatesGroup


class CheckinStates(StatesGroup):
    waiting_note = State()
