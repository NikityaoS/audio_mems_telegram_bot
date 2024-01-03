import datetime
import pprint
import pymongo
import asyncio
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



async def get_filename_of_sound(topic, sound):
    for collection in await mongo_db_sounds.list_collection_names():
        topics = await get_list_of_topics(collection)
        if topic in topics:
            cursor_result = mongo_db_sounds[collection].find({'description': topic, 'sound': sound})
            result2 = await cursor_result.to_list()
            return result2[0]['file']


async def get_number_of_collection(collection):
    result = mongo_db_num_info['numbers_for_collections'].find({'specific': 'str to int'})
    result2 = await result.to_list()
    return result2[0][collection]


async def get_collection_by_number(num):
    result = mongo_db_num_info['numbers_for_collections'].find({'specific': 'int to str'})
    result2 = await result.to_list()
    return result2[0][num]


async def get_number_of_topic(collect, topic):
    result = mongo_db_num_info['numbers_for_topics'].find({'base': collect, 'specific': 'str to int'})
    result2 = await result.to_list()
    return result2[0][topic]


async def get_topic_by_number(collect, num):
    result = mongo_db_num_info['numbers_for_topics'].find({'base': collect, 'specific': 'int to str'})
    result2 = await result.to_list()
    return result2[0][num]


async def get_audio_by_id(numb_collect, numb_topic, id):
    collect = await get_collection_by_number(numb_collect)
    topic = await get_topic_by_number(collect, numb_topic)
    result = mongo_db_sounds[collect].find({'description': topic, '_id': ObjectId(id)})
    result2 = await result.to_list()
    return result2[0]['sound']


async def get_id_by_audio(numb_collect, numb_topic, audio_name):
    collect = await get_collection_by_number(numb_collect)
    topic = await get_topic_by_number(collect, numb_topic)
    result = mongo_db_sounds[collect].find({'description': topic, 'sound': audio_name})
    result2 = await result.to_list()
    return result2[0]['_id']


async def convert_collections_to_numbers():
    return [get_number_of_collection(collect) for collect in await mongo_db_sounds.list_collection_names()]


async def get_col_name_by_topic(topic):
    for collection in await mongo_db_sounds.list_collection_names():
        topics = await get_list_of_topics(collection)
        if topic in topics:
            return collection

async def add_favorite_audio_to_list(user_id, audio):
    await mongo_db_users_info['users_info'].update_one(
        {"_id": user_id}, {"$push": {"favorites": audio}}
    )


async def check_is_there_audio_in_favorlist(user_id, audio):
    result = mongo_db_users_info['users_info'].find(
        {"_id": user_id, "favorites": audio}
    )
    for doc in await result.to_list():
        return doc['_id']



async def show_users_info():
    result = mongo_db_users_info['users_info'].find()
    for i in await result.to_list():
        print(i)


async def get_callback_info_favorite_sound_list(user_id):
    cursor_result = mongo_db_users_info['users_info'].find({'_id': user_id})
    for doc in await cursor_result.to_list():
        return doc['favorites']




async def get_dict_audios(lst):
    main_lst = [i.split(':') for i in lst]
    main_dict = {}
    for i in main_lst:
        audio_name = await get_audio_by_id(i[1], i[2], i[3])
        joined = ':'.join(i)
        main_dict.update({joined: audio_name})
    return main_dict


async def delete_elem_from_favour_soundlist(user_id: str, audio: str):
    await mongo_db_users_info['users_info'].update_one(
        {"_id": user_id}, {"$pull": {"favorites": audio}}
    )



if __name__ == '__main__':
    res = asyncio.run(delete_elem_from_favour_soundlist('806012412', 'f:1:1:657f0a227f404accffbd8692'))
    print(res)
