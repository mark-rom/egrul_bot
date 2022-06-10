from exceptions import EGRULException
from time import sleep
from typing import Dict

import requests as r

from egrul import get_company_data, get_companys_token

FTS_URL = "https://egrul.nalog.ru/"
EXCTACTION_REQUEST_ENDPOINT = 'vyp-request/'
EXCTACTION_STATUS_ENDPOINT = 'vyp-status/'
EXCTACTION_DOWNLOAD_ENDPOINT = "vyp-download/"


def request_extraction(token: str) -> Dict:
    """Отправляет GET-запрос к API налоговой."""
    url = FTS_URL + EXCTACTION_REQUEST_ENDPOINT + token

    try:
        responce = r.get(url)
    except r.exceptions.RequestException:
        msg = f'Невозможно отправить запрос на {url}'
        raise EGRULException(msg)

    return responce.json()


def get_extraction_status(token: str) -> Dict:
    """Отправляет API запрос на формирование выписки ЕГРЮЛ."""
    url = FTS_URL + EXCTACTION_STATUS_ENDPOINT + token

    try:
        responce = r.get(url)
    except r.exceptions.RequestException:
        msg = f'Невозможно отправить запрос на {url}'
        raise EGRULException(msg)

    return responce.json()


def check_status(status_dict: Dict) -> bool:
    """Проверяет статус готовности выписки."""
    try:
        status = status_dict['status']
    except KeyError:
        msg = 'Список компаний не содержит ключа "status"'
        raise EGRULException(msg)
    return status == 'ready'


def get_download_link(status_dict: Dict, token: str) -> str:
    """Получает ссылку для скачивания выписки."""
    counter = 0
    while counter != 1:
        if not check_status(status_dict):
            sleep(0.1)
            counter += 1
        return FTS_URL + EXCTACTION_DOWNLOAD_ENDPOINT + token
    msg = 'ЕГРЮЛ не смог сформировать выписку'
    raise EGRULException(msg)


def get_extraction(query: int) -> str:
    """Получает ИНН/ОГРН, возвращает ссылку на скачиание pdf."""
    try:
        token_dict = get_companys_token(query)
        company_dict = get_company_data(token_dict["t"])

        token = company_dict["t"]
        request_extraction_dict = request_extraction(token)

        if not token == request_extraction_dict["t"]:
            token = request_extraction_dict["t"]

        status_dict = get_extraction_status(token)

        download_link = get_download_link(status_dict, token)

    except EGRULException as error:
        raise Exception(f'При формировании выписки произошла ошибка.\n{error}')

    except Exception as e:
        raise Exception(f'Во время работы программы произошла ошибка.\n{e}')

    return download_link


def main():
    print('Введите ИНН или ОГРН:')
    query = int(input())
    extraction_url = get_extraction(query)
    return print(extraction_url)


if __name__ == '__main__':
    main()
