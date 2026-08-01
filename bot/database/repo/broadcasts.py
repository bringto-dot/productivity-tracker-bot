from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Broadcast


async def create(session: AsyncSession, admin_tg_id: int, text: str) -> Broadcast:
    broadcast = Broadcast(admin_tg_id=admin_tg_id, text=text)
    session.add(broadcast)
    await session.commit()
    await session.refresh(broadcast)
    return broadcast


async def update_counts(session: AsyncSession, broadcast: Broadcast, sent: int, failed: int) -> None:
    broadcast.sent_count = sent
    broadcast.failed_count = failed
    await session.commit()
