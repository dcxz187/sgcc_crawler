import json
import os
import time

import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config import HEADERS


def get_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless==new')  # 无界面
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def request_page(driver, url, wait_time=3):
    driver.get(url)
    time.sleep(wait_time)  # 等待页面动态加载
    return driver.page_source


async def request_url_async(url):
    """异步版本的URL请求函数"""
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(url) as response:
            response.raise_for_status()  # 抛出HTTP错误（如404）
            return await response.text()  # 异步获取响应内容

def save_article_to_file(article, base_dir='articles'):
    os.makedirs(base_dir, exist_ok=True)

    txt_path = os.path.join(base_dir, f"{article['article_id']}.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(article['content'])

    json_path = os.path.join(base_dir, f"{article['article_id']}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(article, f, ensure_ascii=False, indent=4)
