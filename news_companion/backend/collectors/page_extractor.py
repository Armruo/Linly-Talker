"""
网页内容提取模块
"""
import requests
from bs4 import BeautifulSoup
import logging
import time
import random
import cloudscraper

class NewsExtractor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        
    def extract_content(self, url):
        """提取新闻页面内容"""
        try:
            logging.info(f"Attempting to fetch URL: {url}")
            
            # Add a small random delay
            time.sleep(random.uniform(1, 3))
            
            # First try with cloudscraper
            try:
                response = self.scraper.get(url)
                logging.info("Using cloudscraper for request")
            except:
                logging.info("Falling back to regular requests")
                session = requests.Session()
                response = session.get(url, headers=self.headers, timeout=15)
            
            logging.info(f"Response status code: {response.status_code}")
            response.raise_for_status()
            
            # 打印响应内容的前500个字符，用于调试
            logging.info(f"Response content preview: {response.text[:500]}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 记录找到的HTML结构
            logging.info(f"Found article tags: {len(soup.find_all('article'))}")
            logging.info(f"Found main tags: {len(soup.find_all('main'))}")
            logging.info(f"Found content divs: {len(soup.find_all('div', class_=['content', 'article-content', 'article-body', 'story-body', 'post-content']))}")
            
            # 移除不需要的元素
            for tag in soup(['script', 'style', 'iframe', 'nav', 'footer']):
                tag.decompose()
                
            # 提取主要内容
            # 首先尝试常见的新闻内容容器
            main_content = (
                soup.find('article') or 
                soup.find('main') or 
                soup.find('div', class_=['content', 'article-content', 'article-body', 'story-body', 'post-content']) or
                soup.find('div', {'id': ['content', 'article-content', 'main-content', 'story-content']})
            )
            
            # 如果没找到主要容器，尝试查找最长的文本段落
            if not main_content:
                paragraphs = soup.find_all('p')
                if paragraphs:
                    # 选择最长的连续段落作为主要内容
                    text_blocks = []
                    current_block = []
                    
                    for p in paragraphs:
                        text = p.get_text().strip()
                        if len(text) > 50:  # 忽略太短的段落
                            current_block.append(text)
                        elif current_block:
                            text_blocks.append('\n'.join(current_block))
                            current_block = []
                    
                    if current_block:
                        text_blocks.append('\n'.join(current_block))
                    
                    if text_blocks:
                        return self.preprocess_text(max(text_blocks, key=len))
            
            if main_content:
                return self.preprocess_text(main_content.get_text())
                
            return ""
            
        except Exception as e:
            logging.error(f"Error extracting content from {url}: {str(e)}")
            return ""
            
    def preprocess_text(self, content):
        """文本预处理"""
        # 移除多余空白
        content = ' '.join(content.split())
        # 移除特殊字符
        content = content.replace('\n', ' ').replace('\t', ' ')
        return content.strip()
