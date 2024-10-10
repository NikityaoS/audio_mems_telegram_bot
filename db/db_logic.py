import re
import asyncio
import redis
from datetime import datetime
from bson import ObjectId
from async_pymongo import AsyncClient
from config_data.config import load_config_db


config_db = load_config_db()

username = config_db.mongodb.user_name
password = config_db.mongodb.password
authSource = config_db.mongodb.db
authMechanism = config_db.mongodb.auth_mech

# соединение MongoDB сервером
mongo = AsyncClient(f'mongodb://{username}:{password}@mongo')
# mongo = AsyncClient()

mongo_db_sounds = mongo['sound_stickers']
mongo_db_num_info = mongo['number_for_info']
mongo_db_users_info = mongo['users']

r = redis.Redis(host='redis', port=6379, decode_responses=True)
# r = redis.Redis(decode_responses=True)

BLOCKING_LIST_SECONDS = [600, 10_800, 86_400, 259_200]


async def get_list_of_topics(collection: str):
    """
    Возвращает список description из одной коллекции
    :param collection:
    :return: list
    """
    collect = mongo_db_sounds[collection]
    cursor_result = collect.find()
    list_of_doc = await cursor_result.to_list()
    lst = []
    for i in list_of_doc:
        lst.append(i['description'])
    return list(set(lst))


async def get_all_topics_list():
    """
    Возращает список description из всех коллекций
    :return: list
    """
    lst = []
    for collection in await mongo_db_sounds.list_collection_names():
        topics = await get_list_of_topics(collection)
        lst.extend(topics)
    return lst


async def get_audiolist_of_topic(topic: str):
    """
    Возвращает список названий стикеров определенного описания (description)
    :param topic:
    :return: list
    """
    for collection in await mongo_db_sounds.list_collection_names():
        topics = await get_list_of_topics(collection)
        if topic in topics:
            cursor_result = mongo_db_sounds[collection].find({'description': topic})
            return [doc['sound'] for doc in await cursor_result.to_list()]


async def get_all_names_of_audios():
    lst = []
    for topic in await get_all_topics_list():
        lst.extend(await get_audiolist_of_topic(topic))
    return lst


async def brake_list_for_8_items_list(lst: list):
    """
    Разбивает список на подсписки максимум по 8 наименований
    и объединет их в один большой список
    :param lst:
    :return: list of lists
    """
    glob_list = []
    while lst:
        if len(lst) >= 8:
            sub_list = [lst.pop() for _ in range(8)]
            glob_list.append(sub_list)
        else:
            sub_list = [lst.pop() for _ in range(len(lst))]
            glob_list.append(sub_list)
    return glob_list


async def brake_dict_for_8_items_list(dct: dict):
    """
    Разбивает словарь на подсловари максимум по 8 наименований
    и объединет их в один большой список
    :param dct:
    :return:
    """
    keys_lst = [key for key in dct.keys()]

    glob_list = []
    while keys_lst:
        if len(keys_lst) >= 8:
            sub_dct = {}
            for _ in range(8):
                key = keys_lst.pop()
                sub_dct.update({key: dct[key]})
            glob_list.append(sub_dct)

        else:
            sub_dct = {}
            for _ in range(len(keys_lst)):
                key = keys_lst.pop()
                sub_dct.update({key: dct[key]})
            glob_list.append(sub_dct)

    return glob_list


async def get_filename_of_sound(topic, sound):
    """
    Получает название аудио по названию темы.
    :param topic:
    :param sound:
    :return:
    """
    for collection in await mongo_db_sounds.list_collection_names():
        topics = await get_list_of_topics(collection)
        if topic in topics:
            cursor_result = mongo_db_sounds[collection].find({'description': topic, 'sound': sound})
            result2 = await cursor_result.to_list()
            return result2[0]['file']


async def get_number_of_collection(collection):
    """
    Получает номер коллекции по названию
    :param collection:
    :return:
    """
    result = mongo_db_num_info['numbers_for_collections'].find({'specific': 'str to int'})
    result2 = await result.to_list()
    return result2[0][collection]


async def get_collection_by_number(num):
    """
    Получает название коллекции по номеру.
    :param num:
    :return:
    """
    result = mongo_db_num_info['numbers_for_collections'].find({'specific': 'int to str'})
    result2 = await result.to_list()
    return result2[0][num]


async def get_number_of_topic(collect, topic):
    """
    Получает номер темы по названию.
    :param collect:
    :param topic:
    :return:
    """
    result = mongo_db_num_info['numbers_for_topics'].find({'base': collect, 'specific': 'str to int'})
    result2 = await result.to_list()
    return result2[0][topic]


