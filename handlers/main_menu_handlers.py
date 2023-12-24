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
