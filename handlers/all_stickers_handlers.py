
from .decorators import *
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, \
    InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.keyboards import inline_pagination_soundlist_keyboard_build, SoundsCallbackFactory, \
    inline_collections_keyboard_build, inline_pagination_topics_keyboard_build, FavourSoundsCallbackFactory
from db_logic import mongo_db_sounds, get_list_of_topics, get_audiolist_of_topic, \
    brake_list_for_8_items_list, get_filename_of_sound, get_collection_by_number, \
    get_topic_by_number, get_audio_by_id, get_col_name_by_topic, get_number_of_collection, add_favorite_audio_to_list, \
    check_is_there_audio_in_favorlist

# Инициализируем роутер уровня модуля
router: Router = Router()




@router.message(F.text == '🎵 Все аудио-стикеры')
@check_subscrib_to_channel_1param
async def show_collections_list(message: Message):
    """
    Выводит меню со списком коллекций
    :param message: Message
    :return:
    """
    await message.delete()
    coll_names = await mongo_db_sounds.list_collection_names()
    markup = await inline_collections_keyboard_build(coll_names, width=1)
    await message.answer(text='👇 Выберите раздел', reply_markup=markup)


# Задаем фильтр на callback.data, созданный фабриокой, в частности,
# на его атрибуты topic, id_sound. Подразумевается, что аргумент
# collection непустой.
@router.callback_query(SoundsCallbackFactory.filter(F.topic == '0'),
                       SoundsCallbackFactory.filter(F.id_sound == '0'))
@check_subscrib_to_channel_2param
async def show_topics_list(callback: CallbackQuery,
                           callback_data: SoundsCallbackFactory):
    """
    Выводит меню-список с темами аудиофайлов, находящихся в одной коллекции
    :param callback: CallbackQuery
    :param callback_data: SoundsCallbackFactory
    :return:
    """
    # получаем имя коллекции
    collect_name = await get_collection_by_number(callback_data.collection)
    # разбиваем спискок тем из коллекции на подсписки (страницы) максимум по 8 элементов
    # и объединяем их в общий список
    pages_of_topiclist = await brake_list_for_8_items_list(await get_list_of_topics(collect_name))

    await callback.message.edit_text(text=f'{collect_name}')
    await callback.message.edit_reply_markup(
        reply_markup=await inline_pagination_topics_keyboard_build(
            topic_list=pages_of_topiclist,
            num_collect=callback_data.collection,
            width=1,
            # получаем первый список в списке pages_of_audiolist
            index=0)
)


@router.callback_query(SoundsCallbackFactory.filter(F.topic == 'forward_topic_list'))
@check_subscrib_to_channel_2param
async def get_next_page_topic_list(callback: CallbackQuery,
                                   callback_data: SoundsCallbackFactory):
    # получаем имя коллекции
    collect_name = await get_collection_by_number(callback_data.collection)
    # разбиваем спискок тем из коллекции на подсписки (страницы) максимум по 8 элементов
    # и объединяем их в общий список
    pages_of_topiclist = await brake_list_for_8_items_list(await get_list_of_topics(collect_name))

    # получаем строку предыдущего подсписка (страницы) в формате "3/10"
    str_pages = callback.message.reply_markup.inline_keyboard[-2][-2].text
    # получаем номер предыдущей страницы
    previous_page = int(str_pages.split('/')[0])

    if len(pages_of_topiclist) > previous_page:
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_topics_keyboard_build(
                topic_list=pages_of_topiclist,
                num_collect=callback_data.collection,
                width=1,
                # получаем первый список в списке pages_of_audiolist
                index=previous_page)
        )

    elif len(pages_of_topiclist) == 1:
        await callback.answer()

    else:
        # если количетсво страниц равно номеру предыдущей, то переходим в начало
        # т.е. к 0 индексу списка (странице 1)
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_topics_keyboard_build(
                topic_list=pages_of_topiclist,
                num_collect=callback_data.collection,
                width=1,
                index=0)
        )


@router.callback_query(SoundsCallbackFactory.filter(F.topic == 'back_topic_list'))
@check_subscrib_to_channel_2param
async def get_previous_page_topic_list(callback: CallbackQuery,
                                   callback_data: SoundsCallbackFactory):
    # получаем имя коллекции
    collect_name = await get_collection_by_number(callback_data.collection)
    # разбиваем спискок тем из коллекции на подсписки (страницы) максимум по 8 элементов
    # и объединяем их в общий список
    pages_of_topiclist = await brake_list_for_8_items_list(await get_list_of_topics(collect_name))

    # получаем строку предыдущего подсписка (страницы) в формате "3/10"
    str_pages = callback.message.reply_markup.inline_keyboard[-2][-2].text
    # получаем номер предыдущей страницы
    previous_page = int(str_pages.split('/')[0])

    if previous_page > 1:
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_topics_keyboard_build(
                topic_list=pages_of_topiclist,
                num_collect=callback_data.collection,
                width=1,
                # получаем первый список в списке pages_of_audiolist
                index=previous_page - 2)
        )

    elif len(pages_of_topiclist) == 1:
        await callback.answer()

    else:
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_topics_keyboard_build(
                topic_list=pages_of_topiclist,
                num_collect=callback_data.collection,
                width=1,
                index=len(pages_of_topiclist) - 1)
        )



