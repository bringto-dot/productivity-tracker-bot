from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Payment


async def create(
    session: AsyncSession, user_id: int, plan_id: int | None, telegram_charge_id: str, stars_amount: int
) -> Payment:
    payment = Payment(user_id=user_id, plan_id=plan_id, telegram_charge_id=telegram_charge_id, stars_amount=stars_amount)
    session.add(payment)
    await session.commit()
    await session.refresh(payment)
    return payment


async def total_stars_revenue(session: AsyncSession) -> int:
    return await session.scalar(select(func.coalesce(func.sum(Payment.stars_amount), 0))) or 0


async def count(session: AsyncSession) -> int:
    return await session.scalar(select(func.count()).select_from(Payment)) or 0
