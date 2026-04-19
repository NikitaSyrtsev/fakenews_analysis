import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

def parse_page(url):
    """Парсит страницу раздела и возвращает список ссылок на новости."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    news_links = []
    for link in soup.find_all('a', {'data-ui2-ajax': True, 'href': True}):
        if '/news/' in link['href']:
            absolute_link = urljoin(url, link['href'])
            if absolute_link not in news_links:
                news_links.append(absolute_link)

    return news_links

def parse_news_page(url):
    """Парсит страницу новости и возвращает заголовок и текст."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find('meta', {'property': 'og:title'})['content']
    text_div = soup.find('div', {'itemprop': 'articleBody'})
    text = text_div.get_text(strip=True) if text_div else ''

    return title, text

def collect_data(base_url, max_pages=67):
    """Собирает данные со всех страниц раздела."""
    data = []

    for page in range(1, max_pages + 1):
        page_url = f"{base_url}?page={page}" if page > 1 else base_url
        print(f"Парсинг страницы: {page_url}")

        try:
            news_links = parse_page(page_url)
            for link in news_links:
                try:
                    title, text = parse_news_page(link)
                    data.append({
                        'title': title,
                        'link': link,
                        'text': text,
                        'is_fake': 1
                    })
                except Exception as e:
                    print(f"Ошибка при парсинге {link}: {e}")
        except Exception as e:
            print(f"Ошибка при парсинге страницы {page_url}: {e}")

    return data

# Запуск парсера
base_url = "https://panorama.pub/science"
data = collect_data(base_url, max_pages=67)

# Сохранение данных в CSV
df = pd.DataFrame(data)
df.to_csv('panorama_science_news.csv', index=False)
