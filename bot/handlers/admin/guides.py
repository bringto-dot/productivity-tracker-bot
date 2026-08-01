from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import GuideCategory
from bot.database.repo import guides as guides_repo
from bot.filters.admin import IsAdmin
from bot.keyboards.admin import (
    admin_guide_category_pick_keyboard,
    admin_guide_view_keyboard,
    admin_guides_list_keyboard,
    admin_guides_menu_keyboard,
    admin_yes_no_keyboard,
)
from bot.states.admin_states import AdminGuideStates

router = Router(name="admin_guides")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

_PAGE_SIZE = 8


@router.callback_query(F.data == "admin:guides")
async def cb_admin_guides_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text("📚 Материалы", reply_markup=admin_guides_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("admin:g:list:"))
async def cb_admin_guides_list(callback: CallbackQuery, session: AsyncSession) -> None:
    _, _, _, category_value, page_str = callback.data.split(":")
    category = GuideCategory(category_value)
    page = int(page_str)

    all_guides = await guides_repo.list_by_category(session, category, only_active=False)
    total_pages = max(1, (len(all_guides) + _PAGE_SIZE - 1) // _PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))
    page_items = all_guides[page * _PAGE_SIZE : page * _PAGE_SIZE + _PAGE_SIZE]

    text = f"Материалов в разделе: {len(all_guides)}" if all_guides else "Пока пусто."
    await callback.message.edit_text(
        text, reply_markup=admin_guides_list_keyboard(page_items, category.value, page, total_pages)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:g:view:"))
async def cb_admin_guide_view(callback: CallbackQuery, session: AsyncSession) -> None:
    guide_id = int(callback.data.split(":")[-1])
    guide = await guides_repo.get(session, guide_id)
    if guide is None:
        await callback.answer("Не найдено", show_alert=True)
        return

    text = (
        f"{'⭐ ' if guide.is_premium else ''}{guide.title}\n\n"
        f"{guide.description or '—'}\n\n"
        f"Категория: {guide.category.value}\n"
        f"Просмотров: {guide.views}\n"
        f"Активен: {'да' if guide.is_active else 'нет'}"
    )
    await callback.message.edit_text(text, reply_markup=admin_guide_view_keyboard(guide.id))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:g:del:"))
async def cb_admin_guide_delete(callback: CallbackQuery, session: AsyncSession) -> None:
    guide_id = int(callback.data.split(":")[-1])
    guide = await guides_repo.get(session, guide_id)
    if guide is not None:
        await guides_repo.delete(session, guide)
    await callback.message.edit_text("🗑 Материал удалён.", reply_markup=admin_guides_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin:g:add")
async def cb_admin_guide_add_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminGuideStates.waiting_file)
    await callback.message.edit_text("Пришли PDF-файл материала документом.")
    await callback.answer()


@router.message(AdminGuideStates.waiting_file, F.document)
async def msg_admin_guide_file(message: Message, state: FSMContext) -> None:
    await state.update_data(file_id=message.document.file_id)
    await state.set_state(AdminGuideStates.waiting_title)
    await message.answer("Название материала?")


@router.message(AdminGuideStates.waiting_file)
async def msg_admin_guide_file_invalid(message: Message) -> None:
    await message.answer("Нужно прислать именно файл (документ), например PDF.")


@router.message(AdminGuideStates.waiting_title)
async def msg_admin_guide_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(AdminGuideStates.waiting_description)
    await message.answer("Краткое описание? (или «-», чтобы пропустить)")


@router.message(AdminGuideStates.waiting_description)
async def msg_admin_guide_description(message: Message, state: FSMContext) -> None:
    description = None if (message.text or "").strip() == "-" else message.text
    await state.update_data(description=description)
    await state.set_state(AdminGuideStates.waiting_category)
    await message.answer("Выбери категорию:", reply_markup=admin_guide_category_pick_keyboard())


@router.callback_query(AdminGuideStates.waiting_category, F.data.startswith("admin:g:setcat:"))
async def cb_admin_guide_category(callback: CallbackQuery, state: FSMContext) -> None:
    category_value = callback.data.split(":")[-1]
    await state.update_data(category=category_value)
    await state.set_state(AdminGuideStates.waiting_premium_flag)
    await callback.message.edit_text(
        "Материал только по подписке (премиум)?",
        reply_markup=admin_yes_no_keyboard("admin:g:premium:yes", "admin:g:premium:no"),
    )
    await callback.answer()


@router.callback_query(AdminGuideStates.waiting_premium_flag, F.data.startswith("admin:g:premium:"))
async def cb_admin_guide_premium(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    is_premium = callback.data.split(":")[-1] == "yes"
    data = await state.get_data()
    await state.clear()

    guide = await guides_repo.create(
        session,
        title=data["title"],
        description=data.get("description"),
        category=GuideCategory(data["category"]),
        file_id=data["file_id"],
        is_premium=is_premium,
    )
    await callback.message.edit_text(
        f"✅ Материал «{guide.title}» добавлен.", reply_markup=admin_guides_menu_keyboard()
    )
    await callback.answer()