# Задаем фильтр, также на атрибут класса-фабрики id_sound. Подразумевается,
# что атрибуты collection, topic заполнены.
@router.callback_query(SoundsCallbackFactory.filter(F.id_sound == '0'))
@check_subscrib_to_channel_2param
async def show_sounds_list(callback: CallbackQuery,
                           callback_data: SoundsCallbackFactory):
    """
    Выводит меню-список с названиями аудиофайлов
    :param callback: CallbackQuery
    :param callback_data: SoundsCallbackFactory
    :return:
    """
    collect_name = await get_collection_by_number(callback_data.collection)
    topic = await get_topic_by_number(collect_name, callback_data.topic)
    pages_of_audiolist = await brake_list_for_8_items_list(await get_audiolist_of_topic(topic))

    await callback.message.edit_text(text=f'{topic}')
    await callback.message.edit_reply_markup(
        reply_markup=await inline_pagination_soundlist_keyboard_build(
            num_collect=callback_data.collection,
            num_topic=callback_data.topic,
            pages_of_audiolist=pages_of_audiolist,
            # получаем первый список в списке pages_of_audiolist
            index=0)
    )


@router.callback_query(SoundsCallbackFactory.filter(F.id_sound == 'forward'))
@check_subscrib_to_channel_2param
@check_date_pagination_btn_2param
async def get_next_page_sound_list(callback: CallbackQuery,
                                   callback_data: SoundsCallbackFactory):
    """
    Выводит следующий список (страницу) с названиями аудиофайлов
    :param callback: CallbackQuery
    :param callback_data: SoundsCallbackFactory
    :return:
    """
    # получаем название темы из текста сообщения
    topic = callback.message.text
    # разбиваем список названий аудио одной темы на подсписки (страницы)
    pages_of_audiolist = await brake_list_for_8_items_list(await get_audiolist_of_topic(topic))
    # получаем строку предыдущего подсписка (страницы) в формате "3/10"
    str_pages = callback.message.reply_markup.inline_keyboard[-2][-2].text
    # получаем номер предыдущей страницы
    previous_page = int(str_pages.split('/')[0])
    # если количество страниц больше номера предыдущей страницы,
    # то переходим на следующую страницу
    if len(pages_of_audiolist) > previous_page:
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_soundlist_keyboard_build(
                num_collect=callback_data.collection,
                num_topic=callback_data.topic,
                pages_of_audiolist=pages_of_audiolist,
                # номер страницы = индекс + 1
                # индексом текущей стр является номер предыдущей
                index=previous_page)
        )

    elif len(pages_of_audiolist) == 1:
        await callback.answer()

    else:
        # если количетсво страниц равно номеру предыдущей, то переходим в начало
        # т.е. к 0 индексу списка (странице 1)
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_soundlist_keyboard_build(
                num_collect=callback_data.collection,
                num_topic=callback_data.topic,
                pages_of_audiolist=pages_of_audiolist,
                index=0)
        )

@router.callback_query(SoundsCallbackFactory.filter(F.id_sound == 'back'))
@check_subscrib_to_channel_2param
@check_date_pagination_btn_2param
async def get_previous_page_sound_list(callback: CallbackQuery,
                                       callback_data: SoundsCallbackFactory):
    """
    Выводит предыдущий список (страницу) с названиями аудиофайлов
    :param callback: CallbackQuery
    :param callback_data: SoundsCallbackFactory
    :return:
    """
    topic = callback.message.text
    pages_of_audiolist = await brake_list_for_8_items_list(await get_audiolist_of_topic(topic))
    str_pages = callback.message.reply_markup.inline_keyboard[-2][-2].text
    previous_page = int(str_pages.split('/')[0])
    if previous_page > 1:
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_soundlist_keyboard_build(
                num_collect=callback_data.collection,
                num_topic=callback_data.topic,
                pages_of_audiolist=pages_of_audiolist,
                index=previous_page - 2)
        )

    elif len(pages_of_audiolist) == 1:
        await callback.answer()

    else:
        await callback.message.edit_reply_markup(
            reply_markup=await inline_pagination_soundlist_keyboard_build(
                num_collect=callback_data.collection,
                num_topic=callback_data.topic,
                pages_of_audiolist=pages_of_audiolist,
                index=len(pages_of_audiolist) - 1)
        )


