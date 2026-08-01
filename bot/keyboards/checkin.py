from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.services.i18n import t


def score_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for score in range(1, 11):
        builder.button(text=str(score), callback_data=f"checkin:score:{score}")
    builder.adjust(5, 5)
    return builder.as_markup()


def skip_note_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("checkin.skip_note", lang), callback_data="checkin:skip_note")
    return builder.as_markup()
