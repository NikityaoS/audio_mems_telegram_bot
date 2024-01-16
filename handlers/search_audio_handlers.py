from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from handlers.decorators import check_get_searched_audio_list_for_pagination
from keyboards.keyboards import inline_pagination_searched_soundlist_keyboard_build, \
    SearchedSoundsPaginationCallbackFactory
from db_logic import get_dict_audios, brake_dict_for_8_items_list, get_callback_info_searched_audio_list, \
    set_searched_audio_in_redis

# Инициализируем роутер уровня модуля
router: Router = Router()


@router.message(~F.text.in_({'🔊 Все аудио-стикеры', '⭐ Избранное', '📩 Обратная связь'}))
async def show_searched_sounds_list(message: Message):
    """
    Выводит меню-список с найденными по поиску аудио
    :param message: Message
    :return:
    """
    searched_sound_list = await get_callback_info_searched_audio_list(message.text)

    if not searched_sound_list:
        await message.answer(text='😔 Аудио по вашему запросу не найдено!')
    else:
        searched_dct = await get_dict_audios(searched_sound_list)
        pages_dict_searched_audio = await brake_dict_for_8_items_list(searched_dct)

        set_searched_audio_in_redis(user_id=str(message.chat.id),
                                    searched_word=message.text,
                                    searched_audio_list=searched_sound_list)

        markup = await inline_pagination_searched_soundlist_keyboard_build(
            buttons_dict_list=pages_dict_searched_audio,
            index=0,
            searched_word=message.text,
            user_id=str(message.chat.id)
        )
        await message.answer(text=f'{message.text}',
                             reply_markup=markup)


@router.callback_query(SearchedSoundsPaginationCallbackFactory.filter(F.direction == 'forward'))
@check_get_searched_audio_list_for_pagination
async def get_next_page_searched_sound_list(callback: CallbackQuery,
                                            pages_dict_favor_audio: list[dict],
                                            previous_page: int):
    """
    Выводит следующий список (страницу) с найденными по поиску аудио
    :param callback: CallbackQuery
    :return:
    """

    # если количество страниц больше номера предыдущей страницы,
    # то переходим на следующую страницу
    if len(pages_dict_favor_audio) > previous_page:
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_searched_soundlist_keyboard_build(
                buttons_dict_list=pages_dict_favor_audio,
                # номер страницы = индекс + 1
                # индексом текущей стр является номер предыдущей
                index=previous_page,
                searched_word=callback.message.text,
                user_id=str(callback.message.chat.id)
            )
        )
    elif len(pages_dict_favor_audio) == 1:
        await callback.answer()
    else:
        # если количетсво страниц равно номеру предыдущей, то переходим в начало
        # т.е. к 0 индексу списка (странице 1)
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_searched_soundlist_keyboard_build(
                buttons_dict_list=pages_dict_favor_audio,
                index=0,
                searched_word=callback.message.text,
                user_id=str(callback.message.chat.id)
            )
        )


@router.callback_query(SearchedSoundsPaginationCallbackFactory.filter(F.direction == 'back'))
@check_get_searched_audio_list_for_pagination
async def get_previous_page_searched_sound_list(callback: CallbackQuery,
                                                pages_dict_favor_audio: list[dict],
                                                previous_page: int):
    """
    Выводит предыдущий список (страницу) с найденными по поиску аудио
    :param callback: CallbackQuery
    :return:
    """

    # если количество страниц больше номера предыдущей страницы,
    # то переходим на следующую страницу
    if previous_page > 1:
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_searched_soundlist_keyboard_build(
                buttons_dict_list=pages_dict_favor_audio,
                # номер страницы = индекс + 1
                # индексом текущей стр является номер предыдущей
                index=previous_page - 2,
                searched_word=callback.message.text,
                user_id=str(callback.message.chat.id)
            )
        )
    elif len(pages_dict_favor_audio) == 1:
        await callback.answer()
    else:
        # если количетсво страниц равно номеру предыдущей, то переходим в начало
        # т.е. к 0 индексу списка (странице 1)
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_searched_soundlist_keyboard_build(
                buttons_dict_list=pages_dict_favor_audio,
                index=len(pages_dict_favor_audio) - 1,
                searched_word=callback.message.text,
                user_id=str(callback.message.chat.id)
            )
        )
