from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.database.repo import checkins as checkins_repo
from bot.database.repo import referrals as referrals_repo
from bot.database.repo import users as users_repo
from bot.filters.admin import IsAdmin
from bot.keyboards.admin import admin_back_keyboard, admin_user_view_keyboard, admin_users_keyboard
from bot.states.admin_states import AdminUserSearchStates

router = Router(name="admin_users")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


def _user_card_text(user: User, checkins_total: int, referred_count: int) -> str:
    premium = "нет"
    if user.premium_until:
        marker = "✅" if user.has_active_premium else "истекла"
        premium = f"{marker} до {user.premium_until.strftime('%Y-%m-%d %H:%M')}"
    return (
        f"👤 {user.first_name or ''} (@{user.username or '—'})\n"
        f"ID: {user.tg_id}\n"
        f"Язык: {user.lang}\n"
        f"Регистрация: {user.created_at.strftime('%Y-%m-%d')}\n"
        f"Забанен: {'да' if user.is_banned else 'нет'}\n"
        f"Подписка: {premium}\n"
        f"Чек-инов: {checkins_total}\n"
        f"Приглашено (успешно): {referred_count}\n"
        f"Реферальный код: {user.referral_code}"
    )


@router.callback_query(F.data == "admin:users")
async def cb_admin_users(callback: CallbackQuery) -> None:
    await callback.message.edit_text("👥 Пользователи", reply_markup=admin_users_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin:u:search")
async def cb_admin_user_search(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminUserSearchStates.waiting_query)
    await callback.message.edit_text(
        "Отправь Telegram ID или @username пользователя для поиска.",
        reply_markup=admin_back_keyboard("admin:users"),
    )
    await callback.answer()


@router.message(AdminUserSearchStates.waiting_query)
async def msg_admin_user_search(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
    query = message.text or ""
    results = await users_repo.search(session, query, limit=5)
    if not results:
        await message.answer("Никого не нашёл 🤷", reply_markup=admin_back_keyboard("admin:users"))
        return

    for found in results:
        checkins_total = await checkins_repo.count_for_user(session, found.id)
        referred_count = await referrals_repo.count_rewarded_by_referrer(session, found.id)
        await message.answer(
            _user_card_text(found, checkins_total, referred_count), reply_markup=admin_user_view_keyboard(found)
        )


@router.callback_query(F.data.startswith("admin:u:grant:"))
async def cb_admin_grant_premium(callback: CallbackQuery, session: AsyncSession) -> None:
    _, _, _, user_id_str, days_str = callback.data.split(":")
    target = await users_repo.get_by_id(session, int(user_id_str))
    if target is None:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    new_until = await users_repo.grant_premium_days(session, target, int(days_str))
    checkins_total = await checkins_repo.count_for_user(session, target.id)
    referred_count = await referrals_repo.count_rewarded_by_referrer(session, target.id)
    await callback.message.edit_text(
        _user_card_text(target, checkins_total, referred_count), reply_markup=admin_user_view_keyboard(target)
    )
    await callback.answer(f"Выдано! Подписка до {new_until.strftime('%Y-%m-%d')}", show_alert=True)


@router.callback_query(F.data.startswith("admin:u:ban_toggle:"))
async def cb_admin_ban_toggle(callback: CallbackQuery, session: AsyncSession) -> None:
    user_id = int(callback.data.split(":")[-1])
    target = await users_repo.get_by_id(session, user_id)
    if target is None:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    await users_repo.set_banned(session, target, not target.is_banned)
    checkins_total = await checkins_repo.count_for_user(session, target.id)
    referred_count = await referrals_repo.count_rewarded_by_referrer(session, target.id)
    await callback.message.edit_text(
        _user_card_text(target, checkins_total, referred_count), reply_markup=admin_user_view_keyboard(target)
    )
    await callback.answer()
