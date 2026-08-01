from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.database.repo import referrals as referrals_repo
from bot.keyboards.referral import referral_keyboard
from bot.services.i18n import t
from bot.services.referral import REFERRAL_REWARD_DAYS, build_referral_link

router = Router(name="referral")


@router.callback_query(F.data == "menu:referral")
async def cb_referral(callback: CallbackQuery, session: AsyncSession, user: User, lang: str, bot_username: str) -> None:
    link = build_referral_link(bot_username, user.referral_code)
    count = await referrals_repo.count_rewarded_by_referrer(session, user.id)
    share_text = t("referral.share_text", lang)

    text = t("referral.title", lang, reward_days=REFERRAL_REWARD_DAYS, link=link, count=count)
    await callback.message.edit_text(text, reply_markup=referral_keyboard(lang, link, share_text))
    await callback.answer()