async def get_topic_by_number(collect, num):
    """
    Получает название темы по номеру
    :param collect:
    :param num:
    :return:
    """
    result = mongo_db_num_info['numbers_for_topics'].find({'base': collect, 'specific': 'int to str'})
    result2 = await result.to_list()
    return result2[0][num]


async def get_audio_by_id(numb_collect, numb_topic, id):
    """
    Получает название аудио по id.
    :param numb_collect:
    :param numb_topic:
    :param id:
    :return:
    """
    collect = await get_collection_by_number(numb_collect)
    topic = await get_topic_by_number(collect, numb_topic)
    result = mongo_db_sounds[collect].find({'description': topic, '_id': ObjectId(id)})
    result2 = await result.to_list()
    return result2[0]['sound']


async def get_id_by_audio(numb_collect, numb_topic, audio_name):
    """
    Получает id аудио.
    :param numb_collect:
    :param numb_topic:
    :param audio_name:
    :return:
    """
    collect = await get_collection_by_number(numb_collect)
    topic = await get_topic_by_number(collect, numb_topic)
    result = mongo_db_sounds[collect].find({'description': topic, 'sound': audio_name})
    result2 = await result.to_list()
    return result2[0]['_id']


async def convert_collections_to_numbers() -> list:
    """
    Переводит названия коллекций в цифры.
    :return:
    """
    return [get_number_of_collection(collect) for collect in await mongo_db_sounds.list_collection_names()]


async def get_col_name_by_topic(topic) -> str:
    """
    Получает название коллекции по названию темы
    :param topic:
    :return:
    """
    for collection in await mongo_db_sounds.list_collection_names():
        topics = await get_list_of_topics(collection)
        if topic in topics:
            return collection


async def add_favorite_audio_to_list(user_id: str, audio: str) -> None:
    """
    Добавляет аудио в списко избранного.
    :param user_id:
    :param audio:
    :return:
    """
    await mongo_db_users_info['users_info'].update_one(
        {"_id": user_id}, {"$push": {"favorites": audio}}
    )


async def check_is_there_audio_in_favorlist(user_id: str, audio: str) -> str:
    """
    Проверяет, существует ли аудио в списке
    избранного.
    :param user_id: user_id пользователя в телеграм и БД
    :param audio: аудио в виде callback_data
    :return: id аудио или None
    """
    result = mongo_db_users_info['users_info'].find(
        {"_id": user_id, "favorites": audio}
    )
    for doc in await result.to_list():
        return doc['_id']


async def get_callback_info_favorite_sound_list(user_id: str) -> list[str]:
    """
    Получает список избранных аудио в виде callback_data
    :param user_id: user_id пользователя в телеграм и БД
    :return: список избранных аудио
    """
    cursor_result = mongo_db_users_info['users_info'].find({'_id': user_id})
    for doc in await cursor_result.to_list():
        return doc['favorites']


async def get_dict_audios(lst: list) -> dict[str:str]:
    """
    Из списка аудио в виде callback_data формирует
    словарь, где ключ - callback_data, значение -
    название аудио.
    :param lst: список с аудио
    :return: словарь с аудио
    """
    # формируетм список со списками данных об аудио
    main_lst = [i.split(':') for i in lst]
    main_dict = {}
    for i in main_lst:
        audio_name = await get_audio_by_id(i[1], i[2], i[3])
        joined = ':'.join(i)
        main_dict.update({joined: audio_name})
    return main_dict


async def delete_elem_from_favour_soundlist(user_id: str, audio: str) -> None:
    """
    Удаляет аудио из списка избранного.
    :param user_id: user_id пользователя в телеграм и БД
    :param audio: аудио в формате callback_data
    :return:
    """
    await mongo_db_users_info['users_info'].update_one(
        {"_id": user_id}, {"$pull": {"favorites": audio}}
    )


async def add_user_to_db(user_id: str, user_name: str) -> None:
    """
    Добавляет пользователя в базу данных.
    :param user_id: user_id пользователя в телеграм
    :param user_name: user_name пользователя в телеграм
    :return:
    """
    # проверяем наличие пользователя в БД
    result = await mongo_db_users_info['users_info'].find_one({'_id': user_id})
    # если такого нет, то записываем его в БД
    if not result:
        await mongo_db_users_info['users_info'].insert_one(
            {"_id": user_id, "user_name": user_name,
             "start_date": datetime.now(), "favorites": [],
             "blocking_date": None, "blocking_period": None}
        )


