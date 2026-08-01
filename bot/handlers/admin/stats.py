from datetime import date, datetime, timedelta

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repo import analytics as analytics_repo
from bot.database.repo import checkins as checkins_repo
from bot.database.repo import guides as guides_repo
from bot.database.repo import payments as payments_repo
from bot.database.repo import referrals as referrals_repo
from bot.database.repo import users as users_repo
from bot.filters.admin import IsAdmin
from bot.keyboards.admin import admin_back_keyboard

router = Router(name="admin_stats")
router.callback_query.filter(IsAdmin())


@router.callback_query(F.data == "admin:stats")
async def cb_admin_stats(callback: CallbackQuery, session: AsyncSession) -> None:
    today = date.today()
    total_users = await users_repo.count_all(session)
    premium_users = await users_repo.count_premium_active(session)
    banned_users = await users_repo.count_banned(session)
    new_today = await users_repo.new_users_since(session, datetime.combine(today, datetime.min.time()))

    dau = await analytics_repo.dau(session, today)
    wau = await analytics_repo.wau(session, today)
    mau = await analytics_repo.mau(session, today)

    checkins_today = await checkins_repo.count_for_date(session, today)
    checkins_7d = await checkins_repo.count_since(session, today - timedelta(days=6))

    revenue = await payments_repo.total_stars_revenue(session)
    payments_count = await payments_repo.count(session)
    referrals_rewarded = await referrals_repo.count_total_rewarded(session)

    top_guides = await guides_repo.top_viewed(session, limit=5)
    top_guides_text = "\n".join(f"  • {g.title} — {g.views} 👁" for g in top_guides) or "  —"

    text = (
        "📊 Аналитика\n\n"
        f"👤 Пользователи: {total_users} (забанено: {banned_users})\n"
        f"🆕 Новых сегодня: {new_today}\n"
        f"⭐ Активная подписка: {premium_users}\n\n"
        f"📈 DAU: {dau} · WAU: {wau} · MAU: {mau}\n\n"
        f"✅ Чек-инов сегодня: {checkins_today}\n"
        f"✅ Чек-инов за 7 дней: {checkins_7d}\n\n"
        f"💰 Доход: {revenue} ⭐ ({payments_count} платежей)\n"
        f"👥 Награждено рефералов: {referrals_rewarded}\n\n"
        f"🏆 Топ материалов по просмотрам:\n{top_guides_text}"
    )
    await callback.message.edit_text(text, reply_markup=admin_back_keyboard())
    await callback.answer()
