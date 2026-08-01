import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from bot.config import settings
from bot.database.engine import async_session_maker
from bot.database.repo import checkins as checkins_repo
from bot.database.repo import users as users_repo

logger = logging.getLogger(__name__)

_REMINDER_TEXT = {
    "ru": "⏰ Не забудь оценить свою продуктивность сегодня! Загляни в раздел «✅ Чек-ин».",
    "en": '⏰ Don\'t forget to log today\'s productivity! Check the "✅ Check-in" section.',
}

_EXPIRY_TEXT = {
    "ru": "⏳ Твоя подписка истекает менее чем через 24 часа. Продли её в разделе «⭐ Подписка», "
    "чтобы не потерять доступ к премиум-материалам.",
    "en": '⏳ Your subscription expires in less than 24 hours. Renew it in the "⭐ Subscription" '
    "section to keep premium access.",
}


def _tz() -> ZoneInfo:
    return ZoneInfo(settings.timezone)


async def _send_daily_reminders(bot: Bot) -> None:
    now = datetime.now(_tz())
    hh_mm = now.strftime("%H:%M")
    today = now.date()
    async with async_session_maker() as session:
        users = await users_repo.list_due_reminders(session, hh_mm)
        for user in users:
            checkin = await checkins_repo.get_for_date(session, user.id, today)
            if checkin is not None:
                continue
            try:
                await bot.send_message(user.tg_id, _REMINDER_TEXT.get(user.lang, _REMINDER_TEXT["ru"]))
            except Exception:
                logger.warning("Failed to send reminder to %s", user.tg_id, exc_info=True)


async def _notify_premium_expiring(bot: Bot) -> None:
    async with async_session_maker() as session:
        users = await users_repo.list_premium_expiring_within(session, hours=24)
        for user in users:
            if not user.notifications_on:
                continue
            try:
                await bot.send_message(user.tg_id, _EXPIRY_TEXT.get(user.lang, _EXPIRY_TEXT["ru"]))
            except Exception:
                logger.warning("Failed to send expiry notice to %s", user.tg_id, exc_info=True)


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=_tz())
    scheduler.add_job(
        _send_daily_reminders,
        CronTrigger(minute="*"),
        args=[bot],
        id="daily_reminders",
        replace_existing=True,
    )
    scheduler.add_job(
        _notify_premium_expiring,
        CronTrigger(hour=10, minute=0),
        args=[bot],
        id="premium_expiry",
        replace_existing=True,
    )
    return scheduler
