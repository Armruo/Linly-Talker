"""
测试新闻伴读功能
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from news_companion.webui_news import launch_news_companion

if __name__ == "__main__":
    # 启动新闻伴读界面
    launch_news_companion()
