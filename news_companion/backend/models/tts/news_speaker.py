"""
新闻语音播报模块
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

from TTS.EdgeTTS import EdgeTTS
import logging

class NewsSpeaker:
    def __init__(self):
        try:
            self.tts = EdgeTTS()
            self.current_volume = 1.0  # Default volume (0.0 to 1.0)
            self.voice_configs = {
                'zh': {
                    'voice': 'zh-CN-XiaoxiaoNeural',
                    'rate': '+0%',
                    'volume': '+0%'
                },
                'en': {
                    'voice': 'en-US-JennyNeural',
                    'rate': '+0%',
                    'volume': '+0%'
                },
                'th': {
                    'voice': 'th-TH-PremwadeeNeural',
                    'rate': '+0%',
                    'volume': '+0%'
                },
                'vi': {
                    'voice': 'vi-VN-HoaiMyNeural',
                    'rate': '+0%',
                    'volume': '+0%'
                }
            }
        except Exception as e:
            logging.error(f"Error initializing TTS: {str(e)}")
            self.tts = None
            
    def speak_news(self, text, language):
        """将文本转换为语音"""
        if not self.tts:
            return None
            
        try:
            if language not in self.voice_configs:
                raise ValueError(f"Unsupported language for TTS: {language}")
                
            config = self.voice_configs[language]
            audio = self.tts.synthesize(
                text=text,
                voice=config['voice'],
                rate=config['rate'],
                volume=config['volume']
            )
            return audio
            
        except Exception as e:
            logging.error(f"TTS error: {str(e)}")
            return None

    def set_volume(self, volume):
        """设置音量 (0.0 到 1.0)"""
        self.current_volume = max(0.0, min(1.0, volume))
        # 更新所有语音配置的音量
        volume_percent = f"{int(self.current_volume * 100)}%"
        for config in self.voice_configs.values():
            config['volume'] = f"+{volume_percent}"
