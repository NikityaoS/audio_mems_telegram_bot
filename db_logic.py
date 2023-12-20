import datetime
import pprint

import pymongo
from bson import ObjectId
from pymongo import MongoClient
from pprint import pprint

# connect to the MongoDB server
mongo_client = MongoClient()
mongo_db = mongo_client.sound_stickers


def get_description_topics(collection: str):
    """
    Возвращает список description из одной коллекции
    :param collection:
    :return: list
    """
    cursor_result = mongo_db[collection].find()
    list_of_doc = list(cursor_result)
    lst = []
    for i in list_of_doc:
        lst.append(i['description'])
    return list(set(lst))


def get_all_description_topics():
    """
    Возращает список description из всех коллекций
    :return: list
    """
    lst = []
    for collection in mongo_db.list_collection_names():
        topics = get_description_topics(collection)
        lst.extend(topics)
    return lst


def get_audiolist_of_topic(topic: str):
    """
    Возвращает список названий стикеров определенного описания (description)
    :param topic:
    :return: list
    """
    for collection in mongo_db.list_collection_names():
        topics = get_description_topics(collection)
        if topic in topics:
            cursor_result = mongo_db[collection].find({'description': topic})
            return [doc['sound'] for doc in list(cursor_result)]

def get_idlist_of_audio_of_topic(topic: str):
    """
    Возвращает список id стикеров определенного описания (description)
    :param topic:
    :return: list
    """
    for collection in mongo_db.list_collection_names():
        topics = get_description_topics(collection)
        if topic in topics:
            cursor_result = mongo_db[collection].find({'description': topic})
            return [doc['sound'] for doc in list(cursor_result)]


def get_all_names_of_audios():
    lst = []
    for topic in get_all_description_topics():
        lst.extend(get_audiolist_of_topic(topic))
    return lst


def brake_audiolist(audiolist: list):
    """
    Разбивает список названий аудио на подсписки максимум по 8 наименований
    и объединет их в один большой список
    :param audiolist:
    :return: list of lists
    """
    glob_list = []
    while audiolist:
        if len(audiolist) >= 8:
            sub_list = [audiolist.pop() for _ in range(8)]
            glob_list.append(sub_list)
        else:
            sub_list = [audiolist.pop() for _ in range(len(audiolist))]
            glob_list.append(sub_list)
    return glob_list


def get_filemane_of_sound(topic, sound):
    for collection in mongo_db.list_collection_names():
        topics = get_description_topics(collection)
        if topic in topics:
            cursor_result = mongo_db[collection].find({'description': topic, 'sound': sound})
            return list(cursor_result)[0]['file']



if __name__ == '__main__':
    pprint(mongo_db['мемы'].find_one({"_id": ObjectId('657f0a227f404accffbd867e')}))
