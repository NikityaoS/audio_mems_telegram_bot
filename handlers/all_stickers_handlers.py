
from aiogram.exceptions import TelegramBadRequest
from main import bot
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, \
    InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.keyboards import inline_pagination_soundlist_keyboard_build, SoundsCallbackFactory, \
    inline_collections_keyboard_build, inline_pagination_topics_keyboard_build
from db_logic import mongo_db_sounds, get_list_of_topics, get_audiolist_of_topic, \
    brake_list_for_8_items_list, get_filename_of_sound, get_collection_by_number, \
    get_topic_by_number, get_audio_by_id, get_col_name_by_topic, get_number_of_collection

# Инициализируем роутер уровня модуля
router: Router = Router()


def check_subscrib_to_channel(func):
    """
    Декоратор. Проверяет, подписан ли пользователь на канал,
    если нет, то отправляет сообщение о подписке.
    :param func:
    :return:
    """
    async def wrapper(update):
        try:
            await bot.get_chat_member(chat_id=-1001992217206, user_id=0000000)
        except TelegramBadRequest:
            if isinstance(update, Message):
                await update.answer(text='Для доступа к боту подпишитесь на канал: CHANEL!!!!')
            else:
                await update.message.answer(text='Для доступа к боту подпишитесь на канал: CHANEL!!!!')
                await update.answer()
        else:
            result = await func(update)
            return result
    return wrapper


@router.message(F.text == 'Все стикеры')
@check_subscrib_to_channel
async def show_collections_list(message: Message):
    """
    Выводит меню со списком коллекций
    :param message: Message
    :return:
    """
    markup = inline_collections_keyboard_build(mongo_db_sounds.list_collection_names(), width=1)
    await message.answer(text='Выберите раздел!!!!', reply_markup=markup)


# Задаем фильтр на callback.data, созданный фабриокой, в частности,
# на его атрибуты topic, id_sound. Подразумевается, что аргумент
# collection непустой.
@router.callback_query(SoundsCallbackFactory.filter(F.topic == '0'),
                       SoundsCallbackFactory.filter(F.id_sound == '0'))
@check_subscrib_to_channel
async def show_topics_list(callback: CallbackQuery,
                           callback_data: SoundsCallbackFactory):
    """
    Выводит меню-список с темами аудиофайлов, находящихся в одной коллекции
    :param callback: CallbackQuery
    :param callback_data: SoundsCallbackFactory
    :return:
    """
    # получаем имя коллекции
    collect_name = get_collection_by_number(callback_data.collection)
    # разбиваем спискок тем из коллекции на подсписки (страницы) максимум по 8 элементов
    # и объединяем их в общий список
    pages_of_topiclist = brake_list_for_8_items_list(get_list_of_topics(collect_name))

    await callback.message.edit_text(text=f'Это {collect_name}!!!!!')
    await callback.message.edit_reply_markup(
        reply_markup=inline_pagination_topics_keyboard_build(topic_list=pages_of_topiclist,
                                                             num_collect=callback_data.collection,
                                                             width=1,
                                                             # получаем первый список в списке pages_of_audiolist
                                                             index=0)
)


# Задаем фильтр, также на атрибут класса-фабрики id_sound. Подразумевается,
# что атрибуты collection, topic заполнены.
@router.callback_query(SoundsCallbackFactory.filter(F.id_sound == '0'))
@check_subscrib_to_channel
async def show_sounds_list(callback: CallbackQuery,
                           callback_data: SoundsCallbackFactory):
    """
    Выводит меню-список с названиями аудиофайлов
    :param callback: CallbackQuery
    :param callback_data: SoundsCallbackFactory
    :return:
    """
    try:
        await bot.get_chat_member(chat_id=-1001992217206, user_id=0000000)
    except TelegramBadRequest:
        await callback.message.answer(text='Для доступа к боту подпишитесь на канал: CHANEL!!!!')
        await callback.answer()
    else:

        collect_name = get_collection_by_number(callback_data.collection)
        topic = get_topic_by_number(collect_name, callback_data.topic)
        pages_of_audiolist = brake_list_for_8_items_list(get_audiolist_of_topic(topic))

        await callback.message.edit_text(text=f'{topic}')
        await callback.message.edit_reply_markup(
            reply_markup=inline_pagination_soundlist_keyboard_build(num_collect=callback_data.collection,
                                                                    num_topic=callback_data.topic,
                                                                    pages_of_audiolist=pages_of_audiolist,
                                                                    # получаем первый список в списке pages_of_audiolist
                                                                    index=0)
        )


@router.callback_query(SoundsCallbackFactory.filter(F.id_sound == 'forward'))
@check_subscrib_to_channel
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
    pages_of_audiolist = brake_list_for_8_items_list(get_audiolist_of_topic(topic))
    # получаем строку предыдущего подсписка (страницы) в формате "3/10"
    str_pages = callback.message.reply_markup.inline_keyboard[-2][-2].text
    # получаем номер предыдущей страницы
    previous_page = int(str_pages.split('/')[0])
    # если количество страниц больше номера предыдущей страницы,
    # то переходим на следующую страницу
    if len(pages_of_audiolist) > previous_page:
        await callback.message.edit_reply_markup(
            reply_markup=inline_pagination_soundlist_keyboard_build(num_collect=callback_data.collection,
                                                                    num_topic=callback_data.topic,
                                                                    pages_of_audiolist=pages_of_audiolist,
                                                                    # номер страницы = индекс + 1
                                                                    # индексом текущей стр является номер предыдущей
                                                                    index=previous_page)
        )
    else:
        # если количетсво страниц равно номеру предыдущей, то переходим в начало
        # т.е. к 0 индексу списка (странице 1)
        await callback.message.edit_reply_markup(
            reply_markup=inline_pagination_soundlist_keyboard_build(num_collect=callback_data.collection,
                                                                    num_topic=callback_data.topic,
                                                                    pages_of_audiolist=pages_of_audiolist,
                                                                    index=0)
        )


