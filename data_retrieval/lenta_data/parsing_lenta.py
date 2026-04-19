import feedparser

rss_url = "https://lenta.ru/rss/news"
feed = feedparser.parse(rss_url)

news_data = []

for entry in feed.entries:
    title = entry.title
    link = entry.link
    news_data.append({"title": title, "link": link})

import requests
from bs4 import BeautifulSoup

def get_full_text(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # На Lenta.ru основной текст находится в тегах внутри <div class="topic-body__content"> или аналогичных
        article_div = soup.find("div", class_="topic-body__content")
        if article_div:
            paragraphs = article_div.find_all("p")
            full_text = "\n".join([p.get_text(strip=True) for p in paragraphs])
            return full_text
        return ""
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {e}")
        return ""


all_news = []

for entry in feed.entries:
    title = entry.title
    link = entry.link
    text = get_full_text(link)
    
    if text:  # Только если удалось получить текст
        all_news.append({
            "title": title,
            "link": link,
            "text": text,
            "label": 0  # Признак: 0 — это НЕ фейк
        })

import pandas as pd

df = pd.DataFrame(all_news)
df.to_csv("lenta_real_news.csv", index=False)