# отлавливает апдейт кнопи возврата к меню со списком коллекций (разделов)
@router.callback_query(F.data == 'back_to_collection_menu')
@check_subscrib_to_channel_1param
async def back_to_collection_menu(callback: CallbackQuery):
    """
    Выводит инлайй-меню со списком коллекций
    при нажатии кнопки "Назад" в меню списка тем
    :param callback: CallbackQuery
    :return:
    """
    markup = await inline_collections_keyboard_build(await mongo_db_sounds.list_collection_names(), width=1)
    await callback.message.edit_text(text='📌 Выберите раздел')
    await callback.message.edit_reply_markup(reply_markup=markup)


# отлавливает апдейт кнопки возврата к меню со списком тем
@router.callback_query(F.data == 'back_to_topic_menu')
@check_subscrib_to_channel_1param
async def back_to_topic_menu(callback: CallbackQuery):
    """
    Выводит инлайй-меню со списком тем коллекции
    при нажатии кнопки "Назад" в меню с аудио
    :param callback: CallbackQuery
    :return:
    """
    # получаем название темы из текста сообщения
    topic = callback.message.text
    # получаем название коллекции по названию темы
    collection_name = await get_col_name_by_topic(topic)
    # формируем список списков (страниц) с темами коллекции
    pages_of_topiclist = await brake_list_for_8_items_list(await get_list_of_topics(collection_name))
    num_collect = await get_number_of_collection(collection_name)
    await callback.message.edit_text(text=f'{collection_name}')
    await callback.message.edit_reply_markup(
        reply_markup=await inline_pagination_topics_keyboard_build(
            topic_list=pages_of_topiclist,
            num_collect=num_collect,
            width=1,
            # получаем первый список в списке pages_of_audiolist
            index=0)
    )


# предполагается, в фильтр попает collback.data со всеми заполенными атрибутами
@router.callback_query(SoundsCallbackFactory.filter())
@check_subscrib_to_channel_2param
async def get_audio_file(callback: CallbackQuery, callback_data: SoundsCallbackFactory):
    """
    Возвращает аудио-файл
    :param callback: CallbackQuery
    :param callback_data: SoundsCallbackFactory
    :return:
    """
    # по номеру коллекции из бд получаем имя коллекции
    collection = await get_collection_by_number(callback_data.collection)
    # по номеру темы получаем имя темы
    topic = await get_topic_by_number(collection, callback_data.topic)
    # по номерам коллекции, темы и id аудио получаем название аудио
    name_sound = await get_audio_by_id(callback_data.collection,
                                         callback_data.topic,
                                         callback_data.id_sound)
    # по теме и названию аудио получаем название файла
    file_name = await get_filename_of_sound(topic, name_sound)

    button = InlineKeyboardButton(
        text='➕ Добавить в избранное',
        callback_data=FavourSoundsCallbackFactory(
            collection=callback_data.collection,
            topic=callback_data.topic,
            id_sound=callback_data.id_sound
                                  ).pack()
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])

    await callback.message.answer_audio(
        audio=FSInputFile(f'audio/{topic}/{file_name}'),
        title=f'{name_sound}',
        caption='https://t.me/exprrrrrrr_bot',
        performer=f'{topic}',
        thumbnail=FSInputFile(f'audio/{topic}/{topic}.jpeg'),
        reply_markup=keyboard)
    await callback.answer()


@router.callback_query(FavourSoundsCallbackFactory.filter())
async def set_audio_to_favorites_list(callback: CallbackQuery,
                                       callback_data: FavourSoundsCallbackFactory):
    result = await check_is_there_audio_in_favorlist(str(callback.message.chat.id),
                                      callback_data.pack())
    if result:
        await callback.answer('😉 Аудио уже есть в списке избранного!', show_alert=True)
    else:
        await add_favorite_audio_to_list(str(callback.message.chat.id),
                                   callback_data.pack())
        await callback.answer('✅ Аудио добавлено в избранное!', show_alert=True)


# отлавливает апдейт инлайн-кнопки с номером и количеством страниц
@router.callback_query(F.data == 'pass')
async def skip_waiting_from_page_num_button(callback: CallbackQuery):
    await callback.answer()


# отлавливает остальные апдейты от инлайн-кнопок
# @router.callback_query()
# async def skip_waiting_from_inline_button(callback: CallbackQuery):
#     await callback.answer()
#     print(callback.data)