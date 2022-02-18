'''Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для
 конкретного пользователя, сохранить JSON-вывод в файле *.json; написать функцию,
 возвращающую(return) список репозиториев.'''

import requests
import json
from pprint import pprint


def repo_list(username):
    """
        Function for creation .json file with detail info about requested user repos
        and returning links on that
        :param username: str ; it is string which contains username whose repos you want to see
        :return: .json, list of repos links
        """

    # For GitHub request we need User-agent. In this task i use my own GitHub username
    headers = {'User-agent': 'MDFlavis'}

    req = requests.get(f'https://api.github.com/users/{username}/repos', headers=headers)

    data = json.loads(req.text)

    filename = 'task_1.json'
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

    repos_links_list = []
    for el in range(len(data)):
        repos_links_list.append(data[el]['clone_url'])

    return repos_links_list


my_func_result = repo_list('MDFlavis')

pprint(my_func_result)
