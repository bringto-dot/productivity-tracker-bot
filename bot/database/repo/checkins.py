from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import CheckIn


async def get_for_date(session: AsyncSession, user_id: int, day: date) -> CheckIn | None:
    return await session.scalar(select(CheckIn).where(CheckIn.user_id == user_id, CheckIn.date == day))


async def create(session: AsyncSession, user_id: int, day: date, score: int, note: str | None) -> CheckIn:
    checkin = CheckIn(user_id=user_id, date=day, score=score, note=note)
    session.add(checkin)
    await session.commit()
    await session.refresh(checkin)
    return checkin


async def count_for_user(session: AsyncSession, user_id: int) -> int:
    return await session.scalar(select(func.count()).select_from(CheckIn).where(CheckIn.user_id == user_id)) or 0


async def get_dates_desc(session: AsyncSession, user_id: int) -> list[date]:
    result = await session.scalars(
        select(CheckIn.date).where(CheckIn.user_id == user_id).order_by(CheckIn.date.desc())
    )
    return list(result)


async def get_scores_since(session: AsyncSession, user_id: int, since: date) -> list[int]:
    result = await session.scalars(
        select(CheckIn.score).where(CheckIn.user_id == user_id, CheckIn.date >= since)
    )
    return list(result)


async def list_page(session: AsyncSession, user_id: int, offset: int, limit: int) -> list[CheckIn]:
    result = await session.scalars(
        select(CheckIn)
        .where(CheckIn.user_id == user_id)
        .order_by(CheckIn.date.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(result)


async def count_for_date(session: AsyncSession, day: date) -> int:
    return await session.scalar(select(func.count()).select_from(CheckIn).where(CheckIn.date == day)) or 0


async def count_since(session: AsyncSession, since: date) -> int:
    return await session.scalar(select(func.count()).select_from(CheckIn).where(CheckIn.date >= since)) or 0


async def average_score_since(session: AsyncSession, since: date) -> float | None:
    return await session.scalar(select(func.avg(CheckIn.score)).where(CheckIn.date >= since))
