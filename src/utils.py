from requests import RequestException
from bs4 import BeautifulSoup

from exceptions import ParserFindTagException, NoResponseException
from constants import ENCODING, PARSING_MODULE


def get_response(session, url, encoding=ENCODING):
    # Для прохождения тестов
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException:
        error_msg = f'Возникла ошибка при загрузке страницы {url}'
        raise NoResponseException(error_msg)


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        raise ParserFindTagException(error_msg)
    return searched_tag


def get_soup(session, url, features=PARSING_MODULE):
    response = get_response(session, url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features)
    return soup
