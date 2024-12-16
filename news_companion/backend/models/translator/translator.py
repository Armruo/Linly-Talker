"""
多语言翻译模块
"""
from transformers import MarianMTModel, MarianTokenizer
import logging
from langdetect import detect

class MultilingualTranslator:
    def __init__(self):
        self.supported_languages = {
            'zh': 'Chinese',
            'en': 'English',
            'th': 'Thai',
            'vi': 'Vietnamese',
            'id': 'Indonesian',
            'ms': 'Malay'
        }
        
        # 定义语言对和对应的模型
        self.model_pairs = {
            ('zh', 'en'): 'Helsinki-NLP/opus-mt-zh-en',
            ('en', 'zh'): 'Helsinki-NLP/opus-mt-en-zh',
            ('en', 'th'): 'Helsinki-NLP/opus-mt-en-mul',
            ('en', 'vi'): 'Helsinki-NLP/opus-mt-en-mul',
            ('en', 'id'): 'Helsinki-NLP/opus-mt-en-mul',
            ('en', 'ms'): 'Helsinki-NLP/opus-mt-en-mul'
        }
        
        self.current_pair = None
        self.model = None
        self.tokenizer = None
        
    def _detect_language(self, text):
        """检测文本语言"""
        try:
            return detect(text)
        except:
            return 'en'  # 默认假设为英语
            
    def _load_model(self, source_lang, target_lang):
        """加载适当的翻译模型"""
        # 如果已经加载了正确的模型，直接返回
        if self.current_pair == (source_lang, target_lang) and self.model is not None:
            return True
            
        # 查找合适的模型
        model_name = self.model_pairs.get((source_lang, target_lang))
        if not model_name:
            # 如果找不到直接的翻译模型，尝试通过英语作为中间语言
            if source_lang != 'en' and target_lang != 'en':
                logging.info(f"No direct translation model for {source_lang}->{target_lang}, using English as pivot")
                return False  # 将在translate方法中处理两步翻译
                
            logging.error(f"Unsupported language pair: {source_lang}->{target_lang}")
            return False
            
        try:
            logging.info(f"Loading translation model: {model_name}")
            self.tokenizer = MarianTokenizer.from_pretrained(model_name)
            self.model = MarianMTModel.from_pretrained(model_name)
            self.current_pair = (source_lang, target_lang)
            return True
        except Exception as e:
            logging.error(f"Failed to load translation model: {str(e)}")
            return False
            
    def _translate_with_model(self, text):
        """使用当前加载的模型进行翻译"""
        try:
            inputs = self.tokenizer(text, return_tensors="pt", padding=True)
            translated = self.model.generate(**inputs)
            return self.tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
        except Exception as e:
            logging.error(f"Translation error: {str(e)}")
            return text
            
    def translate(self, text, target_lang, source_lang=None):
        """翻译文本"""
        if not text.strip():
            return text
            
        # 如果没有指定源语言，自动检测
        if source_lang is None:
            source_lang = self._detect_language(text)
            logging.info(f"Detected source language: {source_lang}")
            
        # 如果源语言和目标语言相同，直接返回
        if source_lang == target_lang:
            return text
            
        # 检查语言支持
        if target_lang not in self.supported_languages:
            logging.error(f"Unsupported target language: {target_lang}")
            return text
            
        try:
            # 尝试直接翻译
            if self._load_model(source_lang, target_lang):
                return self._translate_with_model(text)
                
            # 如果没有直接的翻译模型，通过英语中转
            if source_lang != 'en':
                # 先翻译成英语
                if self._load_model(source_lang, 'en'):
                    text = self._translate_with_model(text)
                    source_lang = 'en'
                
            if target_lang != 'en':
                # 再从英语翻译到目标语言
                if self._load_model('en', target_lang):
                    return self._translate_with_model(text)
                    
            return text
            
        except Exception as e:
            logging.error(f"Translation error: {str(e)}")
            return text
