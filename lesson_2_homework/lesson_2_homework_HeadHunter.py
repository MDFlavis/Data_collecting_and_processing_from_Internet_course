import time
import requests
import json
from bs4 import BeautifulSoup



class HeadHunterScrapper:

    def __init__(self):
        self.headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                      'like Gecko) Chrome/98.0.4758.82 Safari/537.36'}
        self.page_counter = 0
        self.vacancy_to_find = self.vacancy_to_find()
        self.number_of_pages = self.number_of_pages_to_analyze()

    # Первоначальные переменные: вакансия, которую анализируем, количество страниц
    def vacancy_to_find(self):
        vacancy = str(input('Введите название интересующей вакансии: '))
        vacancy = vacancy.replace(' ', '-')
        return vacancy

    def number_of_pages_to_analyze(self):
        while True:
            try:
                num_pages = int(input('Введите количество анализируемых страниц: '))
            except Exception as e:
                print('Пожалуйста, введите количество анализируемых страниц, используя цифру')
                continue
            else:
                break
        return num_pages

    # Запрос , получение супа страницы, выделение из него блоков с вакансиями
    # TO DO : hh ВСЕ русские названия в ссылках пишет транскипцией, нужно будет продумать этот момент чтобы скрапер
    # обрабатывал и те вакансии, которые были введены на русском языке.Мб ввести автоматическую транслитерацию после
    # ввода искомой вакансии, вообще продумать всю логику этой функции. Она плохо работает, только с вакансиями
    # профессии, сключевыми словами(text=) не работает. СДЕЛАТЬ ЭТО КАК БУДЕТ ВРЕМЯ ОБЯЗАТЕЛЬНО
    def get_vacancies(self):
        info = requests.get(f'https://hh.ru/vacancies/{self.vacancy_to_find}?page='
                            f'{self.page_counter}&hhtmFrom=vacancy_search_catalog', headers=self.headers).text
        soup = BeautifulSoup(info, 'html.parser')
        vacancy_divs = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})
        return vacancy_divs

    #Метод для старта скрапера
    def start_scrapping(self):
        result_list = []
        while self.page_counter != self.number_of_pages:
            for vacancy in self.get_vacancies():
                result_list.append(self.get_result(vacancy))
            print(f'Со страницы {self.page_counter} было добавлено {len(self.get_vacancies())} обьявлений ')
            self.page_counter = self.page_counter + 1
            time.sleep(2)
            if len(self.get_vacancies()) == 0:
                print('Количество страниц, которое вы ввели превышает количество страниц, имеющихся на сайте.')
                break
        self.to_json(result_list)

    # Анализирует элемент vacancy_divs, возвращает result для 1 вакансии
    def get_result(self, element_from_vacancy_divs):
        vacancy_name_tag = element_from_vacancy_divs.find('a', attrs={'data-qa': "vacancy-serp__vacancy-title"})
        vacancy_name = vacancy_name_tag.get_text()
        vacancy_link = vacancy_name_tag.get('href')

        money_info_tag = element_from_vacancy_divs.find('span', attrs={'data-qa': "vacancy-serp__vacancy-compensation"})
        if money_info_tag is not None:
            # vacancy min and max salary, its currency
            salary = money_info_tag.get_text()
            salary = salary.split()

            if '–' in salary:
                div_index = salary.index('–')
                min_salary = int((''.join(salary[:div_index])))
                max_salary = int((''.join(salary[(div_index + 1):-1])))
            elif 'от' in salary:
                min_salary = int((''.join(salary[1:3])))
                max_salary = None
            elif 'до' in salary:
                min_salary = None
                max_salary = int((''.join(salary[1:3])))

            currency = salary[-1]
        else:
            min_salary = None
            max_salary = None
            currency = None

        result = {
            'Наименование вакансии': vacancy_name,
            'Ссылка на вакансию': vacancy_link,
            'Минимальная зарплата': min_salary,
            'Максимальная зарплата': max_salary,
            'Валюта': currency,
            'Сайт': 'https://hh.ru'
        }
        return result

    # Запись результатов в json файл в виде словарей
    def to_json(self, result):
        data = json.dumps(result, ensure_ascii=False)
        data = json.loads(data)
        with open('vacancies_info.json', 'a', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


scrapper = HeadHunterScrapper()
scrapper.start_scrapping()