"""
    author: kaio_stricker
    title: cdm_crowler
    description: get the content of titles from the website 'http://cdm.etc.br/'
"""
from crawler import start

if __name__ == '__main__':
    start(config={
        'method': 'title',
        'description': 'tenchi-muyo'
    })


# maou-jou-de-oyasumi
# tenchi-muyo