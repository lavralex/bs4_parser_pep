from requests import RequestException
from bs4 import BeautifulSoup

from exceptions import ParserFindTagException
from constants import RESPONSE_ENCODING


def get_response(session, url, encoding=RESPONSE_ENCODING):
    # Для прохождения тестов
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException:
        error_msg = f'Возникла ошибка при загрузке страницы {url}'
        raise RequestException(error_msg)


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        raise ParserFindTagException(error_msg)
    return searched_tag


def get_soup(session, url):
    response = get_response(session, url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    return soup
