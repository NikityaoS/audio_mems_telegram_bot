from aiogram import Router, F
from aiogram.types import CallbackQuery
from handlers.decorators import check_get_favorite_audio_list_for_pagination
from keyboards.keyboards import inline_pagination_favorite_soundlist_keyboard_build, \
    inline_pagination_favor_soundlist_delition_keyboard_build, DelSoundsCallbackFactory
from db.db_logic import get_callback_info_favorite_sound_list, get_dict_audios, \
    brake_dict_for_8_items_list, delete_elem_from_favour_soundlist, get_audio_by_id

# Инициализируем роутер уровня модуля
router: Router = Router()




@router.callback_query(F.data == 'favorite_audio_list_forward')
@check_get_favorite_audio_list_for_pagination
async def get_next_page_favorite_sound_list(callback: CallbackQuery,
                                            pages_dict_favor_audio: list[dict],
                                            previous_page: int):
    """
    Выводит следующий список (страницу) с названиями избранных аудиофайлов
    :param callback: CallbackQuery
    :return:
    """
    # если количество страниц больше номера предыдущей страницы,
    # то переходим на следующую страницу
    if len(pages_dict_favor_audio) > previous_page:
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_favorite_soundlist_keyboard_build(
                buttons_dict_list=pages_dict_favor_audio,
                # номер страницы = индекс + 1
                # индексом текущей стр является номер предыдущей
                index=previous_page)
        )
    elif len(pages_dict_favor_audio) == 1:
        await callback.answer()
    else:
        # если количетсво страниц равно номеру предыдущей, то переходим в начало
        # т.е. к 0 индексу списка (странице 1)
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_favorite_soundlist_keyboard_build(
                buttons_dict_list=pages_dict_favor_audio,
                index=0)
        )


@router.callback_query(F.data == 'favorite_audio_list_back')
@check_get_favorite_audio_list_for_pagination
async def get_previous_page_favorite_sound_list(callback: CallbackQuery,
                                                pages_dict_favor_audio: list[dict],
                                                previous_page: int):
    """
    Выводит предыдущий список (страницу) с названиями избранных аудиофайлов
    :param callback: CallbackQuery
    :return:
    """
    # если количество страниц больше номера предыдущей страницы,
    # то переходим на следующую страницу
    if previous_page > 1:
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_favorite_soundlist_keyboard_build(
                buttons_dict_list=pages_dict_favor_audio,
                index=previous_page - 2)
        )

    elif len(pages_dict_favor_audio) == 1:
        await callback.answer()

    else:
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_favorite_soundlist_keyboard_build(
                buttons_dict_list=pages_dict_favor_audio,
                index=len(pages_dict_favor_audio) - 1)
        )


@router.callback_query(F.data == 'edit_favorite_audio_list')
async def get_favorite_sound_list_for_edit(callback: CallbackQuery):
    """
    Выводит список избранных аудио в режиме для удаления
    :param callback: CallbackQuery
    :return:
    """
    favorite_sound_list = await get_callback_info_favorite_sound_list(str(callback.message.chat.id))
    # если в списке нет аудио, то при его удалении присылается соответствующее сообщение без инлайн-кнопок
    if not favorite_sound_list:
        await callback.message.delete_reply_markup()
        await callback.message.edit_text(text='📋 Список избранного пуст! Добавьте аудио-стикер в избранное!')
    else:
        favor_dct = await get_dict_audios(favorite_sound_list)
        pages_dict_favor_audio = await brake_dict_for_8_items_list(favor_dct)

        markup = await inline_pagination_favor_soundlist_delition_keyboard_build(
            buttons_dict_list=pages_dict_favor_audio,
            index=0
        )
        await callback.message.edit_text(text=f'⭐ Избранное (режим удаления)')
        await callback.message.edit_reply_markup(reply_markup=markup)


@router.callback_query(F.data == 'del_audio_list_forward')
@check_get_favorite_audio_list_for_pagination
async def get_next_page_favor_soundlist_for_edit(callback: CallbackQuery,
                                                 pages_dict_favor_audio: list[dict],
                                                 previous_page: int):
    """
    Выводит следующий список (страницу) с названиями избранных аудиофайлов в режиме для
    удаления
    :param callback: CallbackQuery
    :return:
    """
    # если количество страниц больше номера предыдущей страницы,
    # то переходим на следующую страницу
    if len(pages_dict_favor_audio) > previous_page:
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_favor_soundlist_delition_keyboard_build(
                buttons_dict_list=pages_dict_favor_audio,
                # номер страницы = индекс + 1
                # индексом текущей стр является номер предыдущей
                index=previous_page)
        )

    elif len(pages_dict_favor_audio) == 1:
        await callback.answer()

    else:
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_favor_soundlist_delition_keyboard_build(
                buttons_dict_list=pages_dict_favor_audio,
                index=0)
        )


