# 使用Python 3.9基础镜像（满足项目Python 3.9+要求）
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（Chrome浏览器及Selenium运行所需库）
RUN apt-get update && \
    apt-get install -y \
    chromium \
    chromium-driver \
    curl \
    && rm -rf /var/lib/apt/lists/*  # 清理缓存

# 安装Python依赖（从requirements.txt）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目所有文件到容器（包括源代码、配置等）
COPY . .

# 设置Chrome环境变量（匹配webdriver-manager自动检测）
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_DRIVER=/usr/bin/chromedriver

# 启动命令（支持通过参数指定爬取模式，默认全量）
CMD ["python", "src/crawler.py", "--mode", "full"]