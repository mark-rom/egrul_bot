import logging
import os
from logging.handlers import RotatingFileHandler
from time import sleep
from typing import Dict

import requests as r

from settings import LOGS_DIR

from .egrul_info import get_company_data, get_companys_token
from .exceptions import EGRULException

FTS_URL = "https://egrul.nalog.ru/"
REQUEST_ENDPOINT = 'vyp-request/'
STATUS_ENDPOINT = 'vyp-status/'
DOWNLOAD_ENDPOINT = "vyp-download/"


logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
handler = RotatingFileHandler(
    os.path.join(LOGS_DIR, 'egrul_info/egrul_extraction.log'), backupCount=1,
    encoding='utf-8', maxBytes=1000000
)
handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def extraction_request_and_status(token: str, endpoint: str) -> Dict:
    """Отправляет API запрос на формирование выписки ЕГРЮЛ."""
    url = FTS_URL + endpoint + token

    try:
        responce = r.get(url)
    except r.exceptions.RequestException:
        msg = f'Невозможно отправить запрос на {url}'
        raise EGRULException(msg)

    logger.info('Успешный запрос на формирование выписки/проверку статус')

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
        logger.info('Ссылка на выписку получена успешно')
        return FTS_URL + DOWNLOAD_ENDPOINT + token

    msg = 'ЕГРЮЛ не сформировал выписку'
    raise EGRULException(msg)


def get_extraction(query: int) -> str:
    """Получает ИНН/ОГРН, возвращает ссылку на скачиание pdf."""
    try:
        token_dict = get_companys_token(query)
        company_dict = get_company_data(token_dict["t"])

        token = company_dict["t"]
        request_extraction_dict = extraction_request_and_status(
            token, REQUEST_ENDPOINT
        )

        if not token == request_extraction_dict["t"]:
            token = request_extraction_dict["t"]

        status_dict = extraction_request_and_status(token, STATUS_ENDPOINT)

    except EGRULException as error:
        logger.error(error)
        raise Exception(f'При формировании выписки произошла ошибка.\n{error}')

    except Exception as e:
        logger.exception(e)
        raise Exception(f'Во время работы программы произошла ошибка.\n{e}')

    return get_download_link(status_dict, token)


def main():
    print('Введите ИНН или ОГРН:')
    query = int(input())
    extraction_url = get_extraction(query)
    return print(extraction_url)


if __name__ == '__main__':
    main()
