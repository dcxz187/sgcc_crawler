from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无界面
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def request_page(driver, url, wait_time=3):
    driver.get(url)
    time.sleep(wait_time)  # 等待页面动态加载
    return driver.page_source
