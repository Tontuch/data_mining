import requests
import pymongo
import bs4
from urllib.parse import urljoin
from pathlib import Path
import datetime

class MagnitParse:
    month = {
        'янв' : 1,
        'фев': 2,
        'март': 3,
        'апр' : 4,
        'мая' : 5,
        'июн' : 6,
        'июл' : 7,
        'август' : 8,
        'сентябр' : 9,
        'октябр' : 10,
        'ноябр' : 11,
        'декабр' : 12
    }

    def __init__(self, start_url, db_client):
        self.start_url = start_url
        self.db = db_client['data_mining']
        self.collection = self.db['magnit_products']

    def _get_response(self, url):
        return requests.get(url)

    def _get_soup(self, url):
        response = self._get_response(url)
        return bs4.BeautifulSoup(response.text, 'lxml')

    def run(self):
        soup = self._get_soup(self.start_url)
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})
        for prod_a in catalog.findAll('a', recursive=False):
            self.save(self._parse(prod_a))

    def get_template(self):
        return {
            'title': lambda a: a.find('div', attrs={'class': 'card-sale__title'}).text,
            'url': lambda a: urljoin(self.start_url, a.attrs.get('href', '')),
            'promo_name': lambda a: a.find('div', attrs={'class': 'card-sale__name'}).text,
            'old_price': lambda a: float('.'.join(a.find('div', attrs={'class': 'label__price_old'}).text.split())),
            'new_price': lambda a: float('.'.join(a.find('div', attrs={'class': 'label__price_new'}).text.split())),
            'image_url': lambda a: urljoin(self.start_url, a.find('img').attrs.get('data-src')),
            'date_from': lambda a: self._get_date(a.find('div', attrs={'class': 'card-sale__date'}).text),
            # 'date_to': 'pass',
        }
    def _get_date(self, temp_date):
        date_parse = temp_date.replace('\n', ' ').replace('с', ' ').split('до')
        date_period = []
        for date in date_parse:










    def _parse(self, product_a) -> dict:
        data = {}
        for key, funk in self.get_template().items():
            try:
                data[key] = funk(product_a)
            except (AttributeError, ValueError):
                pass
        return data

    def save(self, data: dict, ):
        self.collection.insert_one(data)


def get_save_path(dir_name):
    dir_path = Path(__file__).parent.joinpath(dir_name)
    if not dir_path.exists():
        dir_path.mkdir()
    return dir_path


if __name__ == '__main__':
    url = 'https://magnit.ru/promo/'
    save_path = get_save_path('magnit_product')
    db_client = pymongo.MongoClient('mongodb://localhost:27017')
    parser = MagnitParse(url, db_client)
    parser.run()
