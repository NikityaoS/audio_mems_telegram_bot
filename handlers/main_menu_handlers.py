from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from db.db_logic import add_user_to_db, mongo_db_sounds, get_callback_info_favorite_sound_list, get_dict_audios, \
    brake_dict_for_8_items_list
from lexicon.lexicon import *
from keyboards.keyboards import keyboard_build, inline_collections_keyboard_build, \
    inline_pagination_favorite_soundlist_keyboard_build

# Инициализируем роутер уровня модуля
router: Router = Router()


@router.message(CommandStart())
async def start_command(message: Message):
    await add_user_to_db(str(message.chat.id), message.from_user.username)
    await message.answer(
        text="👋",
        reply_markup=keyboard_build(MAIN_MENU_BUTTONS)
    )


@router.message(F.text == '🔊 Все аудио-мемы')
async def show_collections_list(message: Message):
    """
    Выводит меню со списком коллекций
    :param message: Message
    :return:
    """
    coll_names = await mongo_db_sounds.list_collection_names()
    markup = await inline_collections_keyboard_build(coll_names, width=1)
    await message.answer(text='🗂️ Выберите раздел', reply_markup=markup)


@router.message(F.text == '⭐ Избранное')
async def show_favorite_sounds_list(message: Message):
    """
    Выводит меню-список с названиями избранных аудиофайлов
    :param message: Message
    :return:
    """
    favorite_sound_list = await get_callback_info_favorite_sound_list(str(message.chat.id))

    if not favorite_sound_list:
        await message.answer(text='📋 Список избранного пуст! Добавьте аудио-стикер в избранное!')

    else:
        favor_dct = await get_dict_audios(favorite_sound_list)
        pages_dict_favor_audio = await brake_dict_for_8_items_list(favor_dct)
        markup = await inline_pagination_favorite_soundlist_keyboard_build(
            buttons_dict_list=pages_dict_favor_audio,
            index=0
        )
        if message:
            await message.answer(text=f'⭐ Избранное',
                                 reply_markup=markup)


@router.message(F.text == '📩 Для отзывов')
async def show_connect_message(message: Message):
    """
    Выводит сообщение со ссылкой на сообщение в канале
    :param message:
    :return:
    """
    button = InlineKeyboardButton(url='https://t.me/+9kGSXhtU20FhZDUy', text='🔗 Ссылка')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    await message.answer(text='💬 Переходите по ссылке и оставляйте комментарии!',
                         reply_markup=keyboard)


@router.message(F.text == '/help')
async def show_connect_message(message: Message):
    """
    Выводит сообщение со справочной информацией
    Присылает GIF-инструкцию
    :param message:
    :return:
    """
    await message.answer(text=f'{HELP_INFO}')
    placeholder = await message.answer(text="Загрузка GIF-инструкции..")
    await message.answer_animation(
        animation=FSInputFile("public/help.gif"),
        caption="GIF-инструкция по использованию"
    )
    await placeholder.delete()
