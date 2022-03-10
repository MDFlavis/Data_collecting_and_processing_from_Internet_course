'''
Написать приложение(используя lxml, нельзя использовать BeautifulSoup),
которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex news
Для парсинга использовать xpath. Структура данных должна содержать:

1.название источника(mail и яндекс не источники, а аггрегаторы, см. страницу новости),
2.наименование новости,
3.ссылку на новость,
4.дата публикации

Сложить все новости в БД, новости должны обновляться, т.е. используйте update.

Архитектура:
класс парсер 
    функция инит
        инициализация подключения к БД
        ссылки xpath
        header
        список с собранными данными
    
    функция для получения токена подключения к БД
    
    функция для подключения к БД и коллекции 'News'
        
    функция для добавления данных в монгоДБ
    
    функция для получения кода с сайта
    
    функция для мейл ру
    
    функция для ленты
    
    функция для яндекса  
    
    функция для запуска парсера
            функция для мейл ру
            функция для ленты
            функция для яндекса
            функция для записи в данных в БД
            закрытие клиента БД
    
    
'''
import os
import requests
import time
from lxml import html
from pymongo import MongoClient
from dotenv import load_dotenv


class NewsParser:
    import os
    import requests
    import time
    from lxml import html
    from pymongo import MongoClient
    from dotenv import load_dotenv

    def __init__(self):
        self.env_path = '.env'
        self.my_connection_string = self.get_connection_string()
        self.client = MongoClient(self.my_connection_string)
        self.db_name = 'News_database'
        self.collection_name = 'News'
        self.db_collection = self.connection_to_db_and_collection()


        self.header = {'User-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/98.0.4758.102 Safari/537.36'}

        self.mail_ru_main_url = 'https://news.mail.ru/'
        self.mail_ru_news_container = "//ul[contains(@class, 'list_type_square list_half')]/li[@class='list__item']"
        self.mail_ru_news_name = "//ul[contains(@class, 'list_type_square list_half')]/li[@class='list__item']/a/text()"
        self.mail_ru_news_url = "//ul[contains(@class, 'list_type_square list_half')]/li[@class='list__item']/a/@href"

        self.lenta_main_url = 'https://lenta.ru/'
        self.lenta_news_container = "//div[contains(@class, 'last24') and ./a]/a"
        self.lenta_news_name = "//div[contains(@class, 'last24') and ./a]/a/div[contains(@class, 'text')]/span/text()"
        self.lenta_news_url = "//div[contains(@class, 'last24') and ./a]/a/@href"

        self.yandex_news_main_url = 'https://yandex.ru/news'
        self.yandex_news_container = "//div[contains(@class, 'news-top-flexible-stories')]/div"
        self.yandex_news_name = "//div[contains(@class, 'news-top-flexible-stories')]/div//a[contains(@class, " \
                                "'card__link')]/text()"
        self.yandex_news_url = "//div[contains(@class, 'news-top-flexible-stories')]/div//a[contains(@class, " \
                               "'card__link')]/@href"
        self.yandex_news_source = "//div[contains(@class, 'news-top-flexible-stories')]//a[contains(@aria-label, \
                                   'Источник')]/text()"
        self.yandex_news_time = "//div[contains(@class, 'news-top-flexible-stories')]/div//span[contains(@class, " \
                                "'time')]/text()"
        self.news_data = []

    # get connection string from .env file to connection on the DB
    def get_connection_string(self):
        load_dotenv(self.env_path)
        string = 'CONNECTION_STRING'
        my_connection_string = os.getenv(string)
        return my_connection_string

    # connection to db and collection
    def connection_to_db_and_collection(self):
        my_db = self.client[self.db_name]
        collection = my_db.get_collection(self.collection_name)
        return collection

    # add data to DB
    def add_to_db(self):
        for news in self.news_data:
            self.db_collection.update_one(news, {"$set": news}, upsert=True)

    # news.mail.ru
    def get_root(self, main_url, news_container):
        response = requests.get(main_url, headers=self.header)
        root = html.fromstring(response.text)
        all_news = root.xpath(news_container)
        return all_news

    def get_news_mail_ru_data(self):
        news_counter = 0
        for news in self.get_root(self.mail_ru_main_url, self.mail_ru_news_container):
            info = dict()
            # get news url and title
            info['url'] = news.xpath(self.mail_ru_news_url)[news_counter]
            info['title'] = news.xpath(self.mail_ru_news_name)[news_counter]

            # get new request for source_link and news_datetime
            detail_response = requests.get(info['url'], headers=self.header)
            detail_response_root = html.fromstring(detail_response.text)

            # get news source_url and news_datetime
            info['source_url'] = detail_response_root.xpath("//a[contains(@class, 'link color_gray "
                                                            "breadcrumbs__link')]/@href")[0]
            info['news_datetime'] = detail_response_root.xpath("//span[contains(@class, 'note__text breadcrumbs__text "
                                                               "js-ago')]/@datetime")[0]
            self.news_data.append(info)
            time.sleep(1)
            news_counter += 1

    def get_lenta_data(self):
        news_counter = 0
        for news in self.get_root(self.lenta_main_url, self.lenta_news_container):
            info = dict()
            # get news url and title
            info['url'] = self.lenta_main_url + news.xpath(self.lenta_news_url)[news_counter]
            info['title'] = news.xpath(self.lenta_news_name)[news_counter]

            # get new request for source_link and news_datetime
            detail_response = requests.get(info['url'], headers=self.header)
            detail_response_root = html.fromstring(detail_response.text)

            # get news source_url and news_datetime
            info['source_url'] = self.lenta_main_url
            info['news_datetime'] = detail_response_root.xpath("//time[contains(@class, 'topic-header__time')]/text("
                                                               ")")[0]
            self.news_data.append(info)
            time.sleep(1)
            news_counter += 1

    def get_yandex_news_data(self):
        news_counter = 0
        for news in self.get_root(self.yandex_news_main_url, self.yandex_news_container):
            info = dict()
            # get news url and title
            info['url'] = news.xpath(self.yandex_news_url)[news_counter]
            info['title'] = news.xpath(self.yandex_news_name)[news_counter]

            # get news source_url and news_datetime
            info['source_url'] = news.xpath(self.yandex_news_source)[news_counter]
            info['news_datetime'] = news.xpath(self.yandex_news_time)[news_counter]
            self.news_data.append(info)
            time.sleep(1)
            news_counter += 1

    def start_parsing(self):
        self.get_news_mail_ru_data()
        self.get_lenta_data()
        self.get_yandex_news_data()
        self.add_to_db()
        self.client.close()



my_news = NewsParser()
my_news.start_parsing()

'''Как можно улучшить?
1. Есть много повторяющегося кода в функциях парсинга самих сайтов, у каждого сайта есть небольшие нюансы, но в целом, 
можно создать одну функцию, для всех трех, когда будет время.
2.Нужно больше документировать код.
'''
