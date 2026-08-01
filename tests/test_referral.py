from bot.database.repo import referrals as referrals_repo
from bot.database.repo import users as users_repo
from bot.services.referral import (
    REFERRAL_REWARD_DAYS,
    build_referral_link,
    parse_start_payload,
    reward_referrer_on_first_checkin,
)


def test_parse_start_payload():
    assert parse_start_payload("ref_ABC123") == "ABC123"
    assert parse_start_payload("something_else") is None
    assert parse_start_payload(None) is None


def test_build_referral_link():
    assert build_referral_link("my_bot", "XYZ") == "https://t.me/my_bot?start=ref_XYZ"


async def test_reward_referrer_grants_premium_once(session):
    referrer, _ = await users_repo.get_or_create(session, tg_id=1, username="ref", first_name="R", default_lang="ru")
    referred, _ = await users_repo.get_or_create(
        session, tg_id=2, username="new", first_name="N", default_lang="ru", referred_by=referrer.id
    )

    reward = await reward_referrer_on_first_checkin(session, referred)
    assert reward == REFERRAL_REWARD_DAYS

    await session.refresh(referrer)
    assert referrer.has_active_premium

    reward_again = await reward_referrer_on_first_checkin(session, referred)
    assert reward_again is None

    count = await referrals_repo.count_rewarded_by_referrer(session, referrer.id)
    assert count == 1


async def test_no_reward_when_not_referred(session):
    solo, _ = await users_repo.get_or_create(session, tg_id=3, username="solo", first_name="S", default_lang="ru")
    reward = await reward_referrer_on_first_checkin(session, solo)
    assert reward is None
