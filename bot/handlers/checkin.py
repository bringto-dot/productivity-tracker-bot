from datetime import date, timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.database.repo import analytics as analytics_repo
from bot.database.repo import checkins as checkins_repo
from bot.keyboards.checkin import score_keyboard, skip_note_keyboard
from bot.keyboards.main_menu import main_menu_keyboard
from bot.services import streaks
from bot.services.i18n import t
from bot.services.referral import reward_referrer_on_first_checkin
from bot.states.checkin_states import CheckinStates

router = Router(name="checkin")


@router.callback_query(F.data == "menu:checkin")
async def cb_checkin_start(callback: CallbackQuery, session: AsyncSession, user: User, lang: str, is_admin: bool) -> None:
    today = date.today()
    existing = await checkins_repo.get_for_date(session, user.id, today)
    if existing is not None:
        dates = await checkins_repo.get_dates_desc(session, user.id)
        streak = streaks.current_streak(dates, today)
        await callback.message.edit_text(
            t("checkin.already_done", lang, score=existing.score, streak=streak),
            reply_markup=main_menu_keyboard(lang, is_admin),
        )
        await callback.answer()
        return

    await callback.message.edit_text(t("checkin.ask_score", lang), reply_markup=score_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("checkin:score:"))
async def cb_checkin_score(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    score = int(callback.data.split(":")[-1])
    await state.update_data(score=score)
    await state.set_state(CheckinStates.waiting_note)
    await callback.message.edit_text(t("checkin.ask_note", lang), reply_markup=skip_note_keyboard(lang))
    await callback.answer()


async def _finish_checkin(
    message_target: Message,
    session: AsyncSession,
    user: User,
    lang: str,
    score: int,
    note: str | None,
    is_admin: bool,
) -> None:
    today = date.today()
    await checkins_repo.create(session, user.id, today, score, note)
    await analytics_repo.log_event(session, user.id, "checkin", {"score": score})

    dates = await checkins_repo.get_dates_desc(session, user.id)
    current = streaks.current_streak(dates, today)
    scores_7d = await checkins_repo.get_scores_since(session, user.id, today - timedelta(days=6))
    avg7 = streaks.format_average(streaks.average(scores_7d))

    total_checkins = await checkins_repo.count_for_user(session, user.id)
    text = t("checkin.saved", lang, score=score, streak=current, avg7=avg7)

    if total_checkins == 1:
        reward_days = await reward_referrer_on_first_checkin(session, user)
        if reward_days:
            text += t("checkin.referral_bonus_note", lang, days=reward_days)

    await message_target.answer(text, reply_markup=main_menu_keyboard(lang, is_admin))


@router.callback_query(F.data == "checkin:skip_note")
async def cb_checkin_skip_note(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, user: User, lang: str, is_admin: bool
) -> None:
    data = await state.get_data()
    score = data.get("score")
    await state.clear()
    await callback.message.delete()
    await _finish_checkin(callback.message, session, user, lang, score, None, is_admin)
    await callback.answer()


@router.message(CheckinStates.waiting_note)
async def msg_checkin_note(
    message: Message, state: FSMContext, session: AsyncSession, user: User, lang: str, is_admin: bool
) -> None:
    data = await state.get_data()
    score = data.get("score")
    await state.clear()
    await _finish_checkin(message, session, user, lang, score, message.text, is_admin)
