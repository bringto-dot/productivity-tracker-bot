from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.filters.admin import IsAdmin
from bot.keyboards.admin import admin_menu_keyboard

router = Router(name="admin_panel")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    await message.answer("🛠 Админ-панель", reply_markup=admin_menu_keyboard())


@router.callback_query(F.data == "admin:menu")
async def cb_admin_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text("🛠 Админ-панель", reply_markup=admin_menu_keyboard())
    await callback.answer()
