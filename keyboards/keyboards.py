from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup, \
    KeyboardButton, InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup
from db_logic import get_number_of_collection, get_number_of_topic, get_collection_by_number, get_id_by_audio, \
    get_dict_audios


class SoundsCallbackFactory(CallbackData, prefix='a'):
    collection: str
    topic: str = '0'
    id_sound: str = '0'


class FavourSoundsCallbackFactory(CallbackData, prefix='f'):
    collection: str
    topic: str
    id_sound: str


class DelSoundsCallbackFactory(CallbackData, prefix='d'):
    collection: str
    topic: str
    id_sound: str



def keyboard_build(lexicon: dict) -> ReplyKeyboardMarkup:
    """
    Создает обычную калавиатуру
    :param lexicon: dict
    :return: ReplyKeyboardMarkup
    """
    # инициализируем объект билдера
    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    # делаем список из кнопок
    keys = list(lexicon.keys())
    buttons = [KeyboardButton(text=lexicon[key]) for key in keys]
    # методом билдера добавляем в него кнопки (список списков) и формируем клавиатуру
    return kb_builder.row(*buttons, width=2).as_markup(resize_keyboard=True)


async def inline_collections_keyboard_build(lexicon: list, width: int) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для коллекций
    :param lexicon: list
    :param width: int - количество кнопок на одной строке
    :return: InlineKeyboardMarkup
    """
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons = []
    for i in lexicon:
        # создаем кнопки, callback.data которых формируется из номеров коллекций, взятых из БД
        item = InlineKeyboardButton(
            text=i,
            callback_data=SoundsCallbackFactory(collection=await get_number_of_collection(i)).pack())
        buttons.append(item)

    return kb_builder.row(*buttons, width=width).as_markup()


async def inline_pagination_topics_keyboard_build(topic_list: list[list],
                                            num_collect,
                                            width: int,
                                            index: int) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для тем
    :param topic_list: list - список списов тем (страницы с темами)
    :param num_collect: str - номер коллекции
    :param width: int - количество кнопок на одной строке
    :param index: int - индекс списка темы из общего списка (страницы)
    :return: InlineKeyboardMarkup
    """
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # получаем название коллекции по ее номеру (взятого из callback.data предыдущего апдейта)
    collect = await get_collection_by_number(num_collect)
    buttons = []
    for i in topic_list[index]:
        # создаем кнопки, callback.data которых формируется из номера коллекции, номера темы
        item = InlineKeyboardButton(
            text=i,
            callback_data=SoundsCallbackFactory(
                collection=num_collect,
                topic=await get_number_of_topic(
                    collect=collect,
                    topic=i
                )
            ).pack()
        )
        buttons.append(item)

    kb_builder.row(*buttons, width=width)
    # создаем и добавляем кнопки пагинации
    kb_builder.row(
        InlineKeyboardButton(
            text='<<',
            callback_data=SoundsCallbackFactory(collection=num_collect, topic='back_topic_list').pack()
        ),
        # эта кнопка только информирует о текущей странице и общем количестве страниц
        # номер страницы - индекс списка + 1
        InlineKeyboardButton(
            text=f'{index + 1}/{len(topic_list)}',
            callback_data='pass'),
        InlineKeyboardButton(
            text='>>',
            callback_data=SoundsCallbackFactory(collection=num_collect, topic='forward_topic_list').pack()
        )
    )
    kb_builder.row(
        InlineKeyboardButton(
            text='⬅️ Назад',
            callback_data='back_to_collection_menu')
    )
    return kb_builder.as_markup()


async def inline_pagination_soundlist_keyboard_build(num_collect: str,
                                               num_topic: str,
                                               pages_of_audiolist: list[list],
                                               index: int) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для списка аудио
    :param num_collect:
    :param num_topic:
    :param pages_of_audiolist:
    :param index:
    :return:
    """
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons = []
    # создаем кнопки, callback.data которых формируется из номера коллекции, номера темы, id аудио
    for i in pages_of_audiolist[index]:
        id_sound = await get_id_by_audio(num_collect, num_topic, i)
        item = InlineKeyboardButton(
            text=i,
            callback_data=SoundsCallbackFactory(collection=num_collect, topic=num_topic, id_sound=str(id_sound)).pack()
        )
        buttons.append(item)

    kb_builder.row(*buttons, width=1)
    # создаем и добавляем кнопки пагинации
    kb_builder.row(
        InlineKeyboardButton(
            text='<<',
            callback_data=SoundsCallbackFactory(collection=num_collect, topic=num_topic, id_sound='back').pack()
        ),
        InlineKeyboardButton(
            text=f'{index+1}/{len(pages_of_audiolist)}',
            callback_data='pass'),
        InlineKeyboardButton(
            text='>>',
            callback_data=SoundsCallbackFactory(collection=num_collect, topic=num_topic, id_sound='forward').pack()
        )
    )
    kb_builder.row(
        InlineKeyboardButton(text='⬅️ Назад', callback_data='back_to_topic_menu')
    )
    return kb_builder.as_markup()



async def inline_pagination_favorite_soundlist_keyboard_build(buttons_dict_list: list[dict],
                                                        index: int) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для избранного списка аудио
    :param buttons_dict_list: list[dict]
    :param index: int
    :return:
    """
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons = []

    # создаем кнопки, callback.data которых формируется из номера коллекции, номера темы, id аудио
    for key, value in buttons_dict_list[index].items():
        key_lst = key.split(':')
        item = InlineKeyboardButton(
            text=value,
            callback_data=SoundsCallbackFactory(collection=key_lst[1], topic=key_lst[2], id_sound=key_lst[3]).pack())
        buttons.append(item)

    kb_builder.row(*buttons, width=1)
    # создаем и добавляем кнопки пагинации
    kb_builder.row(
        InlineKeyboardButton(text='<<', callback_data='favorite_audio_list_back'),
        InlineKeyboardButton(text=f'{index+1}/{len(buttons_dict_list)}', callback_data='pass'),
        InlineKeyboardButton(text='>>', callback_data='favorite_audio_list_forward')
    )
    kb_builder.row(
        InlineKeyboardButton(text='✏️ Редактировать список', callback_data='edit_favorite_audio_list')
    )
    return kb_builder.as_markup()




async def inline_pagination_favor_soundlist_delition_keyboard_build(buttons_dict_list: list[dict],
                                                        index: int) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для удаления элементов из избранного списка аудио
    :param buttons_dict_list: list[dict]
    :param index: int
    :return:
    """
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons = []

    # создаем кнопки, callback.data которых формируется из номера коллекции, номера темы, id аудио
    for key, value in buttons_dict_list[index].items():
        key_lst = key.split(':')
        item = InlineKeyboardButton(
            text=f'❌ Удалить {value}',
            callback_data=DelSoundsCallbackFactory(collection=key_lst[1], topic=key_lst[2], id_sound=key_lst[3]).pack())
        buttons.append(item)

    kb_builder.row(*buttons, width=1)
    # создаем и добавляем кнопки пагинации
    kb_builder.row(
        InlineKeyboardButton(text='<<', callback_data='del_audio_list_back'),
        InlineKeyboardButton(text=f'{index+1}/{len(buttons_dict_list)}', callback_data='pass'),
        InlineKeyboardButton(text='>>', callback_data='del_audio_list_forward')
    )
    kb_builder.row(
        InlineKeyboardButton(text='🔙 Отменить редактирование', callback_data='cancel_edit_favor_audio_list')
    )
    return kb_builder.as_markup()


if __name__ == '__main__':
    pass
