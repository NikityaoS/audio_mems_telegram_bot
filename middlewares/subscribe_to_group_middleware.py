import hashlib
from datetime import datetime
from typing import Dict, Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.enums import ChatMemberStatus
from aiogram.types import Update, InlineQueryResultArticle, InputTextMessageContent


class SubscribeMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:

        user_id = data['event_from_user'].id

        from main import bot
        item = await bot.get_chat_member(chat_id="@astib_bot", user_id=user_id)
        print(item)
        text = '📢 Для доступа к боту подпишитесь на канал: <a href="https://t.me/astib_bot">Audio Stickers Box</a>'

        if item.status == ChatMemberStatus.LEFT and event.message and event.message.text.startswith('/start'):
            await handler(event, data)
            await event.message.answer(text=text)

        elif item.status == ChatMemberStatus.LEFT:
            if event.callback_query:
                await event.callback_query.message.answer(text=text)
                await event.callback_query.answer()
                return
            elif event.message:
                print(event.message.text)
                await event.message.answer(text=text)
                return
            elif event.inline_query:
                result_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()
                inline_quer_res = InlineQueryResultArticle(id=result_id,
                                                           title='☝️нажмите на надпись вверху ☝️',
                                                           input_message_content=InputTextMessageContent(
                                                               message_text='Бот аудио-стикеров <a href="https://t.me/astibbot">Audio Stickers Box</a>'
                                                           ))
                await event.inline_query.answer(
                    results=[inline_quer_res],
                    cache_time=20,
                    switch_pm_parameter='q',
                    switch_pm_text='Получить доступ к боту'
                )


        else:
            return await handler(event, data)
