import pymysql
from config import MYSQL_CONFIG

"""封装数据库连接"""
def get_connection():
    return pymysql.connect(**MYSQL_CONFIG)

"""插入文章数据"""
def insert_article(article):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = '''
                INSERT INTO articles (article_id, issue_date, page_number, page_title, article_title, author, content, source_url, crawl_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    issue_date=VALUES(issue_date),
                    page_number=VALUES(page_number),
                    page_title=VALUES(page_title),
                    article_title=VALUES(article_title),
                    author=VALUES(author),
                    content=VALUES(content),
                    source_url=VALUES(source_url),
                    crawl_time=VALUES(crawl_time)
            '''
            cursor.execute(sql, (
                article['article_id'],
                article['issue_date'],
                article['page_number'],
                article['page_title'],
                article['article_title'],
                article['author'],
                article['content'],
                article['source_url'],
                article['crawl_time']
            ))
        conn.commit()
    finally:
        conn.close()

"""检查文章是否已存在（基于article_id）"""
def check_article_exists(article_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 通过唯一键article_id查询是否存在记录
            cursor.execute("SELECT 1 FROM articles WHERE article_id = %s", (article_id,))
            return cursor.fetchone() is not None
    finally:
        conn.close()