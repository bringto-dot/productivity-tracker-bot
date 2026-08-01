from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, TelegramObject

_RESET_PREFIXES = ("menu:", "admin:menu", "admin:guides", "admin:users", "admin:plans", "admin:broadcast", "admin:stats")


class StateResetMiddleware(BaseMiddleware):
    """Clears any dangling FSM state when the user navigates to a top-level menu,
    so an abandoned flow (e.g. checkin note, admin guide upload) can't hijack a
    later, unrelated message."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, CallbackQuery) and event.data and event.data.startswith(_RESET_PREFIXES):
            state: FSMContext | None = data.get("state")
            if state is not None:
                await state.clear()
        return await handler(event, data)
