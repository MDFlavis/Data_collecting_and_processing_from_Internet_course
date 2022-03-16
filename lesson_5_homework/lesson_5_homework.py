'''
Написать программу, которая собирает посты из группы https://vk.com/tokyofashion
Будьте внимательны к сайту!
Делайте задержки, не делайте частых запросов!

1) В программе должен быть ввод, который передается в поисковую строку по постам группы
2) Соберите данные постов:
- Дата поста
- Текст поста
- Ссылка на пост(полная)
- Ссылки на изображения(если они есть; необязательно)
- Количество лайков, "поделиться" и просмотров поста
3) Сохраните собранные данные в MongoDB
4) Скролльте страницу, чтобы получить больше постов(хотя бы 2-3 раза)
5) (Дополнительно, необязательно) Придумайте как можно скроллить "до конца" до тех пор пока посты не перестанут добавляться

Чем пользоваться?
Selenium, можно пользоваться lxml, BeautifulSoup
-----------------------------------------------------------------------------------------------------------------------
Архитектура:

класс Парсер:
    Функция инит*1:
        инициализация переменных: 1- ключевые слова для поиска, 2 - количество скроллов
        инициализация работы вебрайвера
        инициализация пустого списка для собираемых данных

    функция получения строки для подключения к БД

    функция подключения, обновления данных и закрытия БД

    функция открытия вебдрайвера(инициируется при создании экземпляра класса)

    функция поиска постов группы по ключевым словам

    функция, реализующая скролл/несколько скроллов/бесконечный скролл по странице в зависимости от парметров

    функция для получения всех интересующих нас постов

    функция запуска работы браузера*2
        функция поиска постов группы по ключевым словам
        функция, реализующая скролл/несколько скроллов/бесконечный скролл по странице в зависимости от парметров
        return функция для получения контейнера со всеми интересующими нас постами

    функция получения двнных скраппинга и добавление их в общий лист данных

    функция запуска скраппера
        функция получения двнных скраппинга и добавление их в общий лист данных
        функция подключения, обновления данных и закрытия БД


примечание *1 - в прошлой работе я засунул в инит очень много переменных, которые использовались 1 раз в 1 функции,
на этот раз я решил оставить в инициализирующей функции только те переменные, которые по-моему менению либо имеют
особую важность(настройки поиска, список с данными), либо используются в нескольких функциях. Это кажется мне
логичным, но не знаю, насколько это правильно. Все остальные переменные засунул в функции, в которых они используются.

примечание *2 - в целом, не уверен что эта функция нужна, изначально 3 функции которые она в себе содержит были
одной, но вы говорили, что лучше разгружать функции для удобства проверки, поэтому я разделил их на 3 и засунул в
"функция запуска работы браузера*1".
'''

import os
import time
from lxml import html
from pymongo import MongoClient
from dotenv import load_dotenv
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class TokyoFashion:
    def __init__(self):

        # init keywords for searching and scroll amounth
        self.numbers_of_scrolls = int(input('Введите число необходимых прокруток страницы(цифрой): '))
        self.search_words = str(input('Введите ключевые слова для поиска: '))

        # init browser
        self.driver = self.open_chrome()

        # init data
        self.post_data = []

    # get connection string from .env file to connection on the DB
    def get_connection_string(self):
        env_path = '.env'

        load_dotenv(env_path)
        string = 'CONNECTION_STRING'
        my_connection_string = os.getenv(string)
        return my_connection_string

    # connection to db and collection
    def add_to_db(self):
        my_connection_string = self.get_connection_string()
        client = MongoClient(my_connection_string)
        db_name = 'Tokyo_fashion'
        collection_name = 'posts'

        my_db = client[db_name]
        collection = my_db.get_collection(collection_name)
        for post in self.post_data:
            collection.update_one(post, {"$set": post}, upsert=True)
        client.close()

    def open_chrome(self):
        driver_path = 'chromedriver.exe'

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(driver_path)
        return driver

    def search(self):
        vk_url = 'https://vk.com/tokyofashion'
        self.driver.get(vk_url)
        time.sleep(1)

        # input posts name into search
        loupe = self.driver.find_element(By.XPATH, "//body/div[@id='page_wrap']//a[contains(@class, 'ui_tab_search')]")
        scroll_to_element = self.driver.find_element(By.XPATH, "//a[contains(text(),'tokyofashion.com')]")

        self.driver.execute_script("arguments[0].scrollIntoView();", scroll_to_element)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", loupe)
        time.sleep(1)

        input_element = self.driver.find_element(By.XPATH, "//input[@id='wall_search']")

        input_element.send_keys(self.search_words)
        input_element.send_keys(Keys.ENTER)

        time.sleep(5)

    def scroll(self):
        scroll_counter = 0
        scroll_pause_time = 0.5

        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while scroll_counter != self.numbers_of_scrolls:
            try:
                link = self.driver.find_element_by_link_text('Не сейчас')
                link.click()
            except Exception as e:
                # Scroll down to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Wait to load page
                time.sleep(scroll_pause_time)

                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                # для реализации бесконечного скролла нужно убрать строку ниже
                scroll_counter += 1

    def get_all_posts(self):
        post_container = "//div[@id='page_search_posts']/div"

        page_data = self.driver.page_source
        root = html.fromstring(page_data)
        all_posts = root.xpath(post_container)
        return all_posts

    def get_page_source(self):
        self.search()
        self.scroll()
        return self.get_all_posts()

    def get_data(self):
        all_posts = self.get_page_source()

        # Xpath
        post_time = "//div[contains(@id, 'page_search_posts')]//div[contains(@class, 'post_date')]//span/text()"
        post_likes = "//div[contains(@id, 'page_search_posts')]//div[contains(@class, 'PostBottomActionContainer')] " \
                     "//div[contains(@ data-section-ref, 'reactions-button-title')]/text()"

        post_share = "//div[contains(@id, 'page_search_posts')]//div[contains(@class, 'PostBottomAction')]/@data-count"
        post_views = "//div[contains(@id, 'page_search_posts')]//div[contains(@class, 'PostBottomAction')]//span[(" \
                     "@class='_views')]/text()"
        post_link = "//body//div[contains(@class, 'wall_posts')]/div//a[contains(@class, 'post_link')]/@href"
        post_text_path = "//div[contains(@id, 'page_search_posts')]/div//div[contains(@class, 'post_text')]"
        post_counter = 0

        for post in all_posts:
            post_info = {}

            post_info['post_time'] = post.xpath(post_time)[post_counter]
            post_info['post_link'] = 'https://vk.com/' + post.xpath(post_link)[post_counter]
            post_info['post_likes'] = post.xpath(post_likes)[post_counter]
            post_info['post_share'] = post.xpath(post_share)[post_counter]
            post_info['post_text'] = self.driver.find_elements(By.XPATH, post_text_path)[
                post_counter].get_attribute("innerText")
            try:
                post_info['post_views'] = post.xpath(post_views)[post_counter]
            except Exception as e:
                post_info['post_views'] = None

            self.post_data.append(post_info)
            post_counter += 1

        pprint(self.post_data)
        print('Постов добавлено: ', post_counter)

    def start_scrapping(self):
        self.get_data()
        self.add_to_db()


my_class = TokyoFashion()
my_class.start_scrapping()
