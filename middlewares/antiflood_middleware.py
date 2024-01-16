from datetime import datetime
from typing import Dict, Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import Update
from db_logic import get_user_info_antiflood_in_redis, set_user_info_antiflood_in_redis, add_1_to_user_info_in_redis, \
    get_blocking_date_and_period, set_blocking_date_and_period


class AntifloodMiddleware(BaseMiddleware):

    @staticmethod
    def convert_seconds(seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        return f"{int(days)} дней {int(hours):02d} часов {int(minutes):02d} минут {int(seconds):02d} секунд"

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:

        async def is_user_blocked(user_id):
            blocking_date, blocking_period = await get_blocking_date_and_period(str(user_id))
            if not blocking_date:
                return False

            now_date = datetime.now().timestamp()
            blocking_date_timestamp = blocking_date.timestamp()
            return (now_date - blocking_date_timestamp) < blocking_period

        async def handle_too_many_requests(user_id, event):
            await set_blocking_date_and_period(str(user_id))
            blocking_date, blocking_period = await get_blocking_date_and_period(str(user_id))
            formatted_blocking_period = self.convert_seconds(blocking_period)
            message_text = (
                f"🚫️ Вы осуществили множество действий за короткий промежуток времени "
                f"и заблокированы на: {formatted_blocking_period}"
            )

            if event.callback_query:
                await event.callback_query.answer()
                await event.callback_query.message.answer(text=message_text)
            else:
                await event.message.answer(text=message_text)

        async def check_flood_and_handle(event, user_id):
            # Начинаем с обработки команды /start без флуд-контроля
            if event.message and event.message.text == '/start':
                return await handler(event, data)

            # Проверка блокировки пользователя
            if await is_user_blocked(user_id):
                return  # Завершаем выполнение, если пользователь заблокирован

            # Проверка флуда
            info_in_redis = get_user_info_antiflood_in_redis(user_id)
            if info_in_redis and int(info_in_redis) >= 5:
                await handle_too_many_requests(user_id, event)
                return

            if not info_in_redis:
                set_user_info_antiflood_in_redis(user_id)
            else:
                add_1_to_user_info_in_redis(user_id)

            # Обработка события дальше, если не было обнаружено нарушений
            return await handler(event, data)

        # Функция для обработки событий
        async def event_handler(event, data):
            user_id = data['event_from_user'].id
            await check_flood_and_handle(event, user_id)

        await event_handler(event, data)
