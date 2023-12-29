from aiogram.exceptions import TelegramBadRequest
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, \
    InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.keyboards import inline_pagination_soundlist_keyboard_build, SoundsCallbackFactory, \
    inline_collections_keyboard_build, inline_pagination_topics_keyboard_build, FavourSoundsCallbackFactory, \
    inline_pagination_favorite_soundlist_keyboard_build
from db_logic import mongo_db_sounds, get_list_of_topics, get_audiolist_of_topic, \
    brake_list_for_8_items_list, get_filename_of_sound, get_collection_by_number, \
    get_topic_by_number, get_audio_by_id, get_col_name_by_topic, get_number_of_collection, add_favorite_audio_to_list, \
    check_is_there_audio_in_favorlist, get_callback_info_favorite_sound_list, get_dict_audios, \
    brake_dict_for_8_items_list

# Инициализируем роутер уровня модуля
router: Router = Router()

@router.message(F.text == 'Избранное')
# @check_subscrib_to_channel_2param
async def show_sounds_list(message: Message):
    """
    Выводит меню-список с названиями избранных аудиофайлов
    :param message: Message
    :return:
    """
    favor_dct = get_dict_audios(get_callback_info_favorite_sound_list(str(message.chat.id)))
    pages_dict_favor_audio = brake_dict_for_8_items_list(favor_dct)
    markup = inline_pagination_favorite_soundlist_keyboard_build(
        buttons_dict_list=pages_dict_favor_audio,
        index=0
    )
    await message.answer(text='Список избранных аудио',
                         reply_markup=markup)


