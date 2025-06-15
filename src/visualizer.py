import matplotlib.pyplot as plt
from collections import Counter
import os


# 设置中文字体和解决负号显示问题
plt.rcParams['font.sans-serif'] = ['PingFang SC']
plt.rcParams['axes.unicode_minus'] = False


def analyze_by_page_title(articles):
    """
    按 page_title 分类统计文章数量
    """
    titles = [article['page_title'] for article in articles if article.get('page_title')]
    counter = Counter(titles)
    return counter


def plot_bar_chart(data, title="最近7天栏目分布", filename="category_distribution.png"):
    """
    绘制柱状图
    """
    output_dir = "visualizations"
    os.makedirs(output_dir, exist_ok=True)  # 创建目录（如果不存在）

    plt.figure(figsize=(10, 6))
    plt.bar(data.keys(), data.values())
    plt.xticks(rotation=45, ha='right')
    plt.title(title)
    plt.xlabel("栏目")
    plt.ylabel("文章数量")
    plt.tight_layout()

    full_path = os.path.join(output_dir, filename)
    plt.savefig(full_path)
    print(f"📊 栏目分布图已保存为 {os.path.abspath(full_path)}")


def plot_pie_chart(data, title="最近7天栏目占比", filename="category_pie.png"):
    """
    绘制饼图
    """
    output_dir = "visualizations"
    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(8, 8))
    plt.pie(data.values(), labels=data.keys(), autopct='%1.1f%%', startangle=140)
    plt.title(title)
    plt.axis('equal')  # 确保饼图为正圆
    plt.tight_layout()

    full_path = os.path.join(output_dir, filename)
    plt.savefig(full_path)
    print(f"🥧 栏目占比饼图已保存为 {os.path.abspath(full_path)}")
