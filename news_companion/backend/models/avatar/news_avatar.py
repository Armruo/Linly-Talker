"""
新闻数字人模块
"""
import os
import random
from TFG import SadTalker
from TTS.PaddleTTS import PaddleTTS

class NewsAvatar:
    def __init__(self):
        """初始化数字人模块"""
        try:
            self.sadtalker = SadTalker(lazy_load=True)
            self.tts = PaddleTTS()
            self.default_image = os.path.join(os.path.dirname(__file__), "default_avatar.png")
        except Exception as e:
            print(f"Error initializing NewsAvatar: {str(e)}")
            self.sadtalker = None
            self.tts = None
    
    def generate_avatar_video(self, text, source_image=None, language='zh'):
        """生成数字人视频"""
        try:
            # 1. 生成语音
            audio_path = "temp_news_audio.wav"
            self.tts.predict(
                text,
                am="fastspeech2_mix",
                voc="hifigan_csmsc",
                lang=language,
                male=False,
                save_path=audio_path
            )
            
            # 2. 生成视频
            source_image = source_image or self.default_image
            video = self.sadtalker.test2(
                source_image,
                audio_path,
                preprocess_type='crop',
                is_still_mode=False,
                enhancer=False,
                batch_size=2,
                size_of_image=256,
                pose_style=random.randint(0, 45),
                facerender='facevid2vid',
                exp_weight=1,
                use_ref_video=False,
                ref_video=None,
                ref_info='pose',
                use_idle_mode=False,
                length_of_audio=5,
                blink_every=True,
                fps=20
            )
            
            # 3. 清理临时文件
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            return video
            
        except Exception as e:
            print(f"Error generating avatar video: {str(e)}")
            return None
