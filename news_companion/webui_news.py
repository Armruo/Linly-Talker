"""
新闻伴读Web界面
"""
import gradio as gr
from backend.collectors.page_extractor import NewsExtractor
from backend.models.llm.news_summarizer import NewsSummarizer
from backend.models.translator.translator import MultilingualTranslator
from backend.models.tts.news_speaker import NewsSpeaker
from backend.models.db.news_database import NewsDatabase
from backend.models.analyzer.tag_extractor import TagExtractor
from backend.models.avatar.news_avatar import NewsAvatar
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class NewsCompanionUI:
    def __init__(self):
        self.extractor = NewsExtractor()
        self.summarizer = NewsSummarizer()
        self.translator = MultilingualTranslator()
        self.speaker = NewsSpeaker()
        self.tag_extractor = TagExtractor()
        self.db = NewsDatabase("news.db")
        self.avatar = NewsAvatar()
        self.current_text = ""
        self.current_tags = []
        
    def process_news(self, input_text, language_name, auto_play=False):
        """处理新闻内容"""
        try:
            # Get language code from selection
            language_code = language_name.split()[0].lower()
            
            # Determine if input is URL or direct text
            input_text = input_text.strip()
            title = ""
            if input_text.startswith(('http://', 'https://')):
                # Handle URL input
                content = self.extractor.extract_content(input_text)
                title = self.extractor.extract_title(input_text)
                if not content:
                    error_messages = {
                        'zh': "无法从URL提取内容。您可以直接粘贴新闻原文到输入框。",
                        'en': "Cannot extract content from URL. You can paste the news content directly.",
                        'th': "ไม่สามารถดึงเนื้อหาจาก URL ได้ คุณสามารถวางเนื้อหาข่าวโดยตรง",
                        'vi': "Không thể trích xuất nội dung từ URL. Bạn có thể dán trực tiếp nội dung tin tức.",
                        'id': "Tidak dapat mengekstrak konten dari URL. Anda dapat menempelkan konten berita secara langsung.",
                        'ms': "Tidak dapat mengekstrak kandungan dari URL. Anda boleh tampal kandungan berita secara langsung."
                    }
                    return error_messages.get(language_code, error_messages['en']), None, None, []
            else:
                # Use input text directly as content
                content = input_text
                if len(content.strip()) < 50:  # Basic validation
                    error_messages = {
                        'zh': "请输入更多内容（至少50个字符）或有效的新闻URL。",
                        'en': "Please enter more content (at least 50 characters) or a valid news URL.",
                        'th': "โปรดป้อนเนื้อหาเพิ่มเติม (อย่างน้อย 50 ตัวอักษร) หรือ URL ข่าวที่ถูกต้อง",
                        'vi': "Vui lòng nhập thêm nội dung (ít nhất 50 ký tự) hoặc URL tin tức hợp lệ.",
                        'id': "Harap masukkan lebih banyak konten (minimal 50 karakter) atau URL berita yang valid.",
                        'ms': "Sila masukkan lebih banyak kandungan (minimum 50 aksara) atau URL berita yang sah."
                    }
                    return error_messages.get(language_code, error_messages['en']), None, None, []
            
            self.current_text = content
            
            # Extract tags
            self.current_tags = self.tag_extractor.extract_tags(content, title)
            
            # First translate the content if not in target language
            if language_code != 'zh':
                content = self.translator.translate(content, target_lang=language_code, source_lang='zh')
            
            # Generate summary in target language
            summary = self.summarizer.generate_summary(content, language_code)
            if not summary:
                error_messages = {
                    'zh': "生成摘要失败。请稍后重试。",
                    'en': "Failed to generate summary. Please try again later.",
                    'th': "การสร้างสรุปล้มเหลว โปรดลองอีกครั้งในภายหลัง",
                    'vi': "Không thể tạo tóm tắt. Vui lòng thử lại sau.",
                    'id': "Gagal menghasilkan ringkasan. Silakan coba lagi nanti.",
                    'ms': "Gagal menjana ringkasan. Sila cuba lagi kemudian."
                }
                return error_messages.get(language_code, error_messages['en']), None, None, []
            
            # Store in database
            if title or input_text.startswith(('http://', 'https://')):
                self.db.add_news(
                    url=input_text if input_text.startswith(('http://', 'https://')) else "",
                    title=title or "直接输入的新闻",
                    content=self.current_text,
                    summary=summary,
                    tags=self.current_tags
                )
            
            # Get recommendations
            recommendations = self.get_recommendations(5)
            
            # Generate audio if needed
            audio_path = None
            if auto_play:
                audio_path = self.speaker.generate_audio(summary, language_code)
            
            return summary, audio_path, content, recommendations
            
        except Exception as e:
            logging.error(f"Error processing news: {str(e)}")
            error_messages = {
                'zh': f"处理新闻时出错: {str(e)}",
                'en': f"Error processing news: {str(e)}",
                'th': f"เกิดข้อผิดพลาดในการประมวลผลข่าว: {str(e)}",
                'vi': f"Lỗi khi xử lý tin tức: {str(e)}",
                'id': f"Kesalahan saat memproses berita: {str(e)}",
                'ms': f"Ralat semasa memproses berita: {str(e)}"
            }
            return error_messages.get(language_code, error_messages['en']), None, None, []
            
    def get_recommendations(self, limit: int = 5) -> List[Dict]:
        """获取推荐新闻"""
        if not self.current_tags:
            return []
        return self.db.get_similar_news(self.current_tags, limit)
        
    def play_audio(self, audio_path):
        """播放音频"""
        if audio_path:
            self.speaker.play_audio(audio_path)
            
    def stop_audio(self):
        """停止音频播放"""
        self.speaker.stop_audio()