@router.callback_query(F.data == 'del_audio_list_back')
@check_get_favorite_audio_list_for_pagination
async def get_previous_page_favor_soundlist_for_edit(callback: CallbackQuery,
                                                     pages_dict_favor_audio: list[dict],
                                                     previous_page: int):
    """
    Выводит предыдущий список (страницу) с названиями избранных аудиофайлов в режиме
    для удаления
    :param callback: CallbackQuery
    :return:
    """
    # если количество страниц больше номера предыдущей страницы,
    # то переходим на следующую страницу
    if previous_page > 1:
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_favor_soundlist_delition_keyboard_build(
                buttons_dict_list=pages_dict_favor_audio,
                index=previous_page - 2)
        )

    elif len(pages_dict_favor_audio) == 1:
        await callback.answer()

    else:
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_favor_soundlist_delition_keyboard_build(
                buttons_dict_list=pages_dict_favor_audio,
                index=len(pages_dict_favor_audio) - 1)
        )


@router.callback_query(F.data == 'cancel_edit_favor_audio_list')
async def get_favorite_sounds_list(callback: CallbackQuery):
    """
    Выводит меню-список с названиями избранных аудиофайлов
    :param callback: CallbackQuery
    :return:
    """
    favorite_sound_list = await get_callback_info_favorite_sound_list(str(callback.message.chat.id))
    # если в списке нет аудио, то при его удалении присылается соответствующее сообщение без инлайн-кнопок
    if not favorite_sound_list:
        await callback.message.delete_reply_markup()
        await callback.message.edit_text(text='📋 Список избранного пуст! Добавьте аудио-стикер в избранное!')
    else:
        favor_dct = await get_dict_audios(favorite_sound_list)
        pages_dict_favor_audio = await brake_dict_for_8_items_list(favor_dct)

        markup = await inline_pagination_favorite_soundlist_keyboard_build(
            buttons_dict_list=pages_dict_favor_audio,
            index=0
        )
        await callback.message.edit_text(text=f'⭐ Избранное')
        await callback.message.edit_reply_markup(reply_markup=markup)


@router.callback_query(DelSoundsCallbackFactory.filter())
async def delete_element_from_favour_soundlist(callback: CallbackQuery,
                                               callback_data: DelSoundsCallbackFactory):
    """
    Удаляет аудио из списка избранного
    :param callback: CallbackQuery
    :param callback_data: DelSoundsCallbackFactory
    :return:
    """
    # меняем префикс с "d" на "f", так как в БД аудио записаны с "f" (favorite)
    callback_data.__prefix__ = 'f'
    # получаем список со строами идентефикаторов избранных аудио
    favorite_sound_list = await get_callback_info_favorite_sound_list(str(callback.message.chat.id))
    # если в списке 1 аудио, то при его удалении присылается соответствующее сообщение без инлайн-кнопок
    if len(favorite_sound_list) == 1:
        await delete_elem_from_favour_soundlist(str(callback.message.chat.id), callback_data.pack())
        await callback.message.delete_reply_markup()
        await callback.message.edit_text(text='📋 Список избранного пуст! Добавьте аудио-стикер в избранное!')
    # если в списке больше одного аудио, то оно удаляется из БД и из инлайн-клавиатуры
    # и формируется новая инлайн-клавиатура
    else:
        await delete_elem_from_favour_soundlist(str(callback.message.chat.id), callback_data.pack())
        favor_dct = await get_dict_audios(await get_callback_info_favorite_sound_list(str(callback.message.chat.id)))
        pages_dict_favor_audio = await brake_dict_for_8_items_list(favor_dct)

        markup = await inline_pagination_favor_soundlist_delition_keyboard_build(
            buttons_dict_list=pages_dict_favor_audio,
            index=0
        )

        await callback.message.edit_text(text=f'⭐ Избранное (режим удаления)')
        name_deleted_audio = await get_audio_by_id(callback_data.collection, callback_data.topic, callback_data.id_sound)
        await callback.answer(text=f'❌ Аудио "{name_deleted_audio}" удалено!', show_alert=True)
        await callback.message.edit_reply_markup(reply_markup=markup)
