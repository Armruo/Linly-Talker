"""
新闻伴读Web界面
"""
import gradio as gr
from backend.collectors.page_extractor import NewsExtractor
from backend.models.llm.news_summarizer import NewsSummarizer
from backend.models.translator.translator import MultilingualTranslator
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
        
    def process_news(self, url, language_name):
        """处理新闻内容"""
        try:
            # Extract news content
            content = self.extractor.extract_content(url)
            if not content:
                return "无法提取新闻内容。请检查URL是否正确，或尝试其他新闻链接。", None
            
            # Generate summary
            summary = self.summarizer.generate_summary(content)
            if not summary:
                return "生成摘要失败。请稍后重试。", None
                
            # Translate if needed
            language_code = language_name.split()[0].lower()
            if language_code != 'zh':
                summary = self.translator.translate(summary, language_code)
            
            return summary, None
            
        except Exception as e:
            logging.error(f"Error processing news: {str(e)}")
            return f"处理新闻时出错: {str(e)}", None

def launch_news_companion():
    """启动新闻伴读UI"""
    ui = NewsCompanionUI()
    
    # Create the interface
    demo = gr.Interface(
        fn=ui.process_news,
        inputs=[
            gr.Textbox(label="新闻链接", placeholder="请输入新闻URL..."),
            gr.Dropdown(
                choices=["zh 中文", "en English"],
                value="zh 中文",
                label="输出语言"
            )
        ],
        outputs=[
            gr.Textbox(label="新闻摘要"),
            gr.Audio(label="语音播报", visible=False)  # Hidden since we're not using TTS
        ],
        title="新闻伴读助手",
        description="输入新闻链接，获取AI生成的新闻摘要"
    )
    
    # Launch the interface
    demo.launch(share=True)

if __name__ == "__main__":
    launch_news_companion()
