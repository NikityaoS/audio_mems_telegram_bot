import datetime

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from keyboards.keyboards import SoundsCallbackFactory




def check_subscrib_to_channel_1param(func):
    """
    Декоратор для функций с 2 параметрами. Проверяет, подписан ли пользователь на канал,
    если нет, то отправляет сообщение о подписке.
    :param func:
    :return:
    """
    async def wrapper(update):
        try:
            from main import bot
            await bot.get_chat_member(chat_id=-1001992217206, user_id=806012412)
        except TelegramBadRequest:
            if isinstance(update, Message):
                await update.answer(text='📢 Для доступа к боту подпишитесь на канал: CHANEL!!!!')
            else:
                await update.message.answer(text='📢 Для доступа к боту подпишитесь на канал: CHANEL!!!!')
                await update.answer()
        else:
            result = await func(update)
            return result
    return wrapper


def check_subscrib_to_channel_2param(func):
    """
    Декоратор для функций с 2 параметрами. Проверяет, подписан ли пользователь на канал,
    если нет, то отправляет сообщение о подписке.
    :param func:
    :return:
    """
    async def wrapper(callback: CallbackQuery, callback_data: SoundsCallbackFactory):
        try:
            from main import bot
            await bot.get_chat_member(chat_id=-1001992217206, user_id=806012412)
        except TelegramBadRequest:
            await callback.message.answer(text='📢 Для доступа к боту подпишитесь на канал: CHANEL!!!!')
            await callback.answer()
        else:
            result = await func(callback, callback_data)
            return result
    return wrapper


def check_date_pagination_btn_2param(func):
    async def wrapper(callback: CallbackQuery,
                      callback_data: SoundsCallbackFactory):
        if callback.message.date.date() != datetime.datetime.now().date():
            await callback.answer('⌛ Спискок устарел, пожалуйста, повторите команду!', show_alert=True)
        else:
            result = await func(callback, callback_data)
            return result
    return wrapper

