import datetime as dt
import json
from http import HTTPStatus
from time import sleep
from typing import Callable, Dict
from traceback import format_exc

import requests as r

from src.main_logger import main_logger
from src.exceptions import DevEGRULException, EGRULException, UserEGRULException


class EGRUL:

    FTS_URL = 'https://egrul.nalog.ru/'
    SEARCH_ENDPOINT = 'search-result/'
    HEADERS = {
        "Host": "egrul.nalog.ru",
        "Connection": "Close",
        "Content-Type": "application/json",
        "User-Agent": "python-requests/2.27.1"
    }

    def get_companys_token(self, query: int) -> Dict:
        """Отправляет POST-запрос с ИНН/ОГРН.
        Возвращает словарь с токеном организации."""
        payload = json.dumps({
            "vyp3CaptchaToken": "",
            "page": "",
            "query": query,
            "region": ""
        })

        try:
            response = r.post(self.FTS_URL, data=payload, headers=self.HEADERS)
        except r.exceptions.RequestException:
            msg = f'Невозможно отправить запрос на {self.FTS_URL}'
            raise DevEGRULException(msg)

        if response.status_code != HTTPStatus.OK:
            msg = 'Сайт налоговой недоступен, повторите запрос позже'
            raise UserEGRULException(msg)

        main_logger.info('Успешный запрос токена')

        return response.json()

    def get_company_data(self, company_token: str) -> Dict:
        """Отправляет запрос к API и возвращает словарь с данными компании."""
        url = self.FTS_URL + self.SEARCH_ENDPOINT + company_token

        try:
            response = r.get(url)
        except r.exceptions.RequestException:
            msg = f'Невозможно отправить запрос на {url}'
            raise DevEGRULException(msg)

        main_logger.info('Успешный запрос данных компании')

        try:
            rows_list = response.json()["rows"]
        except KeyError:
            msg = 'Перечень компаний не содержит ключа "rows"'
            raise DevEGRULException(msg)

        if len(rows_list) == 0:
            msg = 'По этому ИНН/ОГРН ничего не нашлось. Проверьте написание.'
            raise UserEGRULException(msg)

        main_logger.info('Ответ содержит данные о компании')

        return rows_list[0]


class EGRULInfo(EGRUL):

    def parse_egrul(self, query: int) -> str:
        """Получает на вход ИНН или ОГРН и возвращает информацию о компании."""
        try:
            token_dict = self.get_companys_token(query)
            company_data = self.get_company_data(token_dict["t"])
            expire = self.__check_expire(company_data)
            inf = self.__parse_information(company_data)
            msg = f'{inf}\n{expire}'

        except UserEGRULException as error:
            main_logger.error(error)
            msg = error.message

        except DevEGRULException as error:
            main_logger.error(error)
            main_logger.error(format_exc())
            msg = 'В работе бота произошла ошибка. Свяжитесь с автором'

        except Exception as e:
            main_logger.exception(e)
            main_logger.error(format_exc())
            msg = 'В работе бота произошла ошибка. Свяжитесь с автором'

        finally:
            return msg

    def __check_expire(self, company_dict: Dict) -> str:
        """Проверяет исключено ли лицо из ЕГРЮЛ."""
        try:
            expire_date = company_dict["e"]
            return f'Регистрация прекращена {expire_date}'
        except KeyError:
            date = dt.datetime.now().date().strftime('%d.%m.%Y')
            return f'Действует на {date}'

    def __parse_individual(self, company_dict: Dict) -> str:
        """Получает словарь с данными компании.
        Возвращает имя, ИНН и ОГРНИП индивидуального предпринимателя."""
        try:
            name = company_dict["n"].title()
            inn = company_dict["i"]
            ogrn = company_dict["o"]
        except KeyError:
            msg = 'Отсутвуют или изменены ключи с данными об ИП'
            raise DevEGRULException(msg)

        return f'ИП: {name}\nИНН: {inn}\nОГРНИП: {ogrn}\n'

    def __parse_company(self, company_dict: Dict) -> str:
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
            raise DevEGRULException(msg)

        return (
            f'Компания: {company_name}\n'
            '\n'
            f'{ceo}\n'
            f'ИНН: {inn}\n'
            f'ОГРН: {ogrn}\n'
            f'КПП: {kpp}\n'
            f'Адрес: {address}\n'
        )

    def __parse_information(self, company_dict: Dict) -> Callable[[Dict], str]:
        """Получает словарь с данными компании.
        Возвращает функцию, обрабатывающую данные об ИП или ЮЛ."""
        if company_dict["k"] == "fl":
            return self.__parse_individual(company_dict)
        return self.__parse_company(company_dict)

    __call__ = parse_egrul


class EGRULExtraction(EGRUL):
    REQUEST_ENDPOINT = 'vyp-request/'
    STATUS_ENDPOINT = 'vyp-status/'
    DOWNLOAD_ENDPOINT = "vyp-download/"

    def get_extraction(self, query: int) -> str:
        """Получает ИНН/ОГРН, возвращает ссылку на скачиание pdf."""
        try:
            token_dict = self.get_companys_token(query)
            company_data = self.get_company_data(token_dict["t"])

            token = company_data["t"]
            request_extraction_dict = self.__extraction_request_and_status(
                token, self.REQUEST_ENDPOINT
            )

            if not token == request_extraction_dict["t"]:
                token = request_extraction_dict["t"]

            status_dict = self.__extraction_request_and_status(
                token,
                self.STATUS_ENDPOINT
            )
            msg = self.__get_download_link(status_dict, token)

        except UserEGRULException as error:
            main_logger.error(error)
            msg = error.message

        except DevEGRULException as error:
            main_logger.error(error)
            main_logger.error(format_exc())
            msg = 'В работе бота произошла ошибка. Свяжитесь с автором'
            raise DevEGRULException(msg)

        except Exception as e:
            main_logger.exception(e)
            main_logger.error(format_exc())
            msg = 'В работе бота произошла ошибка. Свяжитесь с автором'
            raise Exception(msg)

        return msg

    def __extraction_request_and_status(
        self, token: str, endpoint: str
    ) -> Dict:
        """Отправляет API запрос на формирование выписки ЕГРЮЛ."""
        url = self.FTS_URL + endpoint + token

        try:
            responce = r.get(url)
        except r.exceptions.RequestException:
            msg = f'Невозможно отправить запрос на {url}'
            raise DevEGRULException(msg)

        main_logger.info(
            'Успешный запрос на формирование выписки/проверку статус'
        )

        return responce.json()

    def __check_status(self, status_dict: Dict) -> bool:
        """Проверяет статус готовности выписки."""
        try:
            status = status_dict['status']
        except KeyError:
            msg = 'Список компаний не содержит ключа "status"'
            raise DevEGRULException(msg)
        return status == 'ready'

    def __get_download_link(self, status_dict: Dict, token: str) -> str:
        """Получает ссылку для скачивания выписки."""
        counter = 0

        while counter != 3:
            if not self.__check_status(status_dict):
                sleep(0.2)
                counter += 1
            main_logger.info('Ссылка на выписку получена успешно')
            return self.FTS_URL + self.DOWNLOAD_ENDPOINT + token

        msg = 'ЕГРЮЛ не сформировал выписку, попробуйте снова'
        raise UserEGRULException(msg)

    __call__ = get_extraction


short_info = EGRULInfo()
pdf_extraction = EGRULExtraction()
