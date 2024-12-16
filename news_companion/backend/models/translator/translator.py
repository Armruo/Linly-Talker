"""
多语言翻译模块
"""
from transformers import MarianMTModel, MarianTokenizer
import logging

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
        self.model_name = 'Helsinki-NLP/opus-mt-en-zh'  # Default English to Chinese
        self.model = None
        self.tokenizer = None
        
    def _load_model(self, source_lang, target_lang):
        """Load the appropriate model based on language pair"""
        model_name = f'Helsinki-NLP/opus-mt-{source_lang}-{target_lang}'
        try:
            self.tokenizer = MarianTokenizer.from_pretrained(model_name)
            self.model = MarianMTModel.from_pretrained(model_name)
        except Exception as e:
            logging.error(f"Failed to load translation model: {str(e)}")
            return False
        return True
        
    def translate(self, text, target_lang, source_lang='en'):
        """翻译文本"""
        try:
            if target_lang not in self.supported_languages:
                logging.error(f"Unsupported target language: {target_lang}")
                return text
                
            if not self._load_model(source_lang, target_lang):
                return text
                
            # Translate
            inputs = self.tokenizer(text, return_tensors="pt", padding=True)
            translated = self.model.generate(**inputs)
            result = self.tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
            return result
            
        except Exception as e:
            logging.error(f"Translation error: {str(e)}")
            return text
            
    def is_language_supported(self, lang_code):
        """检查语言是否支持"""
        return lang_code in self.supported_languages
