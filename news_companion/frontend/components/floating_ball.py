"""
浮动球UI组件
"""
import gradio as gr
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from configs.news_companion_config import NEWS_COMPANION_CONFIG

def create_floating_ball():
    """创建浮动球界面"""
    languages = NEWS_COMPANION_CONFIG['supported_languages']
    
    with gr.Box(elem_classes="floating-ball"):
        with gr.Column():
            # URL输入
            url_input = gr.Textbox(
                label="新闻URL",
                placeholder="请输入新闻网页地址..."
            )
            
            # 语言选择
            lang_dropdown = gr.Dropdown(
                choices=[lang['name'] for lang in languages.values()],
                value=languages['zh']['name'],
                label="选择语言"
            )
            
            # 摘要按钮
            summary_btn = gr.Button("生成摘要", variant="primary")
            
            # 摘要显示
            summary_output = gr.Textbox(
                label="新闻摘要",
                interactive=False
            )
            
            # 语音播报
            audio_output = gr.Audio(
                label="语音播报",
                type="numpy"
            )
            
    return url_input, lang_dropdown, summary_btn, summary_output, audio_output

def get_language_code(language_name):
    """根据语言名称获取语言代码"""
    for code, lang in NEWS_COMPANION_CONFIG['supported_languages'].items():
        if lang['name'] == language_name:
            return code
    return 'zh'  # 默认返回中文

def add_floating_ball_css():
    """添加浮动球样式"""
    return """
        .floating-ball {
            position: fixed;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            background: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
            width: 300px;
        }
    """
