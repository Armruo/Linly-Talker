# News Companion（新闻伴读）

这是Linly-Talker项目的新闻伴读扩展模块，提供新闻摘要、多语言翻译和语音播报功能。

## 功能特点

- 网页新闻内容提取
- AI驱动的新闻摘要生成
- 多语言翻译支持（中文、英语、泰语、越南语等）
- 自然语音播报
- 浮动球式用户界面

## 安装依赖

```bash
cd news_companion
pip install -r requirements.txt
```

## 使用方法

1. 启动新闻伴读界面：
```python
from news_companion.webui_news import launch_news_companion
launch_news_companion()
```

2. 在浏览器中打开显示的URL
3. 输入新闻网页地址
4. 选择目标语言
5. 点击"生成摘要"按钮

## 配置说明

配置文件位于 `configs/news_companion_config.py`，可以根据需要修改：
- 支持的语言
- LLM模型参数
- UI主题设置
- 缓存配置

## 注意事项

- 确保已正确配置Linly-Talker的API密钥
- 网页内容提取可能受目标网站限制
- 建议使用支持的语言列表中的语言

## 开发说明

本模块设计为Linly-Talker的独立扩展，不会影响原有功能。如需扩展：

1. 添加新的语言支持：
   - 在`configs/news_companion_config.py`中添加语言配置
   - 在`models/tts/news_speaker.py`中添加对应的语音配置

2. 自定义UI：
   - 修改`frontend/components/floating_ball.py`
   - 调整CSS样式

3. 添加新功能：
   - 在`backend/models`下添加新的功能模块
   - 在`webui_news.py`中集成新功能
