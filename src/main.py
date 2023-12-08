import re
from urllib.parse import urljoin
import logging
from collections import Counter

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR, MAIN_DOC_URL, PEP_TABLE_URL, EXPECTED_STATUS, DOWNLOAD_DIR_NAME,
)
from outputs import control_output
from utils import find_tag, get_soup
from exceptions import VersionListNotFoundException


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = get_soup(session, whats_new_url)
    div_with_ul = find_tag(soup, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])
        soup = get_soup(session, version_link)
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, ' '+h1.text, dl_text)
        )
    return results


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise VersionListNotFoundException(
            'Не найден список c версиями Python'
        )
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = get_soup(session, downloads_url)
    pdf_a4_tag = find_tag(
        soup,
        'a',
        {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / DOWNLOAD_DIR_NAME
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    soup = get_soup(session, PEP_TABLE_URL)
    section = find_tag(soup, 'section', {'id': 'numerical-index'})
    pep_rows = section.find_all('tr')
    results = [('Статус', 'Количество')]
    status_count = Counter()
    pep_count = 0
    for row in tqdm(pep_rows[1:]):
        status_abbreviation = find_tag(row, 'abbr').text[1:]
        try:
            status_in_table = EXPECTED_STATUS[status_abbreviation]
        except KeyError:
            status_in_table = []
            logging.info(
                f'Статус {status_abbreviation} не обнаружен в списке\n' +
                f'Строка с неизвестным статусом:{row}'
            )
        pep_link = find_tag(row, 'a')['href']
        pep_url = urljoin(PEP_TABLE_URL, pep_link)
        soup = get_soup(session, pep_url)
        dl = find_tag(soup, 'dl')
        status_row = dl.find(string='Status').find_parent()
        if not status_row:
            logging.info(
                f'Cтрока статуса не обнаружена на странице:{pep_url}',
            )
            continue
        pep_status = status_row.next_sibling.next_sibling.text
        if pep_status not in status_in_table:
            logging.info(
                'Статус не соответствует статусу в списке:\n' +
                f'Статусу в списке:{status_in_table}\n' +
                f'Строка в списке:\n{row}\n' +
                f'Статусу на странице PEP:{pep_status}\n' +
                f'Строница с неожиданным статусом:\n{pep_url}\n'
            )
        status_count[pep_status] += 1
        pep_count += 1
    results.extend(status_count.items())
    results.append(('Total', pep_count))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    try:
        results = MODE_TO_FUNCTION[parser_mode](session)
    except Exception as error:
        logging.exception(
            error,
            stack_info=True
        )

    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
