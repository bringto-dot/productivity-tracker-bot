from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings as app_settings
from bot.database.models import User
from bot.database.repo import users as users_repo
from bot.keyboards.settings import reminder_time_keyboard, settings_keyboard
from bot.services.i18n import t

router = Router(name="settings")


@router.callback_query(F.data == "menu:settings")
async def cb_settings_menu(callback: CallbackQuery, user: User, lang: str) -> None:
    await callback.message.edit_text(t("settings.title", lang), reply_markup=settings_keyboard(lang, user))
    await callback.answer()


@router.callback_query(F.data.startswith("settings:lang:"))
async def cb_settings_lang(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    new_lang = callback.data.split(":")[-1]
    await users_repo.set_lang(session, user, new_lang)
    await callback.message.edit_text(t("settings.title", new_lang), reply_markup=settings_keyboard(new_lang, user))
    await callback.answer(t("settings.lang_switched", new_lang))


@router.callback_query(F.data == "settings:reminder")
async def cb_settings_reminder(callback: CallbackQuery, lang: str) -> None:
    await callback.message.edit_text(
        t("settings.choose_time", lang, timezone=app_settings.timezone), reply_markup=reminder_time_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("settings:reminder_time:"))
async def cb_settings_reminder_time(callback: CallbackQuery, session: AsyncSession, user: User, lang: str) -> None:
    value = callback.data.split(":")[-1]
    time_value = None if value == "off" else value
    await users_repo.set_reminder_time(session, user, time_value)

    alert_text = (
        t("settings.reminder_disabled", lang)
        if time_value is None
        else t("settings.reminder_set", lang, time=time_value, timezone=app_settings.timezone)
    )
    await callback.answer(alert_text, show_alert=False)
    await callback.message.edit_text(t("settings.title", lang), reply_markup=settings_keyboard(lang, user))


@router.callback_query(F.data == "settings:notif_toggle")
async def cb_settings_notif_toggle(callback: CallbackQuery, session: AsyncSession, user: User, lang: str) -> None:
    await users_repo.toggle_notifications(session, user)
    await callback.message.edit_text(t("settings.title", lang), reply_markup=settings_keyboard(lang, user))
    await callback.answer()
