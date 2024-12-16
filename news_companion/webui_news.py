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
        
    def process_news(self, url, language_name, auto_play=False):
        """处理新闻内容"""
        try:
            # Extract news content
            content = self.extractor.extract_content(url)
            if not content:
                return "无法提取新闻内容。请检查URL是否正确，或尝试其他新闻链接。", None, None
            
            self.current_text = content
            
            # Generate summary
            language_code = language_name.split()[0].lower()
            summary = self.summarizer.generate_summary(content, language_code)
            if not summary:
                return "生成摘要失败。请稍后重试。", None, None
            
            # Generate audio if auto_play is enabled
            audio_path = None
            if auto_play:
                audio_path = self.speaker.text_to_speech(summary, language_code)
            
            return summary, audio_path, content
            
        except Exception as e:
            logging.error(f"Error processing news: {str(e)}")
            return f"处理新闻时出错: {str(e)}", None, None
            
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
        
        /* Audio controls */
        .audio-controls {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 10px 0;
            padding: 10px;
            background: var(--bg-color);
            border-radius: 5px;
        }
        
        /* Text areas */
        .textbox {
            background: var(--bg-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            border-radius: 5px;
            padding: 10px;
        }
        
        /* Dropdown */
        .dropdown {
            background: var(--bg-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            border-radius: 5px;
            padding: 5px;
        }
    """) as demo:
        with gr.Column(elem_classes="container"):
            # Input Section
            with gr.Box(elem_classes="input-area"):
                url_input = gr.Textbox(
                    label="新闻链接",
                    placeholder="请输入新闻URL...",
                    show_label=True,
                    elem_classes="textbox"
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
