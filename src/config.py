# SQL连接配置
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'sgcc_news',
    'charset': 'utf8mb4'
}

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

REQUEST_DELAY = 0.5  # 连续请求间隔
MAX_WORKERS = 5  # 协程/线程总数
BASE_URL = 'https://epaper.sgcctop.com'
