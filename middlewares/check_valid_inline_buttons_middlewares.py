import datetime
from typing import Dict, Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery


class CheckValidInlineButtonsMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        seconds_delta = datetime.datetime.now().timestamp() - event.message.date.timestamp()

        if seconds_delta > 43200:
            await event.answer('⌛ Срок действия клавиатуры истек! Повторите команду!', show_alert=True)
        else:
            return await handler(event, data)
