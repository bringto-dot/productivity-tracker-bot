from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.services.i18n import t


def main_menu_keyboard(lang: str, is_admin: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("menu.checkin", lang), callback_data="menu:checkin")
    builder.button(text=t("menu.stats", lang), callback_data="menu:stats")
    builder.button(text=t("menu.guides", lang), callback_data="menu:guides")
    builder.button(text=t("menu.referral", lang), callback_data="menu:referral")
    builder.button(text=t("menu.subscription", lang), callback_data="menu:subscription")
    builder.button(text=t("menu.settings", lang), callback_data="menu:settings")
    builder.adjust(2)
    if is_admin:
        builder.row(InlineKeyboardButton(text=t("menu.admin", lang), callback_data="admin:menu"))
    return builder.as_markup()
