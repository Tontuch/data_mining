import requests
from pathlib import Path
import time
import json


url = 'https://5ka.ru/api/v2/special_offers/'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'}
params = {'store': None,
          'records_per_page': 12,
          'page': 1,
          'categories': None,
          'ordering': None,
          'price_promo__gte': None,
          'price_promo__lte': None,
          'search': None}


# response = requests.get(url, params=params, headers=headers)
#
# result_html_file = Path(__file__).parent.joinpath('5ka.html')
# result_json_file = Path(__file__).parent.joinpath('5ka.json')
# result_json_file.write_text(response.text, encoding='UTF-8')

class Parse5ka:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'}

    def __init__(self, start_url: str, save_path: Path):
        self.start_url = start_url
        self.save_path = save_path

    def _get_response(self, url):
        while True:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response
            time.sleep(0.5)

    def run(self):
        for product in self._parse(self.start_url):
            product_path = self.save_path.joinpath(f"{product['id']}.json")
            self._save(product, product_path)

    def _parse(self, url: str):
        while url:
            response = self._get_response(url)
            data: dict = response.json()
            url = data['next']
            for product in data['results']:
                yield product

    def _save(self, data: dict, file_path: Path):
        file_path.write_text(json.dumps(data, ensure_ascii=False), encoding='UTF-8')


class Parse5ka_category(Parse5ka):
    
    def __init__(self, url_category, start_url: str, save_path: Path):
        super().__init__(start_url, save_path)
        self.url_category = url_category

    def _get_category(self):
        response = self._get_response(self.url_category)
        data = response.json()
        for category in data:
            yield category

    def run(self):
        for category in self._get_category():
            category['product'] = []
            url = f"{self.start_url}?categories={category['parent_group_code']}"
            for product in self._parse(url):
                category['product'].append(product)
            cat_path = self.save_path.joinpath(f"{category['parent_group_code']}.json")
            self._save(category, cat_path)


if __name__ == '__main__':
    url = 'https://5ka.ru/api/v2/special_offers/'
    save_path = Path(__file__).parent.joinpath('products')
    if not save_path.exists():
        save_path.mkdir()
    parser = Parse5ka(url, save_path)
    # parser.run()

if __name__ == '__main__':
    url_category = 'https://5ka.ru/api/v2/categories/'
    save_path_category = Path(__file__).parent.joinpath('category')
    if not save_path_category.exists():
        save_path_category.mkdir()
    pars_category = Parse5ka_category(url_category, url, save_path_category)
    pars_category.run()




