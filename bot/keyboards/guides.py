from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models import Guide, GuideCategory
from bot.keyboards.common import add_back_row, pagination_row
from bot.services.i18n import t

_CATEGORY_KEYS = {
    GuideCategory.GUIDE: "guides.category_guide",
    GuideCategory.TRAINING: "guides.category_training",
    GuideCategory.LECTURE: "guides.category_lecture",
}


def categories_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for category, key in _CATEGORY_KEYS.items():
        builder.row(InlineKeyboardButton(text=t(key, lang), callback_data=f"guides:cat:{category.value}:0"))
    add_back_row(builder, lang)
    return builder.as_markup()


def guides_list_keyboard(
    lang: str, category: GuideCategory, guides: list[Guide], page: int, total_pages: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for guide in guides:
        label = f"⭐ {guide.title}" if guide.is_premium else guide.title
        builder.row(InlineKeyboardButton(text=label, callback_data=f"guides:item:{guide.id}"))
    pagination_row(builder, f"guides:cat:{category.value}", page, total_pages)
    add_back_row(builder, lang, "menu:guides")
    return builder.as_markup()


def guide_locked_keyboard(lang: str, category: GuideCategory) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t("guides.subscribe_button", lang), callback_data="menu:subscription"))
    add_back_row(builder, lang, f"guides:cat:{category.value}:0")
    return builder.as_markup()
