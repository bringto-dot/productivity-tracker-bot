from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models import User
from bot.keyboards.common import add_back_row
from bot.services.i18n import t

_REMINDER_OPTIONS = ["09:00", "12:00", "18:00", "21:00"]


def settings_keyboard(lang: str, user: User) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    other_lang = "en" if lang == "ru" else "ru"
    lang_label = "🌐 English" if lang == "ru" else "🌐 Русский"
    builder.row(InlineKeyboardButton(text=lang_label, callback_data=f"settings:lang:{other_lang}"))

    reminder_label = user.reminder_time or t("settings.reminder_off_label", lang)
    builder.row(
        InlineKeyboardButton(
            text=t("settings.reminder_button", lang, time=reminder_label), callback_data="settings:reminder"
        )
    )

    notif_key = "settings.notifications_on" if user.notifications_on else "settings.notifications_off"
    builder.row(InlineKeyboardButton(text=t(notif_key, lang), callback_data="settings:notif_toggle"))

    add_back_row(builder, lang)
    return builder.as_markup()


def reminder_time_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for option in _REMINDER_OPTIONS:
        builder.button(text=option, callback_data=f"settings:reminder_time:{option}")
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(text=t("settings.reminder_off_label", lang), callback_data="settings:reminder_time:off")
    )
    add_back_row(builder, lang, "menu:settings")
    return builder.as_markup()
