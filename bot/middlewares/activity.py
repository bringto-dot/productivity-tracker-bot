from collections.abc import Awaitable, Callable
from datetime import date
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.database.repo import analytics as analytics_repo


class ActivityMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("user")
        session = data.get("session")
        if user is not None and session is not None:
            await analytics_repo.mark_activity(session, user.id, date.today())
        return await handler(event, data)
