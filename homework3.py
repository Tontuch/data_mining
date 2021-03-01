import requests
import bs4
from urllib.parse import urljoin
from database.db import Database


class GbBlogParse:

    def __init__(self, start_url, database:Database):
        self.db = database
        self.start_url = start_url
        self.done_url = set()
        self.tasks = [self.get_task(self.start_url, self.parse_feed),]
        self.done_url.add(self.start_url)

    def get_task(self, url, callback):
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)
        return task

    def _get_response(self, url):
        response = requests.get(url)
        return response

    def _get_soup(self, url):
        soup = bs4.BeautifulSoup(self._get_response(url).text, 'lxml')
        return soup

    def parse_post(self, url, soup):
        img = soup.find('div', attrs={'class': 'hidden', 'itemprop': 'image'}).text
        author_tag = soup.find('div', attrs={'itemprop': 'author'})

        data ={
            'data_posts':{
                'title': soup.find('h1', attrs={'class': 'blogpost-title'}).text,
                'url': url,
            },
            'data_author':{
                'url': urljoin(url, author_tag.parent.get('href')),
                'name': author_tag.text,
            },
            'data_tag':{
                'tag_post': [{'name': tag.text,'url': urljoin(url, tag.attrs.get('href'))}
                        for tag in soup.findAll('a', attrs={'class': 'small'})]
            },
        }
        return data

    def parse_feed(self, url, soup):
        ul = soup.find('ul', attrs={'class': 'gb__pagination'})
        pag_urls = set(urljoin(url, href.attrs.get('href'))
                       for href in ul.findAll('a')
                       if href.attrs.get('href'))
        for pag_urls in pag_urls:
            if pag_urls not in self.done_url:
                self.tasks.append(self.get_task(pag_urls, self.parse_feed))

        post_items = soup.find('div', attrs={'class': 'post-items-wrapper'})
        posts_url = set(urljoin(url, href.attrs.get('href'))
                        for href in post_items.findAll('a', attrs={'class': 'post-item__title'})
                        if href.attrs.get('href'))
        for posts_url in posts_url:
            if posts_url not in self.done_url:
                self.tasks.append(self.get_task(posts_url, self.parse_post))


    def run(self):
        for task in self.tasks:
            task_result = task()
            if task_result:
                self.save(task_result)


    def save(self, data):
        print(1)
        self.db.create_post(data)

if __name__ == '__main__':
    database = Database('sqlite:///gb_blog.db')
    parser = GbBlogParse('https://geekbrains.ru/posts', database)
    parser.run()