## 国家电网报爬虫



### 题目分析

国家电网报只有工作日才发布，即周一到周五，我在6月15日（周日）这天，浏览器输入https://epaper.sgcctop.com 会直接跳转到 https://epaper.sgcctop.com/202506/13/#page=1 ，并且加载2-3秒后出画面，此时为第一页，是封面，获取不到需要的信息，从第二页到第九页，每两页构成一个浏览器页面，展示多篇文稿，一篇文稿的html源代码为

```html
<polygon class="area" points="8.872099740000001,430.2972012 833.97807528,430.2972012 833.97807528,1769.9853830499999 8.872099740000001,1769.9853830499999" title="绿能澎湃沃巴蜀" data-pageid="1" data-contentid="746458"></polygon>
```

title值即为要读取的article_title字段，data-pageid即为要读取的page_number字段，data-contentid即为要读取的article_id字段，点击一篇文稿，会跳转到文稿的详情页 https://epaper.sgcctop.com/202506/13/con-746458.html ，主要由data-contentid的值决定，这个URL就是source_url需要的内容，进入文稿详情页后，会有一些<div class="xxx"></div>的盒子，比如class="top_bar"的盒子里面的内容就是page_title字段，author就是要读取的author字段，content就是要读取的content字段。



### 项目介绍

本项目为国家电网报（ https://epaper.sgcctop.com ） 电子报的爬虫工具，支持全量爬取最近7天的稿件或增量爬取当天稿件，数据存储到 MySQL 数据库和本地文件系统，并生成栏目分布统计图，GitHub仓库为https://github.com/dcxz187/sgcc_crawler.git。

#### 功能

- 全量爬取：抓取最近7天的所有稿件。
- 增量爬取：仅抓取当天的缺失稿件。
- 异步爬取，通过同时发多个请求、等待响应时切换任务、异步处理数据库操作。
- 数据存储：每篇稿件正文保存为 .txt 文件，每篇稿件元数据保存为 .json 文件，所有数据存储到 MySQL 数据库。
- 爬取礼貌：遵守 robots.txt，请求间隔 ≥ 0.5 秒，最大并发 ≤ 5。
- 可视化：生成最近7天栏目分布图 。


#### 依赖

Python 3.9+
requirements.txt

```
pymysql~=1.1.1
aiohttp~=3.10.11
selenium~=4.24.0
webdriver-manager~=4.0.2
beautifulsoup4~=4.11.1
matplotlib~=3.7.1
requests~=2.32.3
```



### 文件结构
```
sgcc_crawler/
├── src/
│   ├── config.py             # 配置文件
│   ├── crawler.py           # 主爬虫逻辑
│   ├── db.py                   # 数据库操作
│   ├── robots_check.py            # robots检测
│   ├── utils.py                # 工具函数
│   ├── visualizer.py        # 数据可视化
├── requirements.txt          # 依赖列表
├── Dockerfile               # Docker 配置文件
├── articles/                  # 输出文章（自动生成）
│   ├── *.txt                # 文章正文
｜   ├── *.json               # 文章元数据
├── visualization/        # 输出图表（自动生成）
│   ├── category_distribution.png     # 条状图
│   └── category_pie.png                   # 饼图
└── README.md                # 项目说明
```



### 安装与运行

本地运行
- 安装 MySQL 并创建数据库、表：

```SQL
CREATE DATABASE sgcc_news;
CREATE TABLE IF NOT EXISTS articles (
    article_id VARCHAR(255) PRIMARY KEY,
    issue_date DATE,
    page_number VARCHAR(10),
    page_title TEXT,
    article_title TEXT,
    author TEXT,
    content TEXT,
    source_url TEXT,
    crawl_time DATETIME
);
```

- 安装 Python 依赖：pip install -r requirements.txt

- 修改 src/config.py 中的 MySQL 配置：
```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'yourusername',
    'password': 'yourpassword',
    'database': 'sgcc_news',
    'charset': 'utf8mb4'
}
```


- 运行爬虫：
全量爬取：```python src/crawler.py --mode full```
增量爬取：```python src/crawler.py --mode incremental```
