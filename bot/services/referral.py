from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.database.repo import referrals as referrals_repo
from bot.database.repo import users as users_repo

REFERRAL_REWARD_DAYS = 3


def build_referral_link(bot_username: str, referral_code: str) -> str:
    return f"https://t.me/{bot_username}?start=ref_{referral_code}"


def parse_start_payload(payload: str | None) -> str | None:
    if payload and payload.startswith("ref_"):
        code = payload[len("ref_"):]
        return code or None
    return None


async def reward_referrer_on_first_checkin(session: AsyncSession, referred_user: User) -> int | None:
    if referred_user.referred_by is None:
        return None

    existing = await referrals_repo.get_event_for_referred(session, referred_user.id)
    if existing is not None and existing.rewarded:
        return None
    if existing is None:
        existing = await referrals_repo.create_event(
            session, referrer_id=referred_user.referred_by, referred_id=referred_user.id
        )

    referrer = await users_repo.get_by_id(session, referred_user.referred_by)
    if referrer is None:
        return None

    await users_repo.grant_premium_days(session, referrer, REFERRAL_REWARD_DAYS)
    await referrals_repo.mark_rewarded(session, existing, REFERRAL_REWARD_DAYS)
    return REFERRAL_REWARD_DAYS
