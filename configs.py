# 设备运行端口 (Device running port)
port = 6006
# api运行端口及IP (API running port and IP)
mode = 'api' # api 需要先运行Linly-api-fast.py，暂时仅仅适用于Linly
ip = '0.0.0.0'  # 允许所有IP访问
api_port = 7871

# API密钥配置
llama3_apikey = None  # 在这里填入你的Llama3 API密钥
openai_apikey = None  # OpenAI API密钥
gemini_apikey = None  # Gemini API密钥

# 代理设置
proxy_url = "http://127.0.0.1:7890"  # 如果需要代理，请设置代理地址

# L模型路径 (Linly model path) 已不用了
mode = 'offline'
model_path = 'Qwen/Qwen-1_8B-Chat'

# ssl证书 (SSL certificate) 麦克风对话需要此参数
# 最好调整为绝对路径
ssl_certfile = "./https_cert/cert.pem"
ssl_keyfile = "./https_cert/key.pem"

llama3_apikey = "LA-bcde398ac3ef443c961f2f0af94be707d8506d0995fa47d09d3fa907fd53298c"