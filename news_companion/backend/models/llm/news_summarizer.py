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
            # 使用OpenAI格式的参数
            response = self.llm.client.chat.completions.create(
                model=self.llm.model_path,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2048,
                temperature=0.7,
                stop=["[END]", "\n\n\n"]
            )
            
            # 从响应中提取文本
            response_text = response.choices[0].message.content
            
            # 清理响应文本
            response_text = response_text.strip()
            
            # 确保响应包含所有必要的部分
            if not ("【核心要点】" in response_text and "【深度分析】" in response_text):
                response_text = self._format_incomplete_response(response_text)
            
            # 格式化为Markdown
            sections_content = self._parse_sections(response_text, language)
            formatted_text = self._format_sections_content(sections_content, language)
            
            return formatted_text
        except Exception as e:
            logging.error(f"Error generating summary: {str(e)}")
            return f"生成摘要时发生错误: {str(e)}"
            
    def _format_incomplete_response(self, response):
        """格式化不完整的响应"""
        if "【核心要点】" not in response:
            response = "【核心要点】\n" + response
        if "【深度分析】" not in response:
            response += "\n\n【深度分析】\n- 影响和意义：正在分析中..."
        return response

    def _create_prompt(self, text, language):
        """创建提示词"""
        lang_prompts = {
            'zh': """
                请对以下新闻内容进行详细分析和总结。要求分三个部分输出：
                {text}
                
                请按照以下格式和要求输出，并确保内容详实：
                
                【分段摘要】
                - 请按照原文的段落或章节顺序，分别总结每个主要部分的内容
                - 保持原文的逻辑结构
                - 每个部分的总结应该包含该部分的关键信息和重要细节
                
                【核心要点】
                - 列出5-7个核心要点
                - 每个要点都应该详细说明其重要性和影响
                - 确保要点涵盖新闻的各个重要方面
                
                【深度分析】
                - 提供全面的背景分析
                - 探讨新闻事件的潜在影响和意义
                - 分析可能的发展趋势和后果
                - 提供相关的建议或见解
            """,
            'en': """
                Please provide a detailed analysis and summary of the following news content in three parts:
                {text}
                
                Please output in the following format and request with comprehensive content:
                
                [Section Summaries]
                - Summarize each major section following the original text's structure
                - Maintain the logical flow of the original content
                - Include key information and important details for each section
                
                [Key Points]
                - List 5-7 key points
                - Explain the importance and impact of each point
                - Ensure coverage of all significant aspects of the news
                
                [In-depth Analysis]
                - Provide comprehensive background analysis
                - Discuss potential impacts and significance
                - Analyze possible trends and consequences
                - Offer relevant insights or recommendations
            """,
            'th': """
                กรุณาวิเคราะห์และสรุปเนื้อหาข่าวต่อไปนี้อย่างละเอียดเป็นสามส่วน:
                {text}
                
                กรุณาแสดงผลในรูปแบบต่อไปนี้ พร้อมเนื้อหาที่ครอบคลุม:
                
                [สรุปตามส่วน]
                - สรุปแต่ละส่วนสำคัญตามโครงสร้างของเนื้อหาต้นฉบับ
                - รักษาลำดับการนำเสนอตามต้นฉบับ
                - รวมข้อมูลสำคัญและรายละเอียดที่สำคัญของแต่ละส่วน
                
                [ประเด็นสำคัญ]
                - ระบุ 5-7 ประเด็นสำคัญ
                - อธิบายความสำคัญและผลกระทบของแต่ละประเด็น
                - ครอบคลุมทุกแง่มุมสำคัญของข่าว
                
                [การวิเคราะห์เชิงลึก]
                - ให้การวิเคราะห์พื้นฐานที่ครอบคลุม
                - อภิปรายผลกระทบและความสำคัญที่อาจเกิดขึ้น
                - วิเคราะห์แนวโน้มและผลที่ตามมา
                - เสนอข้อคิดเห็นหรือคำแนะนำที่เกี่ยวข้อง
            """,
            'vi': """
                Vui lòng phân tích và tóm tắt chi tiết nội dung tin tức sau đây thành ba phần:
                {text}
                
                Vui lòng xuất ra theo định dạng sau với nội dung toàn diện:
                
                [Tóm tắt theo phần]
                - Tóm tắt từng phần chính theo cấu trúc văn bản gốc
                - Duy trì luồng logic của nội dung gốc
                - Bao gồm thông tin chính và chi tiết quan trọng cho mỗi phần
                
                [Điểm chính]
                - Liệt kê 5-7 điểm chính
                - Giải thích tầm quan trọng và tác động của từng điểm
                - Đảm bảo bao quát tất cả khía cạnh quan trọng của tin tức
                
                [Phân tích chuyên sâu]
                - Cung cấp phân tích nền tảng toàn diện
                - Thảo luận về tác động và ý nghĩa tiềm năng
                - Phân tích xu hướng và hệ quả có thể xảy ra
                - Đưa ra những hiểu biết hoặc khuyến nghị liên quan
            """,
            'id': """
                Silakan berikan analisis dan ringkasan rinci dari konten berita berikut dalam tiga bagian:
                {text}
                
                Harap keluarkan dalam format berikut dengan konten yang komprehensif:
                
                [Ringkasan Bagian]
                - Ringkas setiap bagian utama mengikuti struktur teks asli
                - Pertahankan alur logis dari konten asli
                - Sertakan informasi kunci dan detail penting untuk setiap bagian
                
                [Poin Utama]
                - Daftar 5-7 poin utama
                - Jelaskan pentingnya dan dampak setiap poin
                - Pastikan mencakup semua aspek penting dari berita
                
                [Analisis Mendalam]
                - Berikan analisis latar belakang yang komprehensif
                - Bahas dampak dan signifikansi potensial
                - Analisis kemungkinan tren dan konsekuensi
                - Tawarkan wawasan atau rekomendasi yang relevan
            """,
            'ms': """
                Sila berikan analisis dan ringkasan terperinci tentang kandungan berita berikut dalam tiga bahagian:
                {text}
                
                Sila keluarkan dalam format berikut dengan kandungan yang komprehensif:
                
                [Ringkasan Bahagian]
                - Ringkaskan setiap bahagian utama mengikut struktur teks asal
                - Kekalkan aliran logik kandungan asal
                - Sertakan maklumat utama dan butiran penting untuk setiap bahagian
                
                [Perkara Utama]
                - Senaraikan 5-7 perkara utama
                - Terangkan kepentingan dan kesan setiap perkara
                - Pastikan liputan semua aspek penting berita
                
                [Analisis Mendalam]
                - Berikan analisis latar belakang yang komprehensif
                - Bincangkan kesan dan kepentingan yang berpotensi
                - Analisis kemungkinan trend dan akibat
                - Tawarkan pandangan atau cadangan yang berkaitan
            """
        }
        
        # Default to English if language not supported
        prompt_template = lang_prompts.get(language, lang_prompts['en'])
        return prompt_template.format(text=text)

    def _parse_sections(self, response_text, language):
        """解析响应文本为部分内容"""
        sections = self._get_section_headers(language)
        sections_content = {section: [] for section in sections}
        
        current_section = None
        content_started = False
        
        for line in response_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a section header
            is_header = False
            for section in sections:
                if section in line:
                    current_section = section
                    content_started = False
                    is_header = True
                    break
            
            # Skip header lines
            if is_header:
                continue
                
            # Add content lines to current section
            if current_section and (content_started or line):
                content_started = True
                sections_content[current_section].append(line)
        
        return sections_content

    def _get_section_headers(self, language):
        """获取部分标题"""
        if language == 'zh':
            return ['【分段摘要】', '【核心要点】', '【深度分析】']
        elif language == 'en':
            return ['[Section Summaries]', '[Key Points]', '[In-depth Analysis]']
        elif language == 'th':
            return ['[สรุปตามส่วน]', '[ประเด็นสำคัญ]', '[การวิเคราะห์เชิงลึก]']
        elif language == 'vi':
            return ['[Tóm tắt theo phần]', '[Điểm chính]', '[Phân tích chuyên sâu]']
        elif language == 'id':
            return ['[Ringkasan Bagian]', '[Poin Utama]', '[Analisis Mendalam]']
        elif language == 'ms':
            return ['[Ringkasan Bahagian]', '[Perkara Utama]', '[Analisis Mendalam]']
        else:
            return ['[Section Summaries]', '[Key Points]', '[In-depth Analysis]']

    def _format_sections_content(self, sections_content, language):
        """格式化部分内容为Markdown格式"""
        sections = self._get_section_headers(language)
        formatted_text = ""
        
        for section in sections:
            # Remove brackets/【】 from section title for cleaner headers
            clean_title = section.strip('[]【】')
            formatted_text += f"\n## {clean_title}\n\n"
            
            content = sections_content.get(section, [])
            if content:
                if section == sections[0]:  # Section Summaries
                    formatted_text += self._format_section_summaries(content)
                elif section == sections[1]:  # Key Points
                    formatted_text += self._format_key_points(content)
                else:  # In-depth Analysis
                    formatted_text += self._format_analysis(content)
            else:
                formatted_text += "_" + self._get_default_section_message(section, language) + "_\n"
        
        return formatted_text.strip()

    def _format_section_summaries(self, content):
        """格式化分段摘要为Markdown格式"""
        formatted = ""
        for line in content:
            line = line.strip()
            if not line:
                continue
            # Keep existing numbering if present
            if any(line.startswith(f"{i}. ") for i in range(1, 10)):
                formatted += f"{line}\n\n"
            else:
                formatted += f"> {line}\n\n"
        return formatted

    def _format_key_points(self, content):
        """格式化核心要点为Markdown格式"""
        formatted = ""
        point_number = 1
        
        for line in content:
            line = line.strip()
            if not line:
                continue
            # Remove existing markers and numbers
            line = line.lstrip('- •').strip()
            if any(line.startswith(f"{i}. ") for i in range(1, 10)):
                line = line.split('. ', 1)[1]
            formatted += f"{point_number}. {line}\n\n"
            point_number += 1
        return formatted

    def _format_analysis(self, content):
        """格式化深度分析为Markdown格式"""
        formatted = ""
        paragraph = []
        
        for line in content:
            line = line.strip()
            if not line:
                if paragraph:
                    formatted += ' '.join(paragraph) + "\n\n"
                    paragraph = []
                continue
                
            # Check for subheadings (lines with colons)
            if any(separator in line for separator in ['：', ':']):
                # First flush any existing paragraph
                if paragraph:
                    formatted += ' '.join(paragraph) + "\n\n"
                    paragraph = []
                
                title, content = line.replace('：', ':').split(':', 1)
                formatted += f"### {title.strip()}\n\n{content.strip()}\n\n"
            else:
                paragraph.append(line)
        
        # Flush any remaining paragraph
        if paragraph:
            formatted += ' '.join(paragraph) + "\n\n"
            
        return formatted

    def _get_default_section_message(self, section, language):
        """获取默认部分消息"""
        if language == 'zh':
            return {
                '【分段摘要】': '暂无分段摘要',
                '【核心要点】': '暂无核心要点',
                '【深度分析】': '暂无深度分析'
            }.get(section, '暂无内容')
        elif language == 'en':
            return {
                '[Section Summaries]': 'No section summaries available',
                '[Key Points]': 'No key points available',
                '[In-depth Analysis]': 'No in-depth analysis available'
            }.get(section, 'No content available')
        elif language == 'th':
            return {
                '[สรุปตามส่วน]': 'ไม่มีสรุปตามส่วน',
                '[ประเด็นสำคัญ]': 'ไม่มีประเด็นสำคัญ',
                '[การวิเคราะห์เชิงลึก]': 'ไม่มีการวิเคราะห์เชิงลึก'
            }.get(section, 'ไม่มีข้อมูล')
        elif language == 'vi':
            return {
                '[Tóm tắt theo phần]': 'Không có tóm tắt theo phần',
                '[Điểm chính]': 'Không có điểm chính',
                '[Phân tích chuyên sâu]': 'Không có phân tích chuyên sâu'
            }.get(section, 'Không có thông tin')
        elif language == 'id':
            return {
                '[Ringkasan Bagian]': 'Tidak ada ringkasan bagian',
                '[Poin Utama]': 'Tidak ada poin utama',
                '[Analisis Mendalam]': 'Tidak ada analisis mendalam'
            }.get(section, 'Tidak ada informasi')
        elif language == 'ms':
            return {
                '[Ringkasan Bahagian]': 'Tiada ringkasan bahagian',
                '[Perkara Utama]': 'Tiada perkara utama',
                '[Analisis Mendalam]': 'Tiada analisis mendalam'
            }.get(section, 'Tiada maklumat')
        else:
            return {
                '[Section Summaries]': 'No section summaries available',
                '[Key Points]': 'No key points available',
                '[In-depth Analysis]': 'No in-depth analysis available'
            }.get(section, 'No content available')
