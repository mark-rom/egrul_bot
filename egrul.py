import datetime as dt
import json
import logging
import sys
from exceptions import EGRULException
from http import HTTPStatus
from logging import StreamHandler
from typing import Callable, Dict

import requests as r

FTS_URL = 'https://egrul.nalog.ru/'
SEARCH_ENDPOINT = 'search-result/'
HEADERS = {
    "Host": "egrul.nalog.ru",
    "Connection": "Close",
    "Content-Type": "application/json",
    "User-Agent": "python-requests/2.27.1"
}


logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
handler = StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def get_companys_token(query: int) -> Dict:
    """Отправляет POST-запрос с ИНН/ОГРН.
    Возвращает словарь с токеном организации."""
    payload = json.dumps({
        "vyp3CaptchaToken": "",
        "page": "",
        "query": query,
        "region": ""
    })

    try:
        response = r.post(FTS_URL, data=payload, headers=HEADERS)
    except r.exceptions.RequestException:
        msg = f'Невозможно отправить запрос на {FTS_URL}'
        raise EGRULException(msg)

    if response.status_code != HTTPStatus.OK:
        msg = f'Сайт "{FTS_URL}" недоступен, код: {response.status_code}'
        raise EGRULException(msg)

    return response.json()


def get_company_data(company_token: str) -> Dict:
    """Отправляет GET-запрос к API и возвращает словарь с данными компании."""
    url = FTS_URL + SEARCH_ENDPOINT + company_token

    try:
        response = r.get(url)
    except r.exceptions.RequestException:
        msg = f'Невозможно отправить запрос на {url}'
        raise EGRULException(msg)

    try:
        rows_list = response.json()["rows"]
    except KeyError:
        msg = 'Перечень компаний не содержит ключа "rows"'
        raise EGRULException(msg)

    try:
        company = rows_list[0]
    except IndexError:
        msg = 'По этому ИНН/ОГРН ничего не нашлось. Проверьте написание.'
        raise EGRULException(msg)

    return company


def check_expire(company_dict: Dict) -> str:
    """Проверяет исключено ли лицо из ЕГРЮЛ."""
    try:
        expire_date = company_dict["e"]
        return f'Регистрация прекращена {expire_date}'
    except KeyError:
        date = dt.datetime.now().date().strftime('%d.%m.%Y')
        return f'Действует на {date}'


def parse_individual(company_dict: Dict) -> str:
    """Получает словарь с данными компании.
    Возвращает имя, ИНН и ОГРНИП индивидуального предпринимателя."""
    try:
        name = company_dict["n"].title()
        inn = company_dict["i"]
        ogrn = company_dict["o"]
    except KeyError:
        msg = 'Отсутвуют или изменены ключи с данными об ИП'
        raise EGRULException(msg)

    return (
        f'ИП: {name}\n'
        f'ИНН: {inn}\n'
        f'ОГРНИП: {ogrn}\n'
    )


def parse_company(company_dict: Dict) -> str:
    """Получает словарь с данными компании.
    Возвращает название, ЕИО, ОГРН, ИНН, КПП и адрес компании."""
    try:
        company_name = company_dict["c"]
        ceo = company_dict["g"].title()
        inn = company_dict["i"]
        ogrn = company_dict["o"]
        kpp = company_dict["p"]
        address = company_dict["a"].title()
    except KeyError:
        msg = 'Отсутвуют или изменены ключи с данными о компании'
        raise EGRULException(msg)

    return (
        f'Компания: {company_name}\n'
        '\n'
        f'{ceo}\n'
        f'ИНН: {inn}\n'
        f'ОГРН: {ogrn}\n'
        f'КПП: {kpp}\n'
        f'Адрес: {address}\n'
    )


def parse_information(company_dict: Dict) -> Callable[[Dict], str]:
    """Получает словарь с данными компании."""
    # не придумал докстринг на русском
    if company_dict["k"] == "fl":
        return parse_individual(company_dict)
    return parse_company(company_dict)


def parse_egrul(query: int) -> str:
    """Получает на вход ИНН или ОГРН и возвращает информацию о компании."""
    try:
        token_dict = get_companys_token(query)
        company_dict = get_company_data(token_dict["t"])
        expire = check_expire(company_dict)
        inf = parse_information(company_dict)

    except EGRULException as error:
        logger.error(error)
        raise Exception(f'При поиске произошла ошибка.\n{error}')

    except Exception as e:
        logger.error(e)
        raise Exception(f'Во время работы программы произошла ошибка.\n{e}')

    return f'{inf}\n{expire}'


def main():
    print('Введите ИНН или ОГРН:')
    query = int(input())
    information = parse_egrul(query)
    return print(information)


if __name__ == '__main__':
    main()
