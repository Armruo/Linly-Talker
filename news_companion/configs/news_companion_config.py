"""
新闻伴读配置文件
"""

NEWS_COMPANION_CONFIG = {
    'supported_languages': {
        'zh': {
            'name': '中文',
            'tts_voice': 'zh-CN-XiaoxiaoNeural',
            'code': 'zh'
        },
        'en': {
            'name': 'English',
            'tts_voice': 'en-US-JennyNeural',
            'code': 'en'
        },
        'th': {
            'name': 'ภาษาไทย',
            'tts_voice': 'th-TH-PremwadeeNeural',
            'code': 'th'
        },
        'vi': {
            'name': 'Tiếng Việt',
            'tts_voice': 'vi-VN-HoaiMyNeural',
            'code': 'vi'
        }
    },
    
    'llm_config': {
        'model': 'llama3-70b',
        'temperature': 0.7,
        'max_tokens': 500
    },
    
    'ui_config': {
        'theme_color': '#2196F3',
        'floating_ball_position': 'right',
        'floating_ball_size': '48px'
    },
    
    'cache_config': {
        'enable_cache': True,
        'cache_expiration': 3600,  # 1小时
        'max_cache_size': 1000     # 最多缓存1000条
    }
}
