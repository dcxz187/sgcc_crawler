import matplotlib.pyplot as plt
from collections import Counter
import os
import json

# 设置中文字体和解决负号显示问题
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def save_category_counter(counter, filename="category_counter.json"):
    """
    将分类统计数据保存到 JSON 文件
    """
    output_dir = "visualizations"
    os.makedirs(output_dir, exist_ok=True)
    full_path = os.path.join(output_dir, filename)
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(dict(counter), f, ensure_ascii=False, indent=4)

def load_category_counter(filename="category_counter.json"):
    """
    从 JSON 文件中加载分类统计数据
    """
    output_dir = "visualizations"
    full_path = os.path.join(output_dir, filename)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            return Counter(json.load(f))
    return Counter()

def analyze_by_page_title(articles):
    """
    按 page_title 分类统计文章数量
    """
    titles = [article['page_title'] for article in articles if article.get('page_title')]
    new_counter = Counter(titles)
    # 加载历史数据
    old_counter = load_category_counter()
    # 合并新旧数据
    combined_counter = old_counter + new_counter
    # 保存合并后的数据
    save_category_counter(combined_counter)
    return combined_counter


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
    print(f"栏目分布图已保存为 {os.path.abspath(full_path)}")


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
    print(f"栏目占比饼图已保存为 {os.path.abspath(full_path)}")
