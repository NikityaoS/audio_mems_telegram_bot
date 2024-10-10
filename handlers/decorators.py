from aiogram.types import CallbackQuery, InlineQuery
from db.db_logic import get_callback_info_favorite_sound_list, get_dict_audios, brake_dict_for_8_items_list, \
    get_searched_audio_in_redis, get_all_audio_info, get_searched_audio_by_inline_query, \
    get_file_id_favour_audio_list_by_callbackinf


def check_get_favorite_audio_list_for_pagination(func):
    """
    Проверяет и подготавливает данные для клавиатуры
    при пагинации списка избранного.
    :param func:
    :return:
    """
    async def wrapper(callback: CallbackQuery):
        favorite_sound_list = await get_callback_info_favorite_sound_list(str(callback.message.chat.id))
        # если в списке нет аудио, то при его удалении присылается соответствующее сообщение без инлайн-кнопок
        if not favorite_sound_list:
            await callback.message.delete_reply_markup()
            await callback.message.edit_text(text='📋 Список избранного пуст! Добавьте аудио-стикер в избранное!')
        else:
            favor_dct = await get_dict_audios(favorite_sound_list)
            pages_dict_favor_audio = await brake_dict_for_8_items_list(favor_dct)
            # получаем строку предыдущего подсписка (страницы) в формате "3/10"
            str_pages = callback.message.reply_markup.inline_keyboard[-2][-2].text
            # получаем номер предыдущей страницы
            previous_page = int(str_pages.split('/')[0])

            result = await func(callback, pages_dict_favor_audio, previous_page)
            return result
    return wrapper


def check_get_searched_audio_list_for_pagination(func):
    """
    Проверяет и подготавливает данные для клавиатуры
    при пагинации списка аудио, сформированного по поиску.
    :param func:
    :return:
    """
    async def wrapper(callback: CallbackQuery):
        searched_sound_list = get_searched_audio_in_redis(user_id=str(callback.message.chat.id),
                                                          searched_word=callback.message.text)
        # если в списке нет аудио, то присылается соответствующее сообщение
        if not searched_sound_list:
            await callback.answer(text='⌛ Срок действия клавиатуры истек! Повторите команду!', show_alert=True)
        else:
            searched_dct = await get_dict_audios(list(searched_sound_list))
            pages_dict_favor_audio = await brake_dict_for_8_items_list(searched_dct)
            # получаем строку предыдущего подсписка (страницы) в формате "3/10"
            str_pages = callback.message.reply_markup.inline_keyboard[-1][-2].text
            # получаем номер предыдущей страницы
            previous_page = int(str_pages.split('/')[0])

            result = await func(callback, pages_dict_favor_audio, previous_page)
            return result
    return wrapper


def check_content_of_inlinequery(func):
    """
    Проверяет сообщение InlineQuery-объекта. Если None,
    то загружает список всех аудио, если * - загружает
    список избранных аудио пользователя, если какое-либо
    другое сообщение - ищет аудио с содержанием сообщения
    в названии аудио.
    :param func:
    :return:
    """
    async def wrapper(inline_query: InlineQuery):
        audio_lst = await get_all_audio_info()

        if not inline_query.query:
            result = await func(inline_query, audio_lst)
            return result
        elif inline_query.query == '*':
            favour_audio_lst = await get_file_id_favour_audio_list_by_callbackinf(str(inline_query.from_user.id))
            result = await func(inline_query, favour_audio_lst)
            return result
        else:
            audio_lst = await get_searched_audio_by_inline_query(inline_query.query, audio_lst)
            if audio_lst:
                result = await func(inline_query, audio_lst)
                return result
    return wrapper

