import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

def parse_page(url):
    """Парсит страницу раздела и возвращает список ссылок на новости."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    news_links = set()  # Используем множество, чтобы избежать дубликатов
    for link in soup.select('main a[href*="/feiky/"]'):
        absolute_link = urljoin(url, link['href'])
        if "#comments" not in absolute_link:  # Исключаем ссылки на комментарии
            news_links.add(absolute_link)

    return list(news_links)

def parse_news_page(url):
    """Парсит страницу новости и возвращает заголовок и текст из первых двух абзацев."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find('h1').get_text(strip=True) if soup.find('h1') else ''

    article_body = soup.find('div', {'itemprop': 'articleBody'})
    if article_body:
        paragraphs = article_body.find_all('p')
        text = ' '.join([p.get_text(strip=True) for p in paragraphs[:2]])  # Берем только первые два абзаца
    else:
        text = ''

    return title, text

def collect_data(base_url, max_pages=100):
    """Собирает данные со всех страниц раздела."""
    data = []
    seen_links = set()  # Множество для отслеживания уже обработанных ссылок

    for page in range(2, max_pages + 1):
        page_url = f"{base_url}{page}/"
        print(f"Парсинг страницы: {page_url}")

        try:
            news_links = parse_page(page_url)
            for link in news_links:
                if link not in seen_links:
                    try:
                        title, text = parse_news_page(link)
                        data.append({
                            'title': title,
                            'link': link,
                            'text': text,
                            'is_fake': 1
                        })
                        seen_links.add(link)  # Добавляем ссылку в множество обработанных
                    except Exception as e:
                        print(f"Ошибка при парсинге {link}: {e}")
        except Exception as e:
            print(f"Ошибка при парсинге страницы {page_url}: {e}")

    return data

# Запуск парсера
base_url = "https://lapsha.media/feiky/page/"
data = collect_data(base_url, max_pages=100)

# Сохранение данных в CSV
df = pd.DataFrame(data)
df.to_csv('lapsha_feiky_news.csv', index=False)