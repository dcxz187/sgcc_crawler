import requests
import os
import json
import time
from config import HEADERS, REQUEST_DELAY


def request_url(url):
    time.sleep(REQUEST_DELAY)
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    response.encoding = 'utf-8'
    return response.text


def save_article_to_file(article, base_dir='articles'):
    os.makedirs(base_dir, exist_ok=True)

    txt_path = os.path.join(base_dir, f"{article['article_id']}.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(article['content'])

    json_path = os.path.join(base_dir, f"{article['article_id']}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(article, f, ensure_ascii=False, indent=4)
