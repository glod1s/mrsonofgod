import requests
from bs4 import BeautifulSoup as BS

HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36', 'accept': '*/*'}


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_content(html, URL):
    soup = BS(html, 'html.parser')
    try:
        items = soup.find('div', id='translations-content').get_text(' | ', strip=True)
        a = soup.find('div', class_='title-content').get_text(strip=True)
        translation = f'<a href="{URL}"><b>{a}</b></a>\n\n{items}'
        return translation
    except Exception:
        return 'Переклад не знайдено. Якщо вводили словосполучення чи речення, спробуйте перекласти кожне слово окремо.'


def parse(word):
    URL = 'https://context.reverso.net/translation/english-ukrainian/'
    URL = URL+word
    html = get_html(URL)
    if html.status_code == 200:
            html = get_html(URL)
            return get_content(html.text, URL)
    else:
        return 'Немає доступу до сайту. Спробуйте ще раз.'