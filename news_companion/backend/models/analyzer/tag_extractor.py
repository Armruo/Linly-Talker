"""
新闻标签提取模块
"""
from typing import List
import jieba.analyse
import re

class TagExtractor:
    def __init__(self):
        """初始化标签提取器"""
        # 设置jieba关键词提取的停用词
        jieba.analyse.set_stop_words("stopwords.txt")
        
    def extract_tags(self, text: str, title: str = "", top_k: int = 5) -> List[str]:
        """
        从文本中提取关键标签
        
        Args:
            text: 新闻正文
            title: 新闻标题
            top_k: 提取的标签数量
            
        Returns:
            List[str]: 标签列表
        """
        # 合并标题和正文，但给标题更高的权重
        combined_text = f"{title} {title} {text}"
        
        # 使用TF-IDF算法提取关键词
        tags = jieba.analyse.extract_tags(
            combined_text,
            topK=top_k,
            withWeight=False,
            allowPOS=('ns', 'n', 'vn', 'v')  # 允许的词性：地名、名词、动名词、动词
        )
        
        # 清理标签
        cleaned_tags = []
        for tag in tags:
            # 移除标点符号和特殊字符
            tag = re.sub(r'[^\w\s]', '', tag).strip()
            # 过滤掉太短的标签
            if len(tag) >= 2:
                cleaned_tags.append(tag)
        
        return cleaned_tags
        
    def extract_entities(self, text: str) -> List[str]:
        """
        提取命名实体（人名、地名、机构名等）
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 实体列表
        """
        # 使用jieba的命名实体识别
        words = jieba.posseg.cut(text)
        entities = []
        
        for word, flag in words:
            if flag.startswith(('nr', 'ns', 'nt', 'nz')):
                entities.append(word)
        
        return list(set(entities))  # 去重