@router.callback_query(SoundsCallbackFactory.filter(F.id_sound == 'back'))
@check_subscrib_to_channel
async def get_previous_page_sound_list(callback: CallbackQuery,
                                       callback_data: SoundsCallbackFactory):
    """
    Выводит предыдущий список (страницу) с названиями аудиофайлов
    :param callback: CallbackQuery
    :param callback_data: SoundsCallbackFactory
    :return:
    """
    topic = callback.message.text
    pages_of_audiolist = brake_list_for_8_items_list(get_audiolist_of_topic(topic))
    str_pages = callback.message.reply_markup.inline_keyboard[-2][-2].text
    previous_page = int(str_pages.split('/')[0])
    if previous_page > 1:
        await callback.message.edit_reply_markup(
            reply_markup=inline_pagination_soundlist_keyboard_build(num_collect=callback_data.collection,
                                                                    num_topic=callback_data.topic,
                                                                    pages_of_audiolist=pages_of_audiolist,
                                                                    index=previous_page - 2)
        )
    else:
        await callback.message.edit_reply_markup(
            reply_markup=inline_pagination_soundlist_keyboard_build(num_collect=callback_data.collection,
                                                                    num_topic=callback_data.topic,
                                                                    pages_of_audiolist=pages_of_audiolist,
                                                                    index=len(pages_of_audiolist) - 1)
        )


# отлавливает апдейт кнопи возврата к меню со списком коллекий (разделов)
@router.callback_query(F.data == 'back_to_collection_menu')
@check_subscrib_to_channel
async def back_to_collection_menu(callback: CallbackQuery):
    """
    Выводит инлайй-меню со списком коллекций
    при нажатии кнопки "Назад" в меню списка тем
    :param callback: CallbackQuery
    :return:
    """
    markup = inline_collections_keyboard_build(mongo_db_sounds.list_collection_names(), width=1)
    await callback.message.edit_text(text='Выберите Раздел!!!')
    await callback.message.edit_reply_markup(reply_markup=markup)


# отлавливает апдейт кнопи возврата к меню со списком тем
@router.callback_query(F.data == 'back_to_topic_menu')
@check_subscrib_to_channel
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
    collection_name = get_col_name_by_topic(topic)
    # формируем список списков (страниц) с темами коллекции
    pages_of_topiclist = brake_list_for_8_items_list(get_list_of_topics(collection_name))
    num_collect = get_number_of_collection(collection_name)
    await callback.message.edit_text(text=f'Это {collection_name}!!!!!')
    await callback.message.edit_reply_markup(reply_markup=inline_pagination_topics_keyboard_build(
                                                                    topic_list=pages_of_topiclist,
                                                                    num_collect=num_collect,
                                                                    width=1,
                                                                    # получаем первый список в списке pages_of_audiolist
                                                                    index=0))


# предполагается, в фильтр попает collback.data со всеми заполенными атрибутами
@router.callback_query(SoundsCallbackFactory.filter())
@check_subscrib_to_channel
async def get_audio_file(callback: CallbackQuery, callback_data: SoundsCallbackFactory):
    """
    Возвращает аудио-файл
    :param callback: CallbackQuery
    :param callback_data: SoundsCallbackFactory
    :return:
    """
    # по номеру коллекции из бд получаем имя коллекции
    collection = get_collection_by_number(callback_data.collection)
    # по номеру темы получаем имя темы
    topic = get_topic_by_number(collection, callback_data.topic)
    # по номерам коллекции, темы и id аудио получаем название аудио
    name_sound = get_audio_by_id(callback_data.collection,
                                 callback_data.topic,
                                 callback_data.id_sound)
    # по теме и названию аудио получаем название файла
    file_name = get_filename_of_sound(topic, name_sound)

    button = InlineKeyboardButton(text='Добавить в избранное', callback_data='set_to_favorites')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])

    await callback.message.answer_audio(audio=FSInputFile(f'audio/{topic}/{file_name}'),
                                        title=f'{name_sound}',
                                        caption='https://t.me/exprrrrrrr_bot',
                                        performer=f'{topic}',
                                        thumbnail=FSInputFile(f'audio/{topic}/{topic}.jpeg'),
                                        reply_markup=keyboard)
    await callback.answer()


# отлавливает апдейт инлайн-кнопки с номером и количеством страниц
@router.callback_query(F.data == 'pass')
async def skip_waiting_from_page_num_button(callback: CallbackQuery):
    await callback.answer()


# отлавливает остальные апдейты от инлайн-кнопок
@router.callback_query()
async def skip_waiting_from_inline_button(callback: CallbackQuery):
    await callback.answer()
