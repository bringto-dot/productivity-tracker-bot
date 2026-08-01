import json
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import AnalyticsEvent, UserActivity


async def log_event(session: AsyncSession, user_id: int | None, event_type: str, meta: dict | None = None) -> None:
    session.add(AnalyticsEvent(user_id=user_id, event_type=event_type, meta=json.dumps(meta) if meta else None))
    await session.commit()


async def mark_activity(session: AsyncSession, user_id: int, day: date) -> None:
    stmt = sqlite_insert(UserActivity).values(user_id=user_id, date=day)
    stmt = stmt.on_conflict_do_nothing(index_elements=["user_id", "date"])
    await session.execute(stmt)
    await session.commit()


async def active_count_since(session: AsyncSession, since: date) -> int:
    return await session.scalar(
        select(func.count(func.distinct(UserActivity.user_id))).where(UserActivity.date >= since)
    ) or 0


async def active_count_for(session: AsyncSession, day: date) -> int:
    return await session.scalar(
        select(func.count(func.distinct(UserActivity.user_id))).where(UserActivity.date == day)
    ) or 0


async def count_events_since(session: AsyncSession, event_type: str, since: datetime) -> int:
    return await session.scalar(
        select(func.count())
        .select_from(AnalyticsEvent)
        .where(AnalyticsEvent.event_type == event_type, AnalyticsEvent.created_at >= since)
    ) or 0


async def dau(session: AsyncSession, today: date) -> int:
    return await active_count_for(session, today)


async def wau(session: AsyncSession, today: date) -> int:
    return await active_count_since(session, today - timedelta(days=6))


async def mau(session: AsyncSession, today: date) -> int:
    return await active_count_since(session, today - timedelta(days=29))
