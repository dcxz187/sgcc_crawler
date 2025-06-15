import requests
from urllib.robotparser import RobotFileParser
from config import BASE_URL

def check_robots():
    robots_url = f"{BASE_URL}/robots.txt"
    try:
        response = requests.get(robots_url, timeout=5)
        if response.status_code == 200:
            rp = RobotFileParser()
            rp.parse(response.text.splitlines())
            if rp.can_fetch("*", BASE_URL + "/"):
                print("robots.txt 禁止爬取稿件详情页，请立即停止！")
                return False
            print("robots.txt 允许爬取稿件详情页。")
            return True
        else:
            print("robots.txt 不存在，按默认允许处理。")
            return True
    except Exception as e:
        print(f"检查 robots.txt 失败，按默认允许处理。错误: {e}")
        return True
