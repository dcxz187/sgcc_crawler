from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from config import BASE_URL
from utils import save_article_to_file, get_driver, request_page, request_url_async
from db import insert_article, check_article_exists
from robots_check import check_robots
from visualizer import analyze_by_page_title, plot_bar_chart, plot_pie_chart, load_category_counter
import asyncio
import argparse
import schedule
import time

"""获取最近7天的工作日"""
def get_recent_dates(driver, target_count=7, max_check_days=25):
    valid_dates = []
    current_date = datetime.now()
    days_checked = 0

    while len(valid_dates) < target_count and days_checked < max_check_days:
        date_str = current_date.strftime('%Y%m/%d')
        test_url = f"{BASE_URL}/{date_str}/#page=2"

        try:
            request_page(driver, test_url)
            valid_dates.append(date_str)
            print(f"找到有效日期: {date_str}（第 {len(valid_dates)} 个）")
        except Exception as e:
            print(f"日期 {date_str} 无日报: {e}")

        current_date -= timedelta(days=1)
        days_checked += 1

    if len(valid_dates) < target_count:
        print(f"警告：仅找到 {len(valid_dates)} 个有效日期（已检查 {days_checked} 天）")
    return valid_dates


"""解析报纸页面，获取部分信息"""
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

"""异步解析文章详情页面"""
async def parse_article_detail_async(article):
    try:
        # 提前检查是否已存在
        if check_article_exists(article["article_id"]):
            print(f"跳过已存在文章: {article['article_title']}")
            return

        # 异步请求详情页
        html = await request_url_async(article["source_url"])
        soup = BeautifulSoup(html, "html.parser")

        top_bar = soup.find("div", class_="top_bar")
        page_title = top_bar.find(text=True, recursive=False).strip() if top_bar else ""
        author_tag = soup.find("div", class_="author")
        author = author_tag.get_text(strip=True) if author_tag else ""
        content_div = soup.find("div", class_="content")
        content = content_div.get_text(separator="\n", strip=True) if content_div else ""

        # 更新文章信息
        article.update({
            "page_title": page_title,
            "author": author,
            "content": content,
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # 同步数据库操作在异步中运行
        loop = asyncio.get_event_loop()
        # 异步执行数据库插入
        await loop.run_in_executor(None, insert_article, article)
        # 文件保存保持同步
        save_article_to_file(article)

        print(f"爬取成功: {article['article_title']}")
    except Exception as e:
        print(f"爬取失败: {article['source_url']} 错误: {e}")

async def crawl_async(mode="full"):
    if not check_robots():
        return

    driver = get_driver()

    # 根据模式确定爬取日期范围
    if mode == "full":
        # 全量：最近7天
        dates = get_recent_dates(driver)
    else:
        # 增量：仅爬取当天
        today_str = datetime.now().strftime('%Y%m/%d')
        test_url = f"{BASE_URL}/{today_str}/#page=2"
        try:
            request_page(driver, test_url)
            dates = [today_str]
        except:
            dates = []
            print(f"当天 {today_str} 无日报")

    all_articles = []
    seen_article_ids = set()
    pre_total = 0

    for date in dates:
        for page in range(2, 9, 2):
            issue_url = f"{BASE_URL}/{date}/#page={page}"
            try:
                articles = parse_issue_page(driver, issue_url, date)
                new_articles = []
                for article in articles:
                    article_id = article["article_id"]
                    if article_id not in seen_article_ids:
                        seen_article_ids.add(article_id)
                        new_articles.append(article)

                if new_articles:
                    all_articles.extend(new_articles)
            except Exception as e:
                print(f"页面加载失败: {issue_url} 错误: {e}")

        print(f"日期 {date} 的报纸共找到 {len(all_articles) - pre_total} 篇文章")
        pre_total = len(all_articles)

    driver.quit()

    # 过滤已存在的文章
    new_articles = []
    for art in all_articles:
        if check_article_exists(art["article_id"]):
            print(f"跳过已存在文章: {art['article_title']}")
        else:
            new_articles.append(art)
    all_articles = new_articles

    print(f"开始异步下载详情页，总计 {len(all_articles)} 篇新文章")

    # 异步并发执行
    await asyncio.gather(*[parse_article_detail_async(art) for art in all_articles])

    # 统计和绘图
    if all_articles:
        category_counter = analyze_by_page_title(all_articles)
        plot_bar_chart(category_counter)
        plot_pie_chart(category_counter)
    else:
        print("无新文章，使用历史数据绘图")
        category_counter = load_category_counter()
        if category_counter:
            plot_bar_chart(category_counter)
            plot_pie_chart(category_counter)
        else:
            print("无历史数据，无需统计绘图")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="国家电网报爬虫")
    parser.add_argument(
        "--mode",
        choices=["full", "incremental"],
        default="full",
        help="爬取模式：full（全量，爬最近7天）| incremental（增量，仅爬当天新文章）"
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="启用定时任务（每天09:00自动运行增量爬取）"
    )
    args = parser.parse_args()

    # 定义定时任务函数（包装异步调用）
    def run_incremental():
        print("触发定时增量爬取...")
        asyncio.run(crawl_async(mode="incremental"))  # 确保异步函数正确执行


    if args.schedule:
        # 配置定时任务（每天14:00运行）
        schedule.every().day.at("14:00").do(run_incremental)
        print("定时任务已启动，每天14:00自动执行增量爬取...")
        # 启动定时循环
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        # 非定时模式：直接运行指定模式
        asyncio.run(crawl_async(mode=args.mode))