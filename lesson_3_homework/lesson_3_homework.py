import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
from pprint import pprint


class HeadHunterMongoDB:
    def __init__(self):
        self.env_path = '.env'
        self.path_head_hunter_data = 'vacancies_info.json'
        self.my_connection_string = self.get_connection_string()
        self.db_name = 'head_hunter_database'
        self.db = self.connection_to_db()
        self.collection_name = 'deta_enginner_collection'#input('Введите название коллекции с которой хотите работать: ')
        self.collection = self.connection_to_collection()


    def get_connection_string(self):
        load_dotenv(self.env_path)
        string = 'CONNECTION_STRING'
        my_connection_string = os.getenv(string)
        return my_connection_string

    # 1.1 Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB.
    # connection on MongoDB Atlas --> on database --> on collection
    def connection_to_db(self):
        client = MongoClient(self.my_connection_string)
        my_db = client[self.db_name]
        return my_db

    def connection_to_collection(self):
        collection = self.db.get_collection(self.collection_name)
        return collection

    # 1.2 Реализовать функцию, записывающую собранные вакансии в созданную БД
    # add data from json to mongoDB
    def from_json_to_mongo(self):
        with open(self.path_head_hunter_data, 'r', encoding='utf8') as f:
            file_data = json.load(f)
            self.collection.insert_many(file_data)
            print('Вставка произошла успешно')

    # 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой  больше введённой
    # суммы.
    def get_vacancies_by_wealth_more(self):
        wealth = int(input('сколько хотите зарабатывать? (Число: '))
        for document in self.collection.find({"Минимальная зарплата": {"$gt": wealth}}):
            pprint(document)

    # 3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.
    def update_collection(self):
        matched_count = 0
        upserted_id_count = 0
        with open(self.path_head_hunter_data, 'r', encoding='utf8') as f:
            file_data = json.load(f)
            for document in file_data:
                logs = self.collection.update_one(document, {"$set": document}, upsert=True)
                if logs.matched_count != 0:
                    matched_count = matched_count + 1
                if logs.upserted_id is not None:
                    upserted_id_count = upserted_id_count + 1
        print(f'Документы, которые уже есть в базе: {matched_count} \n ')
        print(f'Количество документов, добавленных в базу: {upserted_id_count}')


# homework = HeadHunterMongoDB()
# homework.from_json_to_mongo()
# homework.get_vacancies_by_wealth_more()
# homework.update_collection()