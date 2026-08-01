from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.services.i18n import t


def add_back_row(builder: InlineKeyboardBuilder, lang: str, callback_data: str = "menu:main") -> None:
    builder.row(InlineKeyboardButton(text=t("common.back", lang), callback_data=callback_data))


def pagination_row(builder: InlineKeyboardBuilder, prefix: str, page: int, total_pages: int) -> None:
    if total_pages <= 1:
        return
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"{prefix}:{page - 1}"))
    buttons.append(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"{prefix}:{page + 1}"))
    builder.row(*buttons)
