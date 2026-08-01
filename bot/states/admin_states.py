from aiogram.fsm.state import State, StatesGroup


class AdminGuideStates(StatesGroup):
    waiting_file = State()
    waiting_title = State()
    waiting_description = State()
    waiting_category = State()
    waiting_premium_flag = State()


class AdminPlanStates(StatesGroup):
    waiting_title = State()
    waiting_days = State()
    waiting_price = State()


class AdminBroadcastStates(StatesGroup):
    waiting_text = State()
    waiting_confirm = State()


class AdminUserSearchStates(StatesGroup):
    waiting_query = State()
