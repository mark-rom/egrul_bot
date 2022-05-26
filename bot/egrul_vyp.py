import datetime as dt
import json
from exceptions import EGRULException
from http import HTTPStatus

import requests as r

from logger import logger as log

EGRUL_ENDPOINT = "https://egrul.nalog.ru/search-result/"
REQUEST_URL = "https://egrul.nalog.ru/"
# ссылка для скачивания выписки ЕГРЮЛ
# нужно добавить токен из словаря с инфой о компании и что-то еще сделать(
DOWNLOAD_URL = "https://egrul.nalog.ru/vyp-download/"
HEADERS = {
    "Host": "egrul.nalog.ru",
    "Connection": "Close",
    "Content-Type": "application/json",
    "User-Agent": "python-requests/2.27.1"
}


def get_company_token(query: int):
    """Отправляет запрос с ИНН/ОГРН из инпута.
    Возвращает словарь с токеном организации.
    """
    # проверка, что query это int
    payload = json.dumps({
        "vyp3CaptchaToken": "",
        "page": "",
        "query": query,
        "region": ""
    })
    try:
        response = r.post(REQUEST_URL, data=payload, headers=HEADERS)
    except r.exceptions.RequestException:
        msg = f'Невозможно отправить запрос на {REQUEST_URL}'
        log.error(msg)
        raise EGRULException(msg)

    if response.status_code != HTTPStatus.OK:
        msg = f'Сайт "{REQUEST_URL}" недоступен, код: {response.status_code}'
        log.error(msg)
        raise EGRULException(msg)
    return response.json()
