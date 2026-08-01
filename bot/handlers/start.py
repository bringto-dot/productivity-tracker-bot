from aiogram import F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.database.repo import users as users_repo
from bot.keyboards.main_menu import main_menu_keyboard
from bot.services.i18n import t
from bot.services.referral import parse_start_payload

router = Router(name="start")


def _language_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="start:lang:ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="start:lang:en"),
    )
    return builder.as_markup()


async def show_main_menu(message: Message, lang: str, is_admin: bool) -> None:
    await message.answer(t("menu.title", lang), reply_markup=main_menu_keyboard(lang, is_admin))


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    command: CommandObject,
    session: AsyncSession,
    user: User,
    is_new_user: bool,
    lang: str,
    is_admin: bool,
) -> None:
    if is_new_user and command.args:
        code = parse_start_payload(command.args)
        if code:
            referrer = await users_repo.get_by_referral_code(session, code)
            if referrer is not None and referrer.id != user.id:
                user.referred_by = referrer.id
                await session.commit()

    if is_new_user:
        await message.answer(t("start.choose_language", lang), reply_markup=_language_keyboard())
        return

    await message.answer(t("start.welcome", lang))
    await show_main_menu(message, lang, is_admin)


@router.callback_query(F.data.startswith("start:lang:"))
async def cb_choose_language(callback: CallbackQuery, session: AsyncSession, user: User, is_admin: bool) -> None:
    lang = callback.data.split(":")[-1]
    await users_repo.set_lang(session, user, lang)
    await callback.message.edit_text(t("start.welcome", lang))
    await callback.message.answer(t("menu.title", lang), reply_markup=main_menu_keyboard(lang, is_admin))
    await callback.answer()


@router.callback_query(F.data == "menu:main")
async def cb_main_menu(callback: CallbackQuery, lang: str, is_admin: bool) -> None:
    await callback.message.edit_text(t("menu.title", lang), reply_markup=main_menu_keyboard(lang, is_admin))
    await callback.answer()


@router.callback_query(F.data == "noop")
async def cb_noop(callback: CallbackQuery) -> None:
    await callback.answer()
