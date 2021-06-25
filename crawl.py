import os
import json

import bs4
import requests


class Crawler:
    search_url = 'https://www.eventscribe.net/2021/2021CVPR/searchbyposterbucket.asp'
    info_url = 'https://www.eventscribe.net/2021/2021CVPR/fsPopup.asp'
    poster_url = 'https://www.eventscribe.net/2021/2021CVPR/popups/posterView.asp'
    cvf_url = 'https://openaccess.thecvf.com'

    def __init__(self) -> None:
        self.session = requests.Session()
        cookies = json.load(open('cookies.json', 'r'))
        self.session.cookies.update(cookies)

    def get_html(self, url, **kwargs):
        r = self.session.get(url, **kwargs)
        mt = r.headers['content-type']
        if 'text/html' not in mt:
            raise ValueError(f'Not html page, found: {mt}.')
        return bs4.BeautifulSoup(r.text, features='html.parser')

    def get_content(self, url, **kwargs):
        r = self.session.get(url, **kwargs)
        mt = r.headers['content-type']
        if 'text/html' in mt:
            raise ValueError(f'We expect a media type, found: {mt}.')
        return r.content

    @staticmethod
    def get_link_by_text(soup, text):
        for a in soup.find_all('a'):
            if text in a.text:
                return a.get('href')
        return None

    def get_info(self, poster_id, title):
        paper_info = self.get_html(
            f'{self.info_url}?PosterID={poster_id}&mode=posterinfo')
        paper_url = self.get_link_by_text(paper_info, 'PDF')
        paper_info = self.get_html(paper_url)
        paper_url = self.get_link_by_text(paper_info, 'pdf')
        poster_url = f'{self.poster_url}?posterId={poster_id}'
        soup = self.get_html(poster_url)
        img_url = soup.find('img').get('src')
        paper = {
            'id': poster_id,
            'title': title,
            'pdf': f'{self.cvf_url}{paper_url}',
            'poster': img_url,
        }
        return paper

    # def save_poster(self, paper, path):
    #     soup = self.get_html(paper['poster'])
    #     img_url = soup.find('img').get('src')
    #     r = self.get_content(img_url)
    #     img = Image.open(io.BytesIO(r))
    #     with open(path, 'wb') as f:
    #         img.save(f)

    def save_content(self, url, path):
        if os.path.exists(path):
            return
        c = self.get_content(url)
        with open(path, 'wb') as f:
            f.write(c)

    def crawl(self, papers=None):
        os.makedirs('posters', exist_ok=True)
        os.makedirs('papers', exist_ok=True)
        soup = self.get_html(
            f'{self.search_url}?f=PosterCustomField11&pfp=OralPapers')
        papers = papers or {}
        lis = soup.find_all('li', {'data-presid': True})
        for i, li in enumerate(lis):
            a = li.find('a', {'data-posterid': True})
            title = li.select('div[class*=prestitle]')[0].text.strip()
            poster_id = a.get('data-posterid')
            poster_path = os.path.join('posters', f'{title}.png')
            paper_path = os.path.join('papers', f'{title}.pdf')
            if os.path.exists(poster_path) and \
               os.path.exists(paper_path):
                continue
            paper = self.get_info(poster_id, title)
            print(f'{i + 1}/{len(lis)}: {paper["title"]}')
            title = paper['title']
            self.save_content(paper['poster'], poster_path)
            self.save_content(paper['pdf'], paper_path)
            papers[poster_id] = paper
        return papers


if __name__ == '__main__':
    p = None
    if os.path.exists('papers.json'):
        with open('papers.json', 'r') as f:
            p = json.load(f)
    try:
        p = Crawler().crawl(p)
    except Exception as e:
        print(e)
    with open('papers.json', 'w') as f:
        json.dump(p, f, indent=4)
