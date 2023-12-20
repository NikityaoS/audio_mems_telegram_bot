from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from lexicon.lexicon_buttons import *
from keyboards.keyboards import keyboard_build

# Инициализируем роутер уровня модуля
router: Router = Router()


@router.message(CommandStart(), StateFilter(default_state))
@router.message(F.text == 'Главное меню')
async def start_command(message: Message):

    await message.answer(text='Приветственный текст!!!!',
                         reply_markup=keyboard_build(MAIN_MENU_BUTTONS))
#
# @router.message(F.text == 'О нас', StateFilter(default_state))
# async def about_command(message: Message):
#     await message.answer(text=LEXICON_MS["about_us_message"],
#                          reply_markup=inline_keyboard_build(LEXICON_BTN_REFREN))
#
#
# @router.message(F.text == 'Услуги', StateFilter(default_state))
# async def services_command(message: Message):
#     await message.answer(text=LEXICON_MS["services_message"],
#                          reply_markup=inline_keyboard_build(LEXICON_BTN_SERVICES))
#
#
# @router.message(F.text == 'Кратко о стилях в дизайне интерьера', StateFilter(default_state))
# async def services_command(message: Message):
#     await message.answer_photo(photo=STYLES_DESIGN_INTERIOR['main_picture'],
#                                caption=LEXICON_MS["styles_of_design_interior"],
#                                reply_markup=inline_keyboard_build(LEXICON_BTN_STYLES_DESIGN_INTERIOR))
