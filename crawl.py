import io
import os
import json

import bs4
import requests
from PIL import Image


class Crawler:
    search_url = 'https://www.eventscribe.net/2021/2021CVPR/searchbyposterbucket.asp'
    poster_url = 'https://www.eventscribe.net/2021/2021CVPR/popups/posterView.asp'

    def __init__(self) -> None:
        self.session = requests.Session()
        cookies = json.load(open('cookies.json', 'r'))
        self.session.cookies.update(cookies)

    def get(self, url, **kwargs):
        r = self.session.get(url, **kwargs)
        if 'text/html' not in r.headers['content-type']:
            return r.content
        return bs4.BeautifulSoup(r.text, features='html.parser')

    def search(self):
        data = {
            'f': 'PosterCustomField11',
            'bm': 'Oral%20Paper',
            'pfp': 'OralPapers',
        }
        soup = self.get(self.search_url, data=data)
        posters = []
        for a in soup.find_all('a', {'data-posterid': True}):
            posters.append(a.get('data-posterid'))
        return posters

    def get_poster(self, pid):
        soup = self.get(f'{self.poster_url}?posterId={pid}')
        img_url = soup.find('img').get('src')
        r = self.get(img_url)
        img = Image.open(io.BytesIO(r))
        with open(f'posters/{pid}.png', 'wb') as f:
            img.save(f)

    def crawl(self):
        os.makedirs('posters', exist_ok=True)
        posters = self.search()
        while posters:
            print(f'Remaining papers: {len(posters)}.')
            p = posters.pop()
            try:
                self.get_poster(p)
            except Exception as e:
                print(f'Error getting poster: {p}')
                print(e)
                posters.append(p)


if __name__ == '__main__':
    Crawler().crawl()
