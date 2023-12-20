from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup, \
    KeyboardButton, InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup
# from lexicon.lexicon_btns import *


class SoundsCallbackFactory(CallbackData, prefix='a'):
    name_sound: str
    topic: str


def keyboard_build(lexicon: dict) -> ReplyKeyboardMarkup:
    """
    создает калавиатуру
    :return: ReplyKeyboardMarkup
    """
    # инициализируем объект билдера
    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()

    # делаем список из кнопок
    keys = list(lexicon.keys())
    buttons = [KeyboardButton(text=lexicon[key]) for key in keys]

    # методом билдера добавляем в него кнопки (список списков) и формируем клавиатуру
    return kb_builder.row(*buttons, width=2).as_markup(resize_keyboard=True)


def inline_keyboard_build(lexicon: list, width: int) -> InlineKeyboardMarkup:
    """
    создает инлайн-клавиатуру
    :return: InlineKeyboardMarkup
    """
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    buttons = [InlineKeyboardButton(text=i, callback_data=i) for i in lexicon]
    return kb_builder.row(*buttons, width=width).as_markup()



def inline_pagination_keyboard_build(topic: str, audiolist: list, index: int):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons = [InlineKeyboardButton(text=i, callback_data=SoundsCallbackFactory(name_sound=i, topic=topic).pack()) for i in audiolist[index]]
    kb_builder.row(*buttons, width=1)
    kb_builder.row(
        InlineKeyboardButton(text='<<', callback_data='back'),
        InlineKeyboardButton(text=f'{index+1}/{len(audiolist)}', callback_data='pass'),
        InlineKeyboardButton(text='>>', callback_data='forward')
    )
    return kb_builder.as_markup()



if __name__ == '__main__':
    lst = [['What the hell you to doing?', 'That turns me on', "That's amazing", 'Thank you sir', 'Sswallow my cu#',
      'Suction', 'Stick your finger in my ass', 'Oh yes sir'],
     ["Oh shit i'm sorry", 'Oh my shoulder', 'Lets suck some dick', "It's so fucking dee", "It's bondage",
      "It's a loan", 'I dont do anal', 'Cu##ing'],
     ['Mmmm', 'Fuck you leather man!', 'Fuck you', 'Fuck you!', 'Fucking slaves get your ass back here',
      'Fisting is 300$', 'Dungeon master', 'Do you like what you see?'],
     ['Deep dark fantasies', 'Boy next door', 'Boss in this gym', 'Attention!', 'Ass we can']]

    inline_pagination_keyboard_build(lst, 0)
