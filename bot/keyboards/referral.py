from urllib.parse import quote

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.common import add_back_row
from bot.services.i18n import t


def referral_keyboard(lang: str, link: str, share_text: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    share_url = f"https://t.me/share/url?url={quote(link)}&text={quote(share_text)}"
    builder.row(InlineKeyboardButton(text=t("referral.share_button", lang), url=share_url))
    add_back_row(builder, lang)
    return builder.as_markup()