async def get_callback_info_searched_audio_list(search_word: str) -> list[str]:
    """
    Осуществляет поиск аудио по подстроке в БД и выводит список
    аудио в виде callback_data.
    :param search_word: подсттрока, по которой осуществляется поиск
    :return: список аудио
    """
    collection_names = await mongo_db_sounds.list_collection_names()
    lst = []
    for collection_name in collection_names:
        collection = mongo_db_sounds[collection_name]
        # осущетсвляем поиск аудио по слову с помощью регулярного вырвжения
        results = collection.find({"sound": {"$regex": re.compile(rf"{search_word}", flags=re.IGNORECASE)}})
        # результат поиска формируетм в список аудио, которые записываются в формате: a:1:1:sfvmk3lkdf4lkmdbflnk4
        for result in await results.to_list():
            audio_info = f"a:{await get_number_of_collection(collection_name)}:" \
                         f"{await get_number_of_topic(collection_name, result['description'])}:" \
                         f"{str(result['_id'])}"

            lst.append(audio_info)
    return lst


def set_searched_audio_in_redis(user_id: str,
                                searched_word: str,
                                searched_audio_list: list[str]) -> None:
    """
    Записывает в оперативную память список аудио, сформированного
    по поиску. Запись в виде множества. Ключ записи формируется
    из user_id и поискового слова.
    :param user_id: user_id пользователя в телеграм и БД
    :param searched_word: слово-запрос для поиска
    :param searched_audio_list: список аудио
    :return:
    """
    r.sadd(f'{user_id}:{searched_word}', *searched_audio_list)
    r.expire(f'{user_id}:{searched_word}', 600)


def get_searched_audio_in_redis(user_id: str, searched_word: str) -> set[str]:
    """
    Считвает список аудио из оперативной памяти, сформированного по поиску.
    :param user_id: user_id пользователя в телеграм и БД - часть ключа записи в Redis
    :param searched_word: слово-запрос для поиска - часть ключа записи в Redis
    :return:
    """
    return r.smembers(f'{user_id}:{searched_word}')


def set_user_info_antiflood_in_redis(user_id: str) -> None:
    """
    Записывет в оперативную память данные о количестве
    сообщеинй, отправленных пользователем в течение 5 секунд.
    :param user_id: user_id пользователя в телеграм и БД
    :return:
    """
    r.incr(f'{user_id}:messages_count')
    r.expire(f'{user_id}:messages_count', 5)


def add_1_to_user_info_in_redis(user_id: str) -> None:
    """
    Добавляет 1 к счетчику сообщений пользователя.
    :param user_id: user_id пользователя в телеграм и БД
    :return:
    """
    r.incr(f'{user_id}:messages_count')


def get_user_info_antiflood_in_redis(user_id: str) -> int:
    """
    Получает из оперативной памяти текущее значение
    счетчика сообщений пользователя.
    :param user_id: user_id пользователя в телеграм и БД
    :return: текущее значение счетчика сообщений пользователя
    """
    return r.get(f'{user_id}:messages_count')


async def set_blocking_date_and_period(user_id: str) -> None:
    """
    Записывает в базу данных дату и период блокировки пользователя в секундах.
    :param user_id: user_id пользователя в телеграм и БД
    :return:
    """
    # осуществляем поиск в БД пользователя, которого нужно заблокировать
    cursor_result = await mongo_db_users_info['users_info'].find_one({'_id': user_id})
    blocking_period = None
    # если в поле blocking_period нет значения (блокировка первый раз), устанавливаем переменную в 600 сек
    if not cursor_result['blocking_period']:
        blocking_period = 600
    # если в поле blocking_period установлено значение 259_200, то в переменную передаем это же значение
    elif int(cursor_result['blocking_period']) == 259_200:
        blocking_period = int(cursor_result['blocking_period'])
    # если в поле другое значение, то берем следующее по списку BLOCKING_LIST_SECONDS
    else:
        for i in BLOCKING_LIST_SECONDS:
            if int(cursor_result['blocking_period']) < i:
                blocking_period = i
                break
    # обновляем значения полей blocking_date из текущей даты и blocking_period из переменной blocking_period
    await mongo_db_users_info['users_info'].update_one(
        {"_id": user_id}, {'$set': {"blocking_date": datetime.now(), "blocking_period": blocking_period}}
    )


async def get_blocking_date_and_period(user_id: str) -> tuple[datetime, int]:
    """
    Получает из базы данных дату и период блокировки.
    :param user_id:
    :return: tuple
    """
    cursor_result = await mongo_db_users_info['users_info'].find_one({'_id': user_id})
    return (cursor_result["blocking_date"], cursor_result["blocking_period"])


