import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

# Функция для парсинга главной страницы и получения ссылок на новости
def parse_main_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Находим все ссылки на новости
    news_links = []
    for link in soup.find_all('a', href=True):
        if '/news/' in link['href']:
            absolute_link = urljoin(url, link['href'])
            if absolute_link not in news_links:
                news_links.append(absolute_link)

    return news_links

# Функция для парсинга страницы новости
def parse_news_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Извлекаем заголовок
    title = soup.find('meta', {'property': 'og:title'})['content']

    # Извлекаем текст новости
    text_div = soup.find('div', {'itemprop': 'articleBody'})
    text = text_div.get_text(strip=True) if text_div else ''

    return title, text

# Основная функция для сбора данных
def collect_data(base_url):
    news_links = parse_main_page(base_url)
    data = []

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

    return data

# Запуск парсера
base_url = "https://panorama.pub/"
data = collect_data(base_url)

# Сохраняем данные в CSV
df = pd.DataFrame(data)
df.to_csv('panorama_news.csv', index=False)
