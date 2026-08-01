from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repo import plans as plans_repo
from bot.filters.admin import IsAdmin
from bot.keyboards.admin import admin_plan_view_keyboard, admin_plans_keyboard
from bot.states.admin_states import AdminPlanStates

router = Router(name="admin_plans")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


def _plan_text(plan) -> str:
    return (
        f"{plan.title}\n\n"
        f"Дней: {plan.days}\n"
        f"Цена: {plan.stars_price} ⭐\n"
        f"Активен: {'да' if plan.is_active else 'нет'}"
    )


@router.callback_query(F.data == "admin:plans")
async def cb_admin_plans(callback: CallbackQuery, session: AsyncSession) -> None:
    plans = await plans_repo.list_all(session)
    text = "⭐ Тарифы подписки" if plans else "Пока нет ни одного тарифа."
    await callback.message.edit_text(text, reply_markup=admin_plans_keyboard(plans))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:p:view:"))
async def cb_admin_plan_view(callback: CallbackQuery, session: AsyncSession) -> None:
    plan_id = int(callback.data.split(":")[-1])
    plan = await plans_repo.get(session, plan_id)
    if plan is None:
        await callback.answer("Не найдено", show_alert=True)
        return
    await callback.message.edit_text(_plan_text(plan), reply_markup=admin_plan_view_keyboard(plan))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:p:toggle:"))
async def cb_admin_plan_toggle(callback: CallbackQuery, session: AsyncSession) -> None:
    plan_id = int(callback.data.split(":")[-1])
    plan = await plans_repo.get(session, plan_id)
    if plan is None:
        await callback.answer("Не найдено", show_alert=True)
        return
    await plans_repo.toggle_active(session, plan)
    await callback.message.edit_text(_plan_text(plan), reply_markup=admin_plan_view_keyboard(plan))
    await callback.answer()


@router.callback_query(F.data == "admin:p:add")
async def cb_admin_plan_add_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminPlanStates.waiting_title)
    await callback.message.edit_text("Название тарифа?")
    await callback.answer()


@router.message(AdminPlanStates.waiting_title)
async def msg_admin_plan_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(AdminPlanStates.waiting_days)
    await message.answer("На сколько дней тариф?")


@router.message(AdminPlanStates.waiting_days)
async def msg_admin_plan_days(message: Message, state: FSMContext) -> None:
    if not message.text or not message.text.strip().isdigit():
        await message.answer("Введи число дней, например 30.")
        return
    await state.update_data(days=int(message.text.strip()))
    await state.set_state(AdminPlanStates.waiting_price)
    await message.answer("Цена в Stars ⭐?")


@router.message(AdminPlanStates.waiting_price)
async def msg_admin_plan_price(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not message.text or not message.text.strip().isdigit():
        await message.answer("Введи число, например 199.")
        return

    data = await state.get_data()
    await state.clear()
    plan = await plans_repo.create(
        session, title=data["title"], days=data["days"], stars_price=int(message.text.strip())
    )
    plans = await plans_repo.list_all(session)
    await message.answer(f"✅ Тариф «{plan.title}» создан.", reply_markup=admin_plans_keyboard(plans))