async def get_telegram_file_id(collection: str, id_sound: str) -> str:
    """
    Получает из БД telegram file_id для аудио.
    :param collection: название коллекции в БД
    :param id_sound: id аудио в БД
    :return:
    """
    cursor_result = await mongo_db_sounds[collection].find_one({'_id': ObjectId(id_sound)})
    return cursor_result['file_id']


async def set_telegram_file_id(file_id: str, file_unique_id: str, collection: str, id_sound: str) -> None:
    """
    Записывает telegram file_id в поле file_id документа БД.
    :param file_id: параметр файл-объекта в телеграмм
    :param file_unique_id: второй параметр файл-объекта в телеграмм
    :param collection: название коллекции в БД
    :param id_sound: id аудио в БД
    :return:
    """
    await mongo_db_sounds[collection].update_one(
        {"_id": ObjectId(id_sound)}, {'$set': {"file_id": file_id, "file_unique_id": file_unique_id}}
    )


async def get_all_audio_info() -> list[tuple[str, str, str]]:
    """
    Получает список всех аудио в БД
    :return: список кордежей с содержанием полей description, sound, file_id
    """
    lst = []
    # проходимся по всем коллекциям
    for collection in await mongo_db_sounds.list_collection_names():
        # получаем список всех аудио из коллекции
        cursor = mongo_db_sounds[collection].find({})
        cursor = cursor.to_list()
        # формируем список аудио, у котороых заполнено поле file_id
        for document in await cursor:
            if document['file_id']:
                inf_sound = (document['description'],
                             document['sound'],
                             document['file_id'])
                lst.append(inf_sound)
    return lst


async def get_searched_audio_by_inline_query(searched_word: str,
                                             lst: list[tuple[str, str, str]]) -> list[tuple[str, str, str]]:
    """
    Осуществляет поиск аудио, в названиях которых присутствует запрашиваемая подстрока.
    :param searched_word: запрашиваемая подстрока
    :param lst: список всех аудио, состоящий из кордежей с description,
    sound, file_id
    :return: список найденных аудио, состоящий из кордежей с description,
    sound, file_id
    """
    try:
        pattern = re.compile(rf"{searched_word}", flags=re.IGNORECASE)
    except re.error:
        print('Ошибка модуля re')
    else:
        new_lst = []
        for tup in lst:
            # осуществляем поиск по названию аудио, если есть, добавляем в новый список
            if re.search(pattern, tup[-2]):
                new_lst.append(tup)
        return new_lst


async def get_info_for_audio_for_inline_mode_answer(numb_collect: str,
                                                    numb_topic: str,
                                                    id: str) -> tuple[str, str, str]:
    """
    Получает данные об аудио для использования в ответе на inline-запрос.
    :param numb_collect: номер коллекции
    :param numb_topic: номер темы
    :param id: id аудио
    :return: кортеж данных аудио с description, sound, file_id
    """
    collect = await get_collection_by_number(numb_collect)
    topic = await get_topic_by_number(collect, numb_topic)
    result = mongo_db_sounds[collect].find({'description': topic, '_id': ObjectId(id)})
    result2 = await result.to_list()
    return result2[0]['description'], result2[0]['sound'], result2[0]['file_id']


async def get_file_id_favour_audio_list_by_callbackinf(user_id: str) -> list[tuple[str, str, str]]:
    """
    Получает список избранных аудио в формате (description, sound, file_id) из
    формата callback_data f:1:1:dfvn4nk34kj34vdkfvn67.
    :param user_id:
    :return:
    """
    # получаем спискок избранных аудио в формате f:1:1:dfvn4nk34kj34vdkfvn67
    favor_sonds_callback_lst = await get_callback_info_favorite_sound_list(user_id)
    if favor_sonds_callback_lst:
        result_lst = []
        for i in favor_sonds_callback_lst:
            splited_callback = i.split(':')
            # переделываем формат каждого аудио на (description, sound, file_id)
            sound_file_id = await get_info_for_audio_for_inline_mode_answer(splited_callback[1],
                                                                            splited_callback[2],
                                                                            splited_callback[3])
            # если у аудио есть file_id, т.е. если оно загружено на сервер телеграм
            if sound_file_id[-1]:
                result_lst.append(sound_file_id)
        return result_lst



async def main():
    lst = await get_all_audio_info()
    res = await get_searched_audio_by_inline_query('ху', lst)
    return res



if __name__ == '__main__':
    pass
