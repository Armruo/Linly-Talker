"""
新闻伴读Web界面
"""
import gradio as gr
from backend.collectors.page_extractor import NewsExtractor
from backend.models.llm.news_summarizer import NewsSummarizer
from backend.models.translator.translator import MultilingualTranslator
from backend.models.tts.news_speaker import NewsSpeaker
import logging

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
        self.current_text = ""
        
    def process_news(self, input_text, language_name, auto_play=False):
        """处理新闻内容"""
        try:
            # Get language code from selection
            language_code = language_name.split()[0].lower()
            
            # Determine if input is URL or direct text
            input_text = input_text.strip()
            if input_text.startswith(('http://', 'https://')):
                # Handle URL input
                content = self.extractor.extract_content(input_text)
                if not content:
                    error_messages = {
                        'zh': "无法从URL提取内容。您可以直接粘贴新闻原文到输入框。",
                        'en': "Cannot extract content from URL. You can paste the news content directly.",
                        'th': "ไม่สามารถดึงเนื้อหาจาก URL ได้ คุณสามารถวางเนื้อหาข่าวโดยตรง",
                        'vi': "Không thể trích xuất nội dung từ URL. Bạn có thể dán trực tiếp nội dung tin tức.",
                        'id': "Tidak dapat mengekstrak konten dari URL. Anda dapat menempelkan konten berita secara langsung.",
                        'ms': "Tidak dapat mengekstrak kandungan dari URL. Anda boleh tampal kandungan berita secara langsung."
                    }
                    return error_messages.get(language_code, error_messages['en']), None, None
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
                    return error_messages.get(language_code, error_messages['en']), None, None
            
            self.current_text = content
            
            # First translate the content if not in target language
            # We'll assume the content is in Chinese by default
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
                return error_messages.get(language_code, error_messages['en']), None, None
            
            # Generate audio if auto_play is enabled
            audio_path = None
            if auto_play:
                audio_path = self.speaker.text_to_speech(summary, language_code)
            
            return summary, audio_path, content
            
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
            return error_messages.get(language_code, error_messages['en']), None, None
            
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
        /* Dark theme colors */
        :root {
            --primary-color: #4a6cf7;
            --bg-color: #1a1b1e;
            --text-color: #ffffff;
            --panel-bg: #2a2b2e;
            --border-color: #3a3b3e;
        }
        
        /* Global styles */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Input area */
        .input-area {
            background: var(--panel-bg);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 1px solid var(--border-color);
        }
        
        /* Output area */
        .output-area {
            background: var(--panel-bg);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 1px solid var(--border-color);
        }
        
        /* Buttons */
        .button-primary {
            background: var(--primary-color);
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .button-primary:hover {
            opacity: 0.9;
        }
        
        /* Text areas */
        .textbox {
            background: var(--bg-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            border-radius: 5px;
            padding: 10px;
            min-height: 100px;
        }
        
        /* Dropdown */
        .dropdown {
            background: var(--bg-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            border-radius: 5px;
            padding: 5px;
        }
        
        /* Placeholder text */
        .textbox::placeholder {
            color: #666;
            font-style: italic;
        }
    """) as demo:
        with gr.Column(elem_classes="container"):
            # Input Section
            with gr.Box(elem_classes="input-area"):
                url_input = gr.Textbox(
                    label="新闻链接或原文",
                    placeholder="请输入新闻URL或直接粘贴新闻内容...",
                    show_label=True,
                    elem_classes="textbox",
                    lines=5
                )
                
                with gr.Row():
                    with gr.Column(scale=2):
                        language = gr.Dropdown(
                            choices=[
                                "zh 中文",
                                "en English",
                                "th ไทย",
                                "vi Tiếng Việt",
                                "id Bahasa Indonesia",
                                "ms Bahasa Melayu"
                            ],
                            value="zh 中文",
                            label="输出语言",
                            elem_classes="dropdown"
                        )
                    with gr.Column(scale=1):
                        auto_play = gr.Checkbox(
                            label="自动播放",
                            value=False
                        )
                
                with gr.Row():
                    process_btn = gr.Button("分析新闻", elem_classes="button-primary")
                    stop_btn = gr.Button("停止播放")
            
            # Output Section
            with gr.Box(elem_classes="output-area"):
                with gr.Tabs():
                    with gr.TabItem("新闻摘要"):
                        summary_output = gr.Textbox(
                            label="新闻摘要",
                            show_label=True,
                            lines=10,
                            elem_classes="textbox"
                        )
                    
                    with gr.TabItem("语音播报"):
                        with gr.Box(elem_classes="audio-controls"):
                            audio_output = gr.Audio(
                                label="语音播报",
                                visible=True
                            )
                            volume_slider = gr.Slider(
                                minimum=0,
                                maximum=100,
                                value=70,
                                label="音量"
                            )
                    
                    with gr.TabItem("原文内容"):
                        original_text = gr.Textbox(
                            label="原文内容",
                            show_label=True,
                            lines=10,
                            elem_classes="textbox"
                        )
                        
                with gr.Box(elem_classes="recommendations"):
                    gr.Markdown("### 相关推荐")
                    related_articles = gr.HTML(
                        value="<div id='related-articles'></div>"
                    )
        
        # Event handlers
        process_btn.click(
            fn=ui.process_news,
            inputs=[url_input, language, auto_play],
            outputs=[summary_output, audio_output, original_text]
        )
        
        stop_btn.click(
            fn=ui.stop_audio
        )
        
        # Volume control
        volume_slider.change(
            fn=lambda v: ui.speaker.set_volume(v/100),
            inputs=[volume_slider]
        )
        
        # Auto-play audio when available
        audio_output.change(
            fn=ui.play_audio,
            inputs=[audio_output]
        )
    
    # Launch the interface
    demo.launch(share=True)

if __name__ == "__main__":
    launch_news_companion()
