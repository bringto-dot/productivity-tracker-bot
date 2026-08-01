from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import SubscriptionPlan


async def list_active(session: AsyncSession) -> list[SubscriptionPlan]:
    result = await session.scalars(
        select(SubscriptionPlan)
        .where(SubscriptionPlan.is_active.is_(True))
        .order_by(SubscriptionPlan.position, SubscriptionPlan.id)
    )
    return list(result)


async def list_all(session: AsyncSession) -> list[SubscriptionPlan]:
    result = await session.scalars(
        select(SubscriptionPlan).order_by(SubscriptionPlan.position, SubscriptionPlan.id)
    )
    return list(result)


async def get(session: AsyncSession, plan_id: int) -> SubscriptionPlan | None:
    return await session.get(SubscriptionPlan, plan_id)


async def create(session: AsyncSession, title: str, days: int, stars_price: int) -> SubscriptionPlan:
    plan = SubscriptionPlan(title=title, days=days, stars_price=stars_price)
    session.add(plan)
    await session.commit()
    await session.refresh(plan)
    return plan


async def update(session: AsyncSession, plan: SubscriptionPlan, **fields) -> SubscriptionPlan:
    for key, value in fields.items():
        setattr(plan, key, value)
    await session.commit()
    return plan


async def toggle_active(session: AsyncSession, plan: SubscriptionPlan) -> bool:
    plan.is_active = not plan.is_active
    await session.commit()
    return plan.is_active
