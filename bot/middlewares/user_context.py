from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.database.repo import users as users_repo


class UserContextMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user = data.get("event_from_user")
        if tg_user is None:
            return await handler(event, data)

        session: AsyncSession = data["session"]
        user, is_new = await users_repo.get_or_create(
            session,
            tg_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            default_lang=settings.default_lang,
        )

        if user.is_banned:
            return None

        data["user"] = user
        data["is_new_user"] = is_new
        data["lang"] = user.lang
        data["is_admin"] = tg_user.id in settings.admin_id_list

        return await handler(event, data)
