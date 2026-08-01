import asyncio
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repo import broadcasts as broadcasts_repo
from bot.database.repo import users as users_repo
from bot.filters.admin import IsAdmin
from bot.keyboards.admin import admin_broadcast_confirm_keyboard, admin_broadcast_keyboard
from bot.states.admin_states import AdminBroadcastStates

router = Router(name="admin_broadcast")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

logger = logging.getLogger(__name__)


@router.callback_query(F.data == "admin:broadcast")
async def cb_admin_broadcast_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text("📣 Рассылка", reply_markup=admin_broadcast_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin:b:start")
async def cb_admin_broadcast_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminBroadcastStates.waiting_text)
    await callback.message.edit_text("Пришли текст рассылки одним сообщением.")
    await callback.answer()


@router.message(AdminBroadcastStates.waiting_text)
async def msg_admin_broadcast_text(message: Message, state: FSMContext) -> None:
    await state.update_data(text=message.text)
    await state.set_state(AdminBroadcastStates.waiting_confirm)
    await message.answer(
        f"Предпросмотр:\n\n{message.text}\n\nОтправить всем пользователям?",
        reply_markup=admin_broadcast_confirm_keyboard(),
    )


@router.callback_query(AdminBroadcastStates.waiting_confirm, F.data == "admin:b:cancel")
async def cb_admin_broadcast_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("Рассылка отменена.", reply_markup=admin_broadcast_keyboard())
    await callback.answer()


@router.callback_query(AdminBroadcastStates.waiting_confirm, F.data == "admin:b:confirm")
async def cb_admin_broadcast_confirm(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    text = data.get("text", "")
    await state.clear()

    broadcast = await broadcasts_repo.create(session, callback.from_user.id, text)
    await callback.message.edit_text("🚀 Рассылка запущена, отчёт пришлю по завершении.")
    await callback.answer()

    tg_ids = await users_repo.list_active_for_broadcast(session)
    sent, failed = 0, 0
    for tg_id in tg_ids:
        try:
            await callback.bot.send_message(tg_id, text)
            sent += 1
        except Exception:
            failed += 1
            logger.warning("Broadcast failed for %s", tg_id, exc_info=True)
        await asyncio.sleep(0.05)

    await broadcasts_repo.update_counts(session, broadcast, sent, failed)
    await callback.message.answer(f"✅ Рассылка завершена.\nОтправлено: {sent}\nНе доставлено: {failed}")
