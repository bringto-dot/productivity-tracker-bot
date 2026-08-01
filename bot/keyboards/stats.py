from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.common import add_back_row, pagination_row
from bot.services.i18n import t


def stats_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t("stats.button_history", lang), callback_data="stats:history:0"))
    add_back_row(builder, lang)
    return builder.as_markup()


def history_keyboard(lang: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    pagination_row(builder, "stats:history", page, total_pages)
    add_back_row(builder, lang, "menu:stats")
    return builder.as_markup()
