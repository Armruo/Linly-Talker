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
            
            # Enhanced headers
            enhanced_headers = self.headers.copy()
            enhanced_headers.update({
                'Origin': url.split('/')[0] + '//' + url.split('/')[2],
                'Referer': url,
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"'
            })
            
            # First try with cloudscraper
            try:
                response = self.scraper.get(url, headers=enhanced_headers)
                logging.info("Using cloudscraper for request")
            except Exception as e:
                logging.info(f"Cloudscraper failed: {str(e)}")
                logging.info("Falling back to regular requests")
                session = requests.Session()
                response = session.get(url, headers=enhanced_headers, timeout=15)
            
            logging.info(f"Response status code: {response.status_code}")
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除不需要的元素
            for tag in soup(['script', 'style', 'iframe', 'nav', 'footer', 'header', 'aside', 'form', 'button', 'meta', 'link', 'noscript']):
                tag.decompose()

            # 1. 查找所有可能的内容容器
            content_candidates = []
            
            # 常见的文章容器类名和ID
            article_classes = ['article-content', 'post-content', 'entry-content', 'content-article', 
                             'article-body', 'story-body', 'main-content', 'article__content',
                             'post-body', 'story-content', 'article-text', 'content-body']
            
            article_ids = ['article-content', 'post-content', 'main-content', 'content', 
                          'article-body', 'story-body', 'entry-content']

            # 查找具有这些类名的元素
            for class_name in article_classes:
                elements = soup.find_all(class_=class_name)
                for element in elements:
                    content_candidates.append(element.get_text())

            # 查找具有这些ID的元素
            for id_name in article_ids:
                element = soup.find(id=id_name)
                if element:
                    content_candidates.append(element.get_text())

            # 查找article和main标签
            for tag in ['article', 'main']:
                elements = soup.find_all(tag)
                for element in elements:
                    content_candidates.append(element.get_text())

            # 2. 收集所有有意义的段落
            paragraphs = []
            for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                text = p.get_text().strip()
                if text and len(text) > 20:  # 只保留有意义的段落
                    paragraphs.append(text)

            if paragraphs:
                content_candidates.append('\n'.join(paragraphs))

            # 3. 查找较长的文本块
            for div in soup.find_all(['div', 'section']):
                text = div.get_text().strip()
                if len(text) > 500:  # 较长的文本块可能是文章内容
                    content_candidates.append(text)

            # 处理所有候选内容
            if content_candidates:
                # 预处理并去重
                processed_candidates = []
                seen_contents = set()
                
                for content in content_candidates:
                    processed = self.preprocess_text(content)
                    if processed and processed not in seen_contents:
                        seen_contents.add(processed)
                        processed_candidates.append(processed)

                # 选择最合适的内容（最长的那个）
                if processed_candidates:
                    return max(processed_candidates, key=len)

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
