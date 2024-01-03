from aiogram import Router, F
from keyboards.keyboards import inline_pagination_favorite_soundlist_keyboard_build, \
    inline_pagination_favor_soundlist_delition_keyboard_build, DelSoundsCallbackFactory
from db_logic import get_callback_info_favorite_sound_list, get_dict_audios, \
    brake_dict_for_8_items_list, delete_elem_from_favour_soundlist
from .decorators import *


# Инициализируем роутер уровня модуля
router: Router = Router()


@router.message(F.text == '⭐ Избранное')
@check_subscrib_to_channel_1param
async def show_favorite_sounds_list(message: Message):
    """
    Выводит меню-список с названиями избранных аудиофайлов
    :param message: Message
    :return:
    """
    await message.delete()
    favor_dct = await get_dict_audios(await get_callback_info_favorite_sound_list(str(message.chat.id)))
    pages_dict_favor_audio = await brake_dict_for_8_items_list(favor_dct)
    markup =await inline_pagination_favorite_soundlist_keyboard_build(
        buttons_dict_list=pages_dict_favor_audio,
        index=0
    )
    if message:
        await message.answer(text=f'⭐ Избранное',
                         reply_markup=markup)



@router.callback_query(F.data == 'favorite_audio_list_forward')
@check_subscrib_to_channel_1param
async def get_next_page_favorite_sound_list(callback: CallbackQuery):
    """
    Выводит следующий список (страницу) с названиями избранных аудиофайлов
    :param callback: CallbackQuery
    :return:
    """
    favor_dct = await get_dict_audios(await get_callback_info_favorite_sound_list(str(callback.message.chat.id)))
    pages_dict_favor_audio = await brake_dict_for_8_items_list(favor_dct)

    # получаем строку предыдущего подсписка (страницы) в формате "3/10"
    str_pages = callback.message.reply_markup.inline_keyboard[-2][-2].text
    # получаем номер предыдущей страницы
    previous_page = int(str_pages.split('/')[0])
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
@check_subscrib_to_channel_1param
async def get_previous_page_favorite_sound_list(callback: CallbackQuery):
    """
    Выводит предыдущий список (страницу) с названиями избранных аудиофайлов
    :param callback: CallbackQuery
    :return:
    """
    favor_dct = await get_dict_audios(await get_callback_info_favorite_sound_list(str(callback.message.chat.id)))
    pages_dict_favor_audio = await brake_dict_for_8_items_list(favor_dct)

    # получаем строку предыдущего подсписка (страницы) в формате "3/10"
    str_pages = callback.message.reply_markup.inline_keyboard[-2][-2].text
    # получаем номер предыдущей страницы
    previous_page = int(str_pages.split('/')[0])
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
    favor_dct = await get_dict_audios(await get_callback_info_favorite_sound_list(str(callback.message.chat.id)))
    pages_dict_favor_audio = await brake_dict_for_8_items_list(favor_dct)

    markup = await inline_pagination_favor_soundlist_delition_keyboard_build(
        buttons_dict_list=pages_dict_favor_audio,
        index=0
    )
    await callback.message.edit_text(text=f'⭐ Избранное (режим удаления)')
    await callback.message.edit_reply_markup(reply_markup=markup)




@router.callback_query(F.data == 'del_audio_list_forward')
async def get_next_page_favor_soundlist_for_edit(callback: CallbackQuery):
    """
    Выводит следующий список (страницу) с названиями избранных аудиофайлов в режиме для
    удаления
    :param callback: CallbackQuery
    :return:
    """
    favor_dct = await get_dict_audios(await get_callback_info_favorite_sound_list(str(callback.message.chat.id)))
    pages_dict_favor_audio = await brake_dict_for_8_items_list(favor_dct)

    # получаем строку предыдущего подсписка (страницы) в формате "3/10"
    str_pages = callback.message.reply_markup.inline_keyboard[-2][-2].text
    # получаем номер предыдущей страницы
    previous_page = int(str_pages.split('/')[0])
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
async def get_previous_page_favor_soundlist_for_edit(callback: CallbackQuery):
    """
    Выводит предыдущий список (страницу) с названиями избранных аудиофайлов в режиме
    для удаления
    :param callback: CallbackQuery
    :return:
    """
    favor_dct = await get_dict_audios(await get_callback_info_favorite_sound_list(str(callback.message.chat.id)))
    pages_dict_favor_audio = await brake_dict_for_8_items_list(favor_dct)

    # получаем строку предыдущего подсписка (страницы) в формате "3/10"
    str_pages = callback.message.reply_markup.inline_keyboard[-2][-2].text
    # получаем номер предыдущей страницы
    previous_page = int(str_pages.split('/')[0])
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
@check_subscrib_to_channel_1param
async def show_favorite_sounds_list(callback: CallbackQuery):
    """
    Выводит меню-список с названиями избранных аудиофайлов
    :param callback: CallbackQuery
    :return:
    """
    favor_dct = await get_dict_audios(await get_callback_info_favorite_sound_list(str(callback.message.chat.id)))
    pages_dict_favor_audio = await brake_dict_for_8_items_list(favor_dct)
    markup =await inline_pagination_favorite_soundlist_keyboard_build(
        buttons_dict_list=pages_dict_favor_audio,
        index=0
    )
    await callback.message.edit_text(text=f'⭐ Избранное')
    await callback.message.edit_reply_markup(reply_markup=markup)


@router.callback_query(DelSoundsCallbackFactory.filter())
async def delete_element_from_favour_soundlist(callback: CallbackQuery,
                                               callback_data: DelSoundsCallbackFactory):
    callback_data.__prefix__ = 'f'
    await delete_elem_from_favour_soundlist(str(callback.message.chat.id), callback_data.pack())

    favor_dct = await get_dict_audios(await get_callback_info_favorite_sound_list(str(callback.message.chat.id)))
    pages_dict_favor_audio = await brake_dict_for_8_items_list(favor_dct)

    markup = await inline_pagination_favor_soundlist_delition_keyboard_build(
        buttons_dict_list=pages_dict_favor_audio,
        index=0
    )
    await callback.message.edit_text(text=f'⭐ Избранное (режим удаления)')
    await callback.message.edit_reply_markup(reply_markup=markup)