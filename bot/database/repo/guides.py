from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Guide, GuideCategory


async def create(
    session: AsyncSession,
    title: str,
    description: str | None,
    category: GuideCategory,
    file_id: str,
    is_premium: bool,
    is_local_file: bool = False,
) -> Guide:
    guide = Guide(
        title=title,
        description=description,
        category=category,
        file_id=file_id,
        is_premium=is_premium,
        is_local_file=is_local_file,
    )
    session.add(guide)
    await session.commit()
    await session.refresh(guide)
    return guide


async def get(session: AsyncSession, guide_id: int) -> Guide | None:
    return await session.get(Guide, guide_id)


async def list_by_category(
    session: AsyncSession, category: GuideCategory, only_active: bool = True
) -> list[Guide]:
    stmt = select(Guide).where(Guide.category == category).order_by(Guide.position, Guide.id)
    if only_active:
        stmt = stmt.where(Guide.is_active.is_(True))
    result = await session.scalars(stmt)
    return list(result)


async def list_all(session: AsyncSession) -> list[Guide]:
    result = await session.scalars(select(Guide).order_by(Guide.category, Guide.position, Guide.id))
    return list(result)


async def update(session: AsyncSession, guide: Guide, **fields) -> Guide:
    for key, value in fields.items():
        setattr(guide, key, value)
    await session.commit()
    return guide


async def delete(session: AsyncSession, guide: Guide) -> None:
    await session.delete(guide)
    await session.commit()


async def increment_views(session: AsyncSession, guide: Guide) -> None:
    guide.views += 1
    await session.commit()


async def count_active(session: AsyncSession) -> int:
    return await session.scalar(select(func.count()).select_from(Guide).where(Guide.is_active.is_(True))) or 0


async def top_viewed(session: AsyncSession, limit: int = 5) -> list[Guide]:
    result = await session.scalars(select(Guide).order_by(Guide.views.desc()).limit(limit))
    return list(result)
