import datetime
import pprint
import pymongo
from bson import ObjectId
from async_pymongo import AsyncClient
from pprint import pprint

# connect to the MongoDB server
mongo_client = AsyncClient()
mongo_db_sounds = mongo_client['sound_stickers']
mongo_db_num_info = mongo_client['number_for_info']
mongo_db_users_info = mongo_client['users']

async def get_list_of_topics(collection: str):
    """
    Возвращает список description из одной коллекции
    :param collection:
    :return: list
    """
    collect = mongo_db_sounds[collection]
    cursor_result = await collect.find()
    list_of_doc = list(cursor_result)
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
        topics = get_list_of_topics(collection)
        lst.extend(topics)
    return lst


def get_audiolist_of_topic(topic: str):
    """
    Возвращает список названий стикеров определенного описания (description)
    :param topic:
    :return: list
    """
    for collection in mongo_db_sounds.list_collection_names():
        topics = get_list_of_topics(collection)
        if topic in topics:
            cursor_result = mongo_db_sounds[collection].find({'description': topic})
            return [doc['sound'] for doc in list(cursor_result)]



def get_all_names_of_audios():
    lst = []
    for topic in get_all_topics_list():
        lst.extend(get_audiolist_of_topic(topic))
    return lst


def brake_list_for_8_items_list(lst: list):
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


def brake_dict_for_8_items_list(dct: dict):
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



    # glob_list = []
    #
    # if len(dct) >= 8:
    #     sub_dict = {}
    #     for key, value in dct.items():
    #         sub_dict.update({key: value})
    #         if len(sub_dict) == 8:
    #             break
    #     for key in sub_dict.keys():
    #         dct.pop(key)
    #     glob_list.append(sub_dict)
    # elif len(dct) == 0:
    #     return glob_list
    #
    # else:
    #     sub_dict = {}
    #     for key, value in dct.items():
    #         sub_dict.update({key: value})
    #
    #     for key in sub_dict.keys():
    #         dct.pop(key)
    #     glob_list.append(sub_dict)
    #
    #     return glob_list



def get_filename_of_sound(topic, sound):
    for collection in mongo_db_sounds.list_collection_names():
        topics = get_list_of_topics(collection)
        if topic in topics:
            cursor_result = mongo_db_sounds[collection].find({'description': topic, 'sound': sound})
            return list(cursor_result)[0]['file']


def get_number_of_collection(collection):
    result = await mongo_db_num_info['numbers_for_collections'].find({'specific': 'str to int'})
    return list(result)[0][collection]


def get_collection_by_number(num):
    result = mongo_db_num_info.numbers_for_collections.find({'specific': 'int to str'})
    return list(result)[0][num]


def get_number_of_topic(collect, topic):
    result = mongo_db_num_info.numbers_for_topics.find({'base': collect, 'specific': 'str to int'})
    return list(result)[0][topic]


def get_topic_by_number(collect, num):
    result = mongo_db_num_info.numbers_for_topics.find({'base': collect, 'specific': 'int to str'})
    return list(result)[0][num]


def get_audio_by_id(numb_collect, numb_topic, id):
    collect = get_collection_by_number(numb_collect)
    topic = get_topic_by_number(collect, numb_topic)
    result = mongo_db_sounds[collect].find({'description': topic, '_id': ObjectId(id)})
    return result[0]['sound']


def get_id_by_audio(numb_collect, numb_topic, audio_name):
    collect = get_collection_by_number(numb_collect)
    topic = get_topic_by_number(collect, numb_topic)
    result = mongo_db_sounds[collect].find({'description': topic, 'sound': audio_name})
    return str(result[0]['_id'])


def convert_collections_to_numbers():
    return [get_number_of_collection(collect) for collect in mongo_db_sounds.list_collection_names()]


def get_col_name_by_topic(topic):
    for collection in mongo_db_sounds.list_collection_names():
        topics = get_list_of_topics(collection)
        if topic in topics:
            return collection

def add_favorite_audio_to_list(user_id, audio):
    mongo_db_users_info.users_info.update_one(
        {"_id": user_id}, {"$push": {"favorites": audio}}
    )


def check_is_there_audio_in_favorlist(user_id, audio):
    result = mongo_db_users_info.users_info.find(
        {"_id": user_id, "favorites": audio}
    )
    for doc in result:
        return doc['_id']



def show_users_info():
    result = mongo_db_users_info.users_info.find()
    for i in list(result):
        print(i)


def get_callback_info_favorite_sound_list(user_id):
    cursor_result = mongo_db_users_info.users_info.find({'_id': user_id})
    for doc in cursor_result:
        return doc['favorites']




def get_dict_audios(lst):
    main_lst = [i.split(':') for i in lst]
    main_dict = {}
    for i in main_lst:
        audio_name = get_audio_by_id(i[1], i[2], i[3])
        joined = ':'.join(i)
        main_dict.update({joined: audio_name})
    return main_dict





if __name__ == '__main__':
    pass
    # lst = ['f:1:1:657f0a227f404accffbd8697', 'f:1:1:657f0a227f404accffbd8694',
    #        'f:1:1:657f0a227f404accffbd8692']
    # print(get_callback_info_favorite_sound_list('806012412'))
    # print(get_dict_audios(lst))
    # dct = get_dict_audios(get_callback_info_favorite_sound_list('806012412'))
    # print(dct)
    # print(brake_dict_for_8_items_list(dct))
    # print(get_callback_info_favorite_sound_list('806012412'))
