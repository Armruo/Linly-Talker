"""
新闻摘要生成模块
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

from LLM.Llama3 import Llama3
import logging

class NewsSummarizer:
    def __init__(self):
        try:
            self.llm = Llama3()
        except Exception as e:
            logging.error(f"Error initializing Llama3: {str(e)}")
            self.llm = None
            
    def generate_summary(self, text, language='zh'):
        """生成新闻摘要"""
        if not self.llm:
            return "模型初始化失败"
            
        try:
            prompt = self._create_prompt(text, language)
            response = self.llm.generate(prompt)  # Use generate instead of chat
            if isinstance(response, tuple):
                response = response[0]  # Extract first element if it's a tuple
            return response
        except Exception as e:
            logging.error(f"Error generating summary: {str(e)}")
            return "生成摘要时发生错误"
            
    def _create_prompt(self, text, language):
        """创建提示词"""
        lang_prompts = {
            'zh': """
                请总结以下新闻内容的要点：
                {text}
                
                要求：
                1. 提取3-5个核心观点
                2. 每个观点不超过30字
                3. 使用中文输出
                """,
            'en': """
                Please summarize the key points of the following news:
                {text}
                
                Requirements:
                1. Extract 3-5 core points
                2. Each point should not exceed 30 words
                3. Output in English
                """
        }
        
        prompt = lang_prompts.get(language, lang_prompts['zh'])
        return prompt.format(text=text)
