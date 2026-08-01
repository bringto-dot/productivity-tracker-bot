from datetime import timedelta

from bot.database.models import utcnow
from bot.database.repo import users as users_repo
from bot.services.stars_payments import build_payload, parse_payload


def test_payload_round_trip():
    assert parse_payload(build_payload(42)) == 42


def test_parse_payload_rejects_unknown_format():
    assert parse_payload("not_a_payload") is None
    assert parse_payload("sub_plan_abc") is None


async def test_grant_premium_days_extends_from_existing_expiry(session):
    user, _ = await users_repo.get_or_create(session, tg_id=1, username="a", first_name="A", default_lang="ru")

    first_until = await users_repo.grant_premium_days(session, user, 7)
    assert first_until - utcnow() > timedelta(days=6)

    second_until = await users_repo.grant_premium_days(session, user, 3)
    assert second_until - first_until == timedelta(days=3)


async def test_grant_premium_days_from_scratch_when_expired(session):
    user, _ = await users_repo.get_or_create(session, tg_id=2, username="b", first_name="B", default_lang="ru")
    user.premium_until = utcnow() - timedelta(days=10)
    await session.commit()

    new_until = await users_repo.grant_premium_days(session, user, 5)
    assert new_until - utcnow() < timedelta(days=6)
    assert new_until > utcnow()
