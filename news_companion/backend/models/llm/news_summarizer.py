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
            response = self.llm.generate(prompt)
            if isinstance(response, tuple):
                response = response[0]
            return response
        except Exception as e:
            logging.error(f"Error generating summary: {str(e)}")
            return f"生成摘要时发生错误: {str(e)}"
            
    def _create_prompt(self, text, language):
        """创建提示词"""
        lang_prompts = {
            'zh': """
                请分析以下新闻内容，并提供详细总结：
                {text}
                
                请按以下格式输出：
                
                【核心要点】
                1. 
                2. 
                3. 
                4.
                5.
                
                【深度分析】
                - 影响和意义：
                - 发展趋势：
                - 相关建议：
            """,
            'en': """
                Please analyze the following news content and provide a detailed summary:
                {text}
                
                Please output in the following format:
                
                [Key Points]
                1. 
                2. 
                3. 
                4.
                5.
                
                [In-depth Analysis]
                - Impact and Significance:
                - Development Trends:
                - Related Suggestions:
            """,
            'th': """
                กรุณาวิเคราะห์เนื้อหาข่าวต่อไปนี้และให้สรุปโดยละเอียด:
                {text}
                
                กรุณาแสดงผลในรูปแบบต่อไปนี้:
                
                [ประเด็นสำคัญ]
                1. 
                2. 
                3. 
                4.
                5.
                
                [การวิเคราะห์เชิงลึก]
                - ผลกระทบและความสำคัญ:
                - แนวโน้มการพัฒนา:
                - ข้อเสนอแนะที่เกี่ยวข้อง:
            """,
            'vi': """
                Vui lòng phân tích nội dung tin tức sau và cung cấp bản tóm tắt chi tiết:
                {text}
                
                Vui lòng xuất ra theo định dạng sau:
                
                [Điểm chính]
                1. 
                2. 
                3. 
                4.
                5.
                
                [Phân tích chuyên sâu]
                - Tác động và ý nghĩa:
                - Xu hướng phát triển:
                - Đề xuất liên quan:
            """,
            'id': """
                Silakan analisis konten berita berikut dan berikan ringkasan terperinci:
                {text}
                
                Harap keluarkan dalam format berikut:
                
                [Poin Utama]
                1. 
                2. 
                3. 
                4.
                5.
                
                [Analisis Mendalam]
                - Dampak dan Signifikansi:
                - Tren Perkembangan:
                - Saran Terkait:
            """,
            'ms': """
                Sila analisis kandungan berita berikut dan berikan ringkasan terperinci:
                {text}
                
                Sila output dalam format berikut:
                
                [Poin Utama]
                1. 
                2. 
                3. 
                4.
                5.
                
                [Analisis Mendalam]
                - Kesan dan Kepentingan:
                - Trend Pembangunan:
                - Cadangan Berkaitan:
            """
        }
        
        # Default to English if language not supported
        prompt_template = lang_prompts.get(language, lang_prompts['en'])
        return prompt_template.format(text=text)
