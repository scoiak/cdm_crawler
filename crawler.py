import requests
import re
import os.path
from multiprocessing import Pool
from bs4 import BeautifulSoup
main_url = 'http://cdm.etc.br'

"""
    RUNNING PARAMETERS
"""
DEBUG = False                       # True for help messagens while running
TOTAL_WORKERS = 6                   # Total of threads used to download files
MAIN_URL = 'http://cdm.etc.br'      # Base URL of the website


def start(config):
    """
    Main function that iteretes throug cdm website and gets the target data
    :param config:
        'method': title | letter | all
        'description': based on 'method' parameter
    """
    check_folder()
    url = None
    if config['method'] == 'title':
        url = f'{MAIN_URL}/titulos/{config["description"]}'
    elif config['method'] == 'letter':
        url = f'{MAIN_URL}/filtro/{config["description"]}'
    else:
        print("Invalid method.")
    if DEBUG:
        print('::start - url:', url)
    scrap_title(config["description"], url)


def scrap_title(description, url):
    """
    Gatter data about the title
    :param url: url from where title data will be collecte
    """
    check_folder(description)
    print(f'Starting download of the title \'{description}\'')
    r = requests.get(url=url)
    if r.ok:
        soup = BeautifulSoup(r.content, 'html.parser')
        links = [x for x in soup.find_all('a')]
        if DEBUG:
            print('::scrap_title - links:', links)
        for item in links.__reversed__():
            if 'ler-online-completo' in str(item):
                url = f'{MAIN_URL}/{item.attrs["href"]}'
                if DEBUG:
                    print('::scrap_title - url:', url)
                scrap_chapter(description, url)


def scrap_chapter(description, url):
    """
    Gatter data about the chapter of the title
    :param description: name of the content
    :param url: url of the content
    """
    chapter = re.search('\d+$', url).group(0)
    check_folder(description, chapter)
    url_base = None
    pages_base = None
    if DEBUG:
        print('::scrap_chapter - url:', url)
    r = requests.get(url=url)
    if r.ok:
        soup = BeautifulSoup(r.content, 'html.parser')
        script_list = soup.find_all('script')
        for item in script_list:
            if 'urlSulfix' in str(item):
                url_line = re.search('.*(urlSulfix).*', str(item)).group(0)
                url_base = re.search('\'(.*)\'', url_line).group(0).replace('\'', '')
                pages_line = re.search('.*(pages).*', str(item)).group(0)
                pages_base = re.findall('(\d+)', pages_line)
                if DEBUG:
                    print('::scrap_chapter - url_base:', url_base)
                    print('::scrap_chapter - pages_base:', pages_base)
        contador = 0
        download_list = []
        for item in pages_base:
            contador += 1
            if DEBUG:
                print('::scrap_chapter - item:', item)
            download_list.append({
                'description': description,
                'chapter': chapter,
                'url': url_base,
                'page': item,
                'file_format': 'jpg'
            })
        with Pool(processes=TOTAL_WORKERS) as pool:
            pool.map(get_page, download_list)
        print(f' Chapter successfully downloaded.')


def get_page(params):
    """
    Function that gets the actual image of the title
    :param params: dict with the data parameters used for running the thread
    """
    description = params.get('description')
    chapter = params.get('chapter')
    url = params.get('url')
    page = params.get('page')
    file_format = params.get('file_format')

    print(f'\r- Dowloading {description} chapter {chapter} ({page}).', end='')

    url_page = f'{url}{page}.{file_format}'
    if DEBUG:
        print('::get_page - url_page:', url_page)
    r = requests.get(url=url_page, headers={'Referer': 'http://centraldemangas.online'})
    if r.ok:
        file = open(f'output/{description}/{chapter}/{page}.{file_format}', "wb")
        file.write(r.content)
        file.close()


def check_folder(t=None, c=None):
    """
    Checks if the target folder exists, if not, creates it
    :param t: name of the tile
    :param c: number of the chapter
    """
    if t is None:
        if not os.path.exists(f'output'):
            os.mkdir(f'output')

    if t is not None and c is None:
        if not os.path.exists(f'output/{t}'):
            os.mkdir(f'output/{t}')

    if t is not None and c is not None:
        if not os.path.exists(f'output/{t}/{c}'):
            os.mkdir(f'output/{t}/{c}')
