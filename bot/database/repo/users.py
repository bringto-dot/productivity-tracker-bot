import secrets
import string
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User, utcnow

_ALPHABET = string.ascii_uppercase + string.digits


async def _generate_unique_referral_code(session: AsyncSession) -> str:
    while True:
        code = "".join(secrets.choice(_ALPHABET) for _ in range(8))
        existing = await session.scalar(select(User).where(User.referral_code == code))
        if existing is None:
            return code


async def get_by_tg_id(session: AsyncSession, tg_id: int) -> User | None:
    return await session.scalar(select(User).where(User.tg_id == tg_id))


async def get_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def get_by_referral_code(session: AsyncSession, code: str) -> User | None:
    return await session.scalar(select(User).where(User.referral_code == code))


async def get_or_create(
    session: AsyncSession,
    tg_id: int,
    username: str | None,
    first_name: str | None,
    default_lang: str,
    referred_by: int | None = None,
) -> tuple[User, bool]:
    user = await get_by_tg_id(session, tg_id)
    if user is not None:
        changed = False
        if user.username != username:
            user.username = username
            changed = True
        if user.first_name != first_name:
            user.first_name = first_name
            changed = True
        if changed:
            await session.commit()
        return user, False

    code = await _generate_unique_referral_code(session)
    user = User(
        tg_id=tg_id,
        username=username,
        first_name=first_name,
        lang=default_lang,
        referral_code=code,
        referred_by=referred_by,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user, True


async def set_lang(session: AsyncSession, user: User, lang: str) -> None:
    user.lang = lang
    await session.commit()


async def set_reminder_time(session: AsyncSession, user: User, time_str: str | None) -> None:
    user.reminder_time = time_str
    await session.commit()


async def toggle_notifications(session: AsyncSession, user: User) -> bool:
    user.notifications_on = not user.notifications_on
    await session.commit()
    return user.notifications_on


async def grant_premium_days(session: AsyncSession, user: User, days: int) -> datetime:
    now = utcnow()
    base = user.premium_until if (user.premium_until and user.premium_until > now) else now
    user.premium_until = base + timedelta(days=days)
    await session.commit()
    return user.premium_until


async def set_banned(session: AsyncSession, user: User, banned: bool) -> None:
    user.is_banned = banned
    await session.commit()


async def search(session: AsyncSession, query: str, limit: int = 10) -> list[User]:
    query = query.strip().lstrip("@")
    stmt = select(User).limit(limit)
    if query.isdigit():
        stmt = stmt.where((User.tg_id == int(query)) | (User.id == int(query)))
    else:
        stmt = stmt.where(User.username.ilike(f"%{query}%"))
    result = await session.scalars(stmt)
    return list(result)


async def count_all(session: AsyncSession) -> int:
    return await session.scalar(select(func.count()).select_from(User)) or 0


async def count_premium_active(session: AsyncSession) -> int:
    now = utcnow()
    return await session.scalar(
        select(func.count()).select_from(User).where(User.premium_until.is_not(None), User.premium_until > now)
    ) or 0


async def count_banned(session: AsyncSession) -> int:
    return await session.scalar(select(func.count()).select_from(User).where(User.is_banned.is_(True))) or 0


async def list_active_for_broadcast(session: AsyncSession) -> list[int]:
    result = await session.scalars(select(User.tg_id).where(User.is_banned.is_(False)))
    return list(result)


async def list_due_reminders(session: AsyncSession, hh_mm: str) -> list[User]:
    result = await session.scalars(
        select(User).where(
            User.reminder_time == hh_mm,
            User.notifications_on.is_(True),
            User.is_banned.is_(False),
        )
    )
    return list(result)


async def new_users_since(session: AsyncSession, since: datetime) -> int:
    return await session.scalar(select(func.count()).select_from(User).where(User.created_at >= since)) or 0


async def list_premium_expiring_within(session: AsyncSession, hours: int) -> list[User]:
    now = utcnow()
    horizon = now + timedelta(hours=hours)
    result = await session.scalars(
        select(User).where(
            User.premium_until.is_not(None),
            User.premium_until > now,
            User.premium_until <= horizon,
        )
    )
    return list(result)
