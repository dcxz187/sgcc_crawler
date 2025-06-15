from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from config import BASE_URL, MAX_WORKERS
from utils import request_url, save_article_to_file
from db import insert_article
from browser_utils import get_driver, request_page
from robots_check import check_robots
from visualizer import analyze_by_page_title, plot_bar_chart, plot_pie_chart

def get_recent_dates(days=7):
    today = datetime.now()
    dates = []
    for i in range(days):
        d = today - timedelta(days=i)
        if d.weekday() < 5:
            dates.append(d.strftime('%Y%m/%d'))
    return dates

def parse_issue_page(driver, issue_url, issue_date_str):
    html = request_page(driver, issue_url)
    soup = BeautifulSoup(html, 'html.parser')
    polygons = soup.find_all('polygon', class_='area')

    articles = []
    for poly in polygons:
        article_title = poly.get('title')
        page_number = poly.get('data-pageid')
        article_id = poly.get('data-contentid')
        source_url = f"{BASE_URL}/{issue_date_str}/con-{article_id}.html"
        issue_date = f"{issue_date_str[:4]}-{issue_date_str[4:6]}-{issue_date_str[7:]}"
        articles.append({
            'article_title': article_title,
            'page_number': page_number,
            'article_id': article_id,
            'source_url': source_url,
            'issue_date': issue_date
        })
    return articles

def parse_article_detail(article):
    try:
        html = request_url(article['source_url'])
        soup = BeautifulSoup(html, 'html.parser')

        top_bar = soup.find('div', class_='top_bar')
        page_title = top_bar.find(text=True, recursive=False).strip() if top_bar else ''

        author_tag = soup.find('div', class_='author')
        author = author_tag.get_text(strip=True) if author_tag else ''

        content_div = soup.find('div', class_='content')
        content = content_div.get_text(separator='\n', strip=True)

        article['page_title'] = page_title
        article['author'] = author
        article['content'] = content
        article['crawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        insert_article(article)
        save_article_to_file(article)
        print(f"爬取成功: {article['article_title']}")
    except Exception as e:
        print(f"爬取失败: {article['source_url']} 错误: {e}")

def crawl():
    if not check_robots():
        return

    driver = get_driver()
    dates = get_recent_dates()
    all_articles = []

    for date in dates:
        for page in range(2, 9, 2):
            issue_url = f"{BASE_URL}/{date}/#page={page}"
            try:
                articles = parse_issue_page(driver, issue_url, date)
                if articles:
                    all_articles.extend(articles)
                    print(f"日期 {date} 第 {page} 页，找到 {len(articles)} 篇文章")
            except Exception as e:
                print(f"页面加载失败: {issue_url} 错误: {e}")

    driver.quit()

    print(f"开始下载详情页，总计 {len(all_articles)} 篇文章")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(parse_article_detail, all_articles)

    # 新增：统计和绘图
    category_counter = analyze_by_page_title(all_articles)
    plot_bar_chart(category_counter)
    plot_pie_chart(category_counter)

if __name__ == '__main__':
    crawl()
