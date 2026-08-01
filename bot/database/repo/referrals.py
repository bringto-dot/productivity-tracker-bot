from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import ReferralEvent, utcnow


async def get_event_for_referred(session: AsyncSession, referred_id: int) -> ReferralEvent | None:
    return await session.scalar(select(ReferralEvent).where(ReferralEvent.referred_id == referred_id))


async def create_event(session: AsyncSession, referrer_id: int, referred_id: int) -> ReferralEvent:
    event = ReferralEvent(referrer_id=referrer_id, referred_id=referred_id)
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


async def mark_rewarded(session: AsyncSession, event: ReferralEvent, reward_days: int) -> None:
    event.rewarded = True
    event.reward_days = reward_days
    event.rewarded_at = utcnow()
    await session.commit()


async def count_rewarded_by_referrer(session: AsyncSession, referrer_id: int) -> int:
    return await session.scalar(
        select(func.count())
        .select_from(ReferralEvent)
        .where(ReferralEvent.referrer_id == referrer_id, ReferralEvent.rewarded.is_(True))
    ) or 0


async def count_total_referred_by(session: AsyncSession, referrer_id: int) -> int:
    return await session.scalar(
        select(func.count()).select_from(ReferralEvent).where(ReferralEvent.referrer_id == referrer_id)
    ) or 0


async def count_total_rewarded(session: AsyncSession) -> int:
    return await session.scalar(
        select(func.count()).select_from(ReferralEvent).where(ReferralEvent.rewarded.is_(True))
    ) or 0
