import requests
import re
import os.path
from os import path
from bs4 import BeautifulSoup
main_url = 'http://cdm.etc.br'


def start(config):
    """
    Main function that iteretes throug cdm website and gets the target data
    :param config:
        'method': title | letter | all
        'description': based on 'method' parameter
    """
    check_folder()
    if config['method'] == 'title':
        url = f'{main_url}/titulos/{config["description"]}'
    elif config['method'] == 'letter':
        url = f'{main_url}/filtro/{config["description"]}'
    else:
        print("Invalid method.")
    print('Getting data from:', url)
    scrap_title(config["description"], url)


def scrap_title(description, url):
    """
    Gatter data about the title
    :param url: url from where title data will be collecte
    """
    check_folder(description)
    r = requests.get(url=url)
    if r.ok:
        soup = BeautifulSoup(r.content, 'html.parser')
        links = soup.find_all('a')
        for item in links:
            if 'ler-online-completo' in str(item):
                url = f'{main_url}/{item.attrs["href"]}'
                print("Getting chapter from:", url)
                scrap_chapter(description, url)


def scrap_chapter(description, url):
    """
    Gatter data about the chapter of the title
    :param description: name of the content
    :param url: url of the content
    """
    chapter = re.search('\d+$', url).group(0)
    check_folder(description, chapter)
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
        for item in pages_base:
            get_page(description, chapter, url_base, item, 'jpg')


def get_page(description, chapter, url, page, file_format):
    """
    Function that gets the actual image of the title
    :param description: name of the title
    :param chapter: number of the chapter of the title
    :param url: url where the image is getting from
    :param page: relative link of the url of the page
    :param file_format: format of the image
    """
    url_page = f'{url}{page}.{file_format}'
    print('url_page', url_page)
    r = requests.get(url=url_page, headers={'Referer': 'http://centraldemangas.online'})
    if r.ok:
        file = open(f'output/{description}/{chapter}/{page}.{file_format}', "wb")
        file.write(r.content)
        file.close()


def check_folder(t=None, c=None):
    """
    Check if the targer folder exists, if not, creates it
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
