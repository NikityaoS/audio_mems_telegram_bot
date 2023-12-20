from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from lexicon.lexicon_buttons import *
from keyboards.keyboards import keyboard_build, inline_keyboard_build, \
    inline_pagination_keyboard_build, SoundsCallbackFactory
from db_logic import mongo_db, get_description_topics, get_all_description_topics, get_audiolist_of_topic, \
    brake_audiolist, get_all_names_of_audios, get_filemane_of_sound


# Инициализируем роутер уровня модуля
router: Router = Router()


@router.message(F.text == 'Все стикеры')
async def start_command(message: Message):
    await message.answer(text='Выберите раздел!!!!',
                         reply_markup=inline_keyboard_build(mongo_db.list_collection_names(),
                                                            width=1))


@router.callback_query(F.data.in_(mongo_db.list_collection_names()))
async def start_command(callback: CallbackQuery):
    await callback.message.edit_text(text=f'Это {callback.data}!!!!!')
    await callback.message.edit_reply_markup(
        reply_markup=inline_keyboard_build(get_description_topics(callback.data),
                                           width=1)
    )


@router.callback_query(F.data.in_(get_all_description_topics()))
async def start_command(callback: CallbackQuery):
    topic = callback.data
    pages_of_audiolist = brake_audiolist(get_audiolist_of_topic(topic))
    await callback.message.edit_text(text=f'{callback.data}')
    await callback.message.edit_reply_markup(
        reply_markup=inline_pagination_keyboard_build(topic=topic,
                                                      audiolist=pages_of_audiolist,
                                                      index=0)
    )


@router.callback_query(F.data == 'forward')
async def start_command(callback: CallbackQuery):
    topic = callback.message.text
    pages_of_audiolist = brake_audiolist(get_audiolist_of_topic(topic))
    previous_page = int(callback.message.reply_markup.inline_keyboard[-1][-2].text[0])
    if len(pages_of_audiolist) > previous_page:
        await callback.message.edit_reply_markup(
            reply_markup=inline_pagination_keyboard_build(topic=topic,
                                                          audiolist=pages_of_audiolist,
                                                          index=previous_page)
        )
    else:
        await callback.message.edit_reply_markup(
            reply_markup=inline_pagination_keyboard_build(topic=topic,
                                                          audiolist=pages_of_audiolist,
                                                          index=0)
        )



@router.callback_query(F.data == 'back')
async def start_command(callback: CallbackQuery):
    topic = callback.message.text
    pages_of_audiolist = brake_audiolist(get_audiolist_of_topic(topic))
    previous_page = int(callback.message.reply_markup.inline_keyboard[-1][-2].text[0])
    if previous_page > 1:
        await callback.message.edit_reply_markup(
            reply_markup=inline_pagination_keyboard_build(topic=topic,
                                                          audiolist=pages_of_audiolist,
                                                          index=previous_page-2)
        )
    else:
        await callback.message.edit_reply_markup(
            reply_markup=inline_pagination_keyboard_build(topic=topic,
                                                          audiolist=pages_of_audiolist,
                                                          index=len(pages_of_audiolist)-1)
        )


@router.callback_query(F.data == 'pass')
async def start_command(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(SoundsCallbackFactory.filter(F.name_sound.in_(get_all_names_of_audios())))
async def start_command(callback: CallbackQuery,
                        callback_data: SoundsCallbackFactory):
    topic = callback_data.topic
    name_sound = callback_data.name_sound
    file_name = get_filemane_of_sound(topic, name_sound)
    await callback.message.answer_audio(audio=FSInputFile(f'audio/{topic}/{file_name}'),
                                        title=f'{name_sound}',
                                        caption='https://t.me/exprrrrrrr_bot',
                                        performer=f'{topic}',
                                        thumbnail=FSInputFile(f'audio/{topic}/{topic}.jpeg'),
                                        reply_markup=inline_keyboard_build(['Добавить в избранное'], width=1))
    await callback.answer()










@router.callback_query()
async def start_command(callback: CallbackQuery):
    await callback.answer(callback.data)