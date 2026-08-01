from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models import SubscriptionPlan
from bot.keyboards.common import add_back_row
from bot.services.i18n import t


def plans_keyboard(lang: str, plans: list[SubscriptionPlan]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for plan in plans:
        text = t("subscription.plan_button", lang, title=plan.title, price=plan.stars_price)
        builder.row(InlineKeyboardButton(text=text, callback_data=f"sub:plan:{plan.id}"))
    add_back_row(builder, lang)
    return builder.as_markup()
