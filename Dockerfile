# 使用非 slim 的 Python 3.9 镜像（包含更多基础库）
FROM python:3.9

# 设置时区（避免时间相关问题）
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

## 安装 Chrome 依赖（根据错误日志补充所有缺失的库）
#RUN apt-get update && apt-get install -y \
#    fonts-liberation \
#    libasound2 \
#    libatk-bridge2.0-0 \
#    libatk1.0-0 \
#    libatspi2.0-0 \
#    libc6 \
#    libcairo2 \
#    libcups2 \
#    libcurl4 \
#    libdbus-1-3 \
#    libexpat1 \
#    libgbm1 \
#    libglib2.0-0 \
#    libgtk-3-0 \
#    libnspr4 \
#    libnss3 \
#    libpango-1.0-0 \
#    libudev1 \
#    libvulkan1 \
#    libx11-6 \
#    libxcb1 \
#    libxcomposite1 \
#    libxdamage1 \
#    libxext6 \
#    libxfixes3 \
#    libxkbcommon0 \
#    libxrandr2 \
#    xdg-utils \
#    wget \
#    && rm -rf /var/lib/apt/lists/*
#
## 手动下载并安装 Chrome
#RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
#    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
#    && rm -f google-chrome-stable_current_amd64.deb \
#    && rm -rf /var/lib/apt/lists/*

# 工作目录
WORKDIR /app

# 复制依赖文件并安装（利用 Docker 分层缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码（仅 src 目录，避免冗余）
COPY src/ ./src/

# 环境变量（可通过 docker run -e 覆盖）
ENV MYSQL_HOST=mysql
ENV MYSQL_USER=root
ENV MYSQL_PASSWORD=123456
ENV MYSQL_DATABASE=sgcc_news

# 数据卷（持久化存储爬取的文章和图表）
VOLUME ["/app/articles", "/app/visualizations"]

# 启动命令（支持全量/增量模式，默认全量）
CMD ["python", "src/crawler.py", "--mode", "full"]