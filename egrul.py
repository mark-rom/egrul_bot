import datetime as dt
import json
import logging
import sys
from http import HTTPStatus
from logging.handlers import RotatingFileHandler

import requests as r

from exceptions import EGRULException

EGRUL_ENDPOINT = "https://egrul.nalog.ru/search-result/"
REQUEST_URL = "https://egrul.nalog.ru/"
HEADERS = {
    "Host": "egrul.nalog.ru",
    "Connection": "Close",
    "Content-Type": "application/json",
    "User-Agent": "python-requests/2.27.1"
}


logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
handler = RotatingFileHandler(sys.stdout)
handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


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
        logger.error(msg)
        raise EGRULException(msg)

    if response.status_code != HTTPStatus.OK:
        msg = f'Сайт "{REQUEST_URL}" недоступен, код: {response.status_code}'
        logger.error(msg)
        raise EGRULException(msg)
    return response.json()


def get_information(company_token: str):
    """Отправляет GET-запрос к API и возвращает словарь с данными компании."""
    url = EGRUL_ENDPOINT + company_token

    try:
        response = r.get(url)
    except r.exceptions.RequestException:
        msg = f'Невозможно отправить запрос на {url}'
        logger.error(msg)
        raise EGRULException(msg)

    try:
        rows_list = response.json().get("rows")
    except KeyError:
        msg = 'Список компаний не содержит ключа "rows"'
        logger.error(msg)
        raise EGRULException(msg)
    return rows_list[0]


def chech_expire(company_dict):
    """Проверяет исключено ли лицо из ЕГРЮЛ."""
    try:
        expire_date = company_dict["e"]
        return f'Регистрация прекращена {expire_date}'
    except KeyError:
        date = dt.datetime.now().date().strftime('%d.%m.%Y')
        return f'Действует на {date}'


def parse_individual(company_dict):
    name = company_dict["n"].title()
    inn = company_dict["i"]
    ogrn = company_dict["o"]

    return (
        f'ИП: {name}\n'
        f'ИНН: {inn}\n'
        f'ОГРНИП: {ogrn}\n'
    )


def parse_company(company_dict):
    company_name = company_dict["c"]
    ceo = company_dict["g"].title()
    inn = company_dict["i"]
    ogrn = company_dict["o"]
    kpp = company_dict["p"]
    address = company_dict["a"].title()

    return (
        f'Компания: {company_name}\n'
        f'{ceo}\n'
        f'ИНН: {inn}\n'
        f'ОГРН: {ogrn}\n'
        f'КПП: {kpp}\n'
        f'Адрес: {address}\n'
    )


def parse_information(company_dict) -> str:
    """Получает словарь с данными компании.
    Возвращает название, ЕИО, ОГРН, ИНН, КПП и адрес компании.
    Либо возвращает имя, ИНН и ОГРНИП индивидуального предпринимателя.
    """
    if company_dict["k"] == "fl":
        return parse_individual(company_dict)
    return parse_company(company_dict)


def parse_egrul(query) -> str:
    """Получает на вход ИНН или ОГРН и возвращает информацию о компании.
    """
    try:
        token_dict = get_company_token(query)
        company_dict = get_information(token_dict["t"])
        expire = chech_expire(company_dict)
        inf = parse_information(company_dict)
    except EGRULException as error:
        return print(f'Во время работы программы произошла ошибка {error}')

    return f'{inf}\n{expire}'


def main():
    query = int(input())
    information = parse_egrul(query)
    return print(information)


if __name__ == '__main__':
    main()
