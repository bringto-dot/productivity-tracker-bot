from datetime import date, timedelta

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.database.repo import checkins as checkins_repo
from bot.keyboards.stats import history_keyboard, stats_keyboard
from bot.services import streaks
from bot.services.i18n import t

router = Router(name="stats")

_PAGE_SIZE = 10


@router.callback_query(F.data == "menu:stats")
async def cb_stats(callback: CallbackQuery, session: AsyncSession, user: User, lang: str) -> None:
    total = await checkins_repo.count_for_user(session, user.id)
    if total == 0:
        await callback.message.edit_text(t("stats.no_data", lang), reply_markup=stats_keyboard(lang))
        await callback.answer()
        return

    today = date.today()
    dates = await checkins_repo.get_dates_desc(session, user.id)
    current = streaks.current_streak(dates, today)
    best = streaks.best_streak(dates)
    scores_7d = await checkins_repo.get_scores_since(session, user.id, today - timedelta(days=6))
    scores_30d = await checkins_repo.get_scores_since(session, user.id, today - timedelta(days=29))
    avg7 = streaks.format_average(streaks.average(scores_7d))
    avg30 = streaks.format_average(streaks.average(scores_30d))
    last_date = dates[0].isoformat()

    text = t(
        "stats.body",
        lang,
        current_streak=current,
        best_streak=best,
        total=total,
        avg7=avg7,
        avg30=avg30,
        last_date=last_date,
    )
    await callback.message.edit_text(text, reply_markup=stats_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("stats:history:"))
async def cb_history(callback: CallbackQuery, session: AsyncSession, user: User, lang: str) -> None:
    page = int(callback.data.split(":")[-1])
    total = await checkins_repo.count_for_user(session, user.id)
    total_pages = max(1, (total + _PAGE_SIZE - 1) // _PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))

    entries = await checkins_repo.list_page(session, user.id, page * _PAGE_SIZE, _PAGE_SIZE)
    if not entries:
        text = t("stats.history_empty", lang)
    else:
        lines = [
            t(
                "stats.history_entry",
                lang,
                date=c.date.isoformat(),
                score=c.score,
                note=f" — {c.note}" if c.note else "",
            )
            for c in entries
        ]
        title = t("stats.history_title", lang, page=page + 1, pages=total_pages)
        text = title + "\n\n" + "\n".join(lines)

    await callback.message.edit_text(text, reply_markup=history_keyboard(lang, page, total_pages))
    await callback.answer()