def launch_news_companion():
    """启动新闻伴读UI"""
    ui = NewsCompanionUI()
    
    with gr.Blocks(css="""
        /* 样式定义... */
    """) as demo:
        gr.Markdown("""
        # 新闻伴读助手
        智能新闻摘要与数字人讲解系统
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                input_text = gr.Textbox(
                    label="输入新闻URL或内容",
                    placeholder="请输入新闻URL或直接粘贴新闻内容...",
                    lines=5
                )
                
                with gr.Row():
                    language = gr.Dropdown(
                        choices=["zh 中文", "en English", "th ไทย", "vi Tiếng Việt", "id Indonesia", "ms Melayu"],
                        value="zh 中文",
                        label="输出语言"
                    )
                    avatar_image = gr.Image(
                        label="选择数字人形象（可选）",
                        type="filepath"
                    )
                
                with gr.Row():
                    submit_btn = gr.Button("生成摘要", variant="primary")
                    clear_btn = gr.Button("清除")
                    
            with gr.Column(scale=3):
                with gr.Tabs() as tabs:
                    with gr.TabItem("摘要"):
                        summary_output = gr.Textbox(
                            label="新闻摘要",
                            lines=10,
                            interactive=False
                        )
                    
                    with gr.TabItem("原文"):
                        original_text = gr.Textbox(
                            label="原文内容",
                            lines=15,
                            interactive=False
                        )
                    
                    with gr.TabItem("数字人"):
                        avatar_video = gr.Video(
                            label="数字人讲解",
                            interactive=False
                        )
                        
                    with gr.TabItem("相关推荐"):
                        recommendations = gr.JSON(
                            label="相关新闻",
                            interactive=False
                        )
        
        def process_with_avatar(input_text, language_name, avatar_img):
            # 处理新闻并生成摘要
            summary, _, content, recs = ui.process_news(input_text, language_name, False)
            
            # 生成数字人视频
            if summary and summary != "生成摘要时发生错误":
                video = ui.avatar.generate_avatar_video(summary, avatar_img, language_name.split()[0])
            else:
                video = None
            
            return summary, content, video, recs
        
        submit_btn.click(
            fn=process_with_avatar,
            inputs=[input_text, language, avatar_image],
            outputs=[summary_output, original_text, avatar_video, recommendations]
        )
        
        clear_btn.click(
            fn=lambda: ("", "", None, None),
            inputs=[],
            outputs=[summary_output, original_text, avatar_video, recommendations]
        )
    
    demo.launch(share=True)

if __name__ == "__main__":
    launch_news_companion()
