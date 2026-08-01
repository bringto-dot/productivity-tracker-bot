from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import GuideCategory, User
from bot.database.repo import analytics as analytics_repo
from bot.database.repo import guides as guides_repo
from bot.keyboards.guides import categories_keyboard, guide_locked_keyboard, guides_list_keyboard
from bot.services.i18n import t

router = Router(name="guides")

_PAGE_SIZE = 8


@router.callback_query(F.data == "menu:guides")
async def cb_guides_menu(callback: CallbackQuery, lang: str) -> None:
    await callback.message.edit_text(t("guides.title", lang), reply_markup=categories_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("guides:cat:"))
async def cb_guides_category(callback: CallbackQuery, session: AsyncSession, lang: str) -> None:
    _, _, category_value, page_str = callback.data.split(":")
    category = GuideCategory(category_value)
    page = int(page_str)

    all_guides = await guides_repo.list_by_category(session, category)
    if not all_guides:
        await callback.message.edit_text(t("guides.empty", lang), reply_markup=categories_keyboard(lang))
        await callback.answer()
        return

    total_pages = max(1, (len(all_guides) + _PAGE_SIZE - 1) // _PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))
    page_items = all_guides[page * _PAGE_SIZE : page * _PAGE_SIZE + _PAGE_SIZE]

    await callback.message.edit_text(
        t(f"guides.category_{category.value}", lang),
        reply_markup=guides_list_keyboard(lang, category, page_items, page, total_pages),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("guides:item:"))
async def cb_guide_item(callback: CallbackQuery, session: AsyncSession, user: User, lang: str) -> None:
    guide_id = int(callback.data.split(":")[-1])
    guide = await guides_repo.get(session, guide_id)
    if guide is None or not guide.is_active:
        await callback.answer()
        return

    if guide.is_premium and not user.has_active_premium:
        await callback.message.edit_text(
            t("guides.premium_locked", lang, title=guide.title),
            reply_markup=guide_locked_keyboard(lang, guide.category),
        )
        await callback.answer()
        return

    await callback.answer()
    document = FSInputFile(guide.file_id) if guide.is_local_file else guide.file_id
    await callback.message.answer_document(document, caption=guide.title)
    await guides_repo.increment_views(session, guide)
    await analytics_repo.log_event(session, user.id, "guide_view", {"guide_id": guide.id})
